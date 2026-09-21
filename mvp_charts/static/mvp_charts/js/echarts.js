/*
 * Drawing into a chart region with ECharts.
 *
 * The server decided everything it can: which chart type, which values, which
 * axes, what the empty message says, and — as sentinel strings rather than
 * colours — which role in the theme each mark takes. This file does the three
 * things only a running page can.
 *
 *   1. Resolve `mvp:` sentinels against the theme the browser is actually
 *      showing. A daisyUI theme is a block of CSS custom properties chosen in
 *      the browser and changeable without a page load, so the server cannot
 *      know a single colour on the page.
 *   2. Hand the options to ECharts once the region says it is ready, and hand
 *      them over again on every resize the region reports.
 *   3. Redraw when the theme changes under it.
 *
 * No dependencies beyond `window.echarts` and the region module's events, and
 * safe to evaluate twice.
 */
(function () {
  "use strict";

  if (window.mvpEcharts) {
    return;
  }

  var CHART_SELECTOR = "[data-mvp-echarts-options]";
  var SENTINEL = "mvp:";

  /*
   * The categorical order, as offsets from the theme's own primary hue.
   *
   * Not the theme's semantic roles. Those were the obvious choice and they do
   * not survive a check: daisyUI reserves four of its eight for status, which
   * leaves primary, secondary, accent and neutral — and neutral sits within a
   * few points of the body-text colour on most themes, so it reads as ink
   * rather than as a series. Of the three that remain, `corporate` puts its
   * primary and secondary a perceptual distance of 11 apart, which is below
   * the floor at which full-colour vision can tell two marks apart at all.
   *
   * So the hues are stepped from the theme's primary instead, and the theme
   * still decides everything that carries its character: the hue the sequence
   * starts at, how saturated the marks are, and how light they sit against its
   * own surface. The offsets and the lightness modulation below were searched
   * against a colour-vision-deficiency check over every theme the demo offers,
   * rather than chosen by eye.
   */
  var HUE_OFFSETS = [0, 160, 60, 240, 110, 300];
  var LIGHTNESS_STEPS = [0, 0.06, -0.06, 0.06, -0.06, 0];

  var clamp = function (value, low, high) {
    return Math.max(low, Math.min(high, value));
  };

  /* -- colour ------------------------------------------------------------- */

  function oklchToRgb(L, C, H) {
    var a = C * Math.cos((H * Math.PI) / 180);
    var b = C * Math.sin((H * Math.PI) / 180);
    var l = Math.pow(L + 0.3963377774 * a + 0.2158037573 * b, 3);
    var m = Math.pow(L - 0.1055613458 * a - 0.0638541728 * b, 3);
    var s = Math.pow(L - 0.0894841775 * a - 1.291485548 * b, 3);
    var encode = function (channel) {
      var c = clamp(channel, 0, 1);
      c = c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
      return Math.round(clamp(c, 0, 1) * 255);
    };
    return [
      encode(4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s),
      encode(-1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s),
      encode(-0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s),
    ];
  }

  function rgbToOklch(r, g, b) {
    var lin = function (channel) {
      var c = channel / 255;
      return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    };
    var R = lin(r),
      G = lin(g),
      B = lin(b);
    var l = Math.cbrt(0.4122214708 * R + 0.5363325363 * G + 0.0514459929 * B);
    var m = Math.cbrt(0.2119034982 * R + 0.6806995451 * G + 0.1073969566 * B);
    var s = Math.cbrt(0.0883024619 * R + 0.2817188376 * G + 0.6299787005 * B);
    var L = 0.2104542553 * l + 0.793617785 * m - 0.0040720468 * s;
    var A = 1.9779984951 * l - 2.428592205 * m + 0.4505937099 * s;
    var Bb = 0.0259040371 * l + 0.7827717662 * m - 0.808675766 * s;
    var H = (Math.atan2(Bb, A) * 180) / Math.PI;
    return [L, Math.sqrt(A * A + Bb * Bb), H < 0 ? H + 360 : H];
  }

  /*
   * A theme's own text for one of its colours, as [L, C, H].
   *
   * A custom property holds whatever the theme author wrote, unresolved — the
   * browser does not compute it into a colour until something paints with it.
   * daisyUI writes `oklch()`, but a hand-written theme may well write a hex,
   * so both are read rather than assuming one.
   */
  function readColor(root, name) {
    var text = getComputedStyle(root).getPropertyValue("--color-" + name).trim();
    if (!text) {
      return null;
    }
    var oklch = /^oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)/i.exec(text);
    if (oklch) {
      var L = parseFloat(oklch[1]) / (oklch[2] === "%" ? 100 : 1);
      return [L, parseFloat(oklch[3]), parseFloat(oklch[4])];
    }
    var hex = /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.exec(text);
    if (hex) {
      var digits = hex[1];
      if (digits.length === 3) {
        digits = digits.replace(/(.)/g, "$1$1");
      }
      return rgbToOklch(
        parseInt(digits.slice(0, 2), 16),
        parseInt(digits.slice(2, 4), 16),
        parseInt(digits.slice(4, 6), 16)
      );
    }
    var rgb = /rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)/i.exec(text);
    if (rgb) {
      return rgbToOklch(+rgb[1], +rgb[2], +rgb[3]);
    }
    return null;
  }

  /*
   * Everything the sentinels resolve against, read once per draw.
   *
   * Once rather than per lookup because a chart asks for the same half-dozen
   * colours many times over, and `getComputedStyle` is a layout read.
   */
  function Theme(root) {
    this.root = root;
    this.cache = {};
    var surface = readColor(root, "base-100");
    this.dark = surface ? surface[0] < 0.5 : false;
    this.palette = this.derivePalette(readColor(root, "primary"));
  }

  Theme.prototype.derivePalette = function (primary) {
    var base = primary || [0.55, 0.16, 250];
    var light = clamp(base[0], this.dark ? 0.62 : 0.48, this.dark ? 0.8 : 0.66);
    var chroma = clamp(base[1], 0.12, 0.19);
    var slots = [];
    for (var i = 0; i < HUE_OFFSETS.length; i += 1) {
      slots.push(
        oklchToRgb(
          clamp(light + LIGHTNESS_STEPS[i], 0.44, 0.76),
          chroma,
          (base[2] + HUE_OFFSETS[i]) % 360
        )
      );
    }
    return slots;
  };

  /*
   * One sentinel, resolved.
   *
   * `mvp:slot-2` is the second categorical slot. `mvp:error` is that role in
   * the theme, for a series whose colour carries meaning rather than identity.
   * `mvp:base-content/70` is the same colour at 70% — how axis labels and
   * gridlines stay one step off the surface instead of competing with the data.
   */
  Theme.prototype.resolve = function (sentinel) {
    if (this.cache[sentinel] !== undefined) {
      return this.cache[sentinel];
    }
    var body = sentinel.slice(SENTINEL.length);
    var parts = body.split("/");
    var alpha = parts.length > 1 ? clamp(parseFloat(parts[1]) / 100, 0, 1) : 1;
    var slot = /^slot-(\d+)$/.exec(parts[0]);
    var rgb = slot
      ? this.palette[
          clamp(parseInt(slot[1], 10), 1, this.palette.length) - 1
        ]
      : null;
    if (!rgb) {
      var lch = readColor(this.root, parts[0]);
      rgb = lch ? oklchToRgb(lch[0], lch[1], lch[2]) : [127, 127, 127];
    }
    var value =
      alpha === 1
        ? "rgb(" + rgb.join(",") + ")"
        : "rgba(" + rgb.join(",") + "," + alpha + ")";
    this.cache[sentinel] = value;
    return value;
  };

  /*
   * Walk the options and swap every sentinel for a colour.
   *
   * A walk rather than a fixed list of known keys: an author reaching for a raw
   * ECharts option can write `mvp:accent` anywhere in it and have it follow the
   * theme like everything the component wrote. A list of keys would work for
   * the component's own output and quietly fail for theirs.
   */
  function resolveColors(value, theme) {
    if (typeof value === "string") {
      return value.indexOf(SENTINEL) === 0 ? theme.resolve(value) : value;
    }
    if (Array.isArray(value)) {
      return value.map(function (item) {
        return resolveColors(item, theme);
      });
    }
    if (value && typeof value === "object") {
      var out = {};
      for (var key in value) {
        if (Object.prototype.hasOwnProperty.call(value, key)) {
          out[key] = resolveColors(value[key], theme);
        }
      }
      return out;
    }
    return value;
  }

  /* -- drawing ------------------------------------------------------------ */

  function readPayload(region) {
    var script = document.getElementById(
      region.getAttribute("data-mvp-echarts-options")
    );
    if (!script) {
      return null;
    }
    try {
      return JSON.parse(script.textContent);
    } catch (error) {
      return null;
    }
  }

  /*
   * Say there is nothing to draw, where the chart would have been.
   *
   * A chart with no data draws an empty rectangle, which is the exact failure
   * this package exists not to produce: indistinguishable from a broken chart,
   * a missing library, or a wrapper with no height. The wording comes from the
   * server so it is translated with everything else.
   */
  function reportEmpty(region, message) {
    var surface = region.querySelector("[data-mvp-chart-region-surface]");
    if (!surface) {
      return;
    }
    surface.textContent = "";
    var note = document.createElement("p");
    note.className = "text-base-content/60 grid h-full place-items-center p-4 text-sm";
    note.setAttribute("role", "status");
    note.textContent = message || "";
    surface.appendChild(note);
  }

  function Drawing(region, payload) {
    this.region = region;
    this.payload = payload;
    this.surface = region.querySelector("[data-mvp-chart-region-surface]");
    this.instance = null;
  }

  Drawing.prototype.draw = function () {
    if (!this.surface || !window.echarts) {
      return;
    }
    if (!this.instance) {
      this.instance = window.echarts.init(this.surface, null, {
        renderer: this.payload.renderer === "svg" ? "svg" : "canvas",
      });
    }
    var theme = new Theme(document.documentElement);
    var options = resolveColors(this.payload.options, theme);
    /*
     * Two things the server cannot know, filled in here rather than guessed
     * there: the page's own typeface, because a canvas inherits nothing, and
     * whether this reader has asked for less motion.
     */
    options.textStyle = options.textStyle || {};
    options.textStyle.fontFamily = getComputedStyle(document.body).fontFamily;
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      options.animation = false;
    }
    this.instance.setOption(options, { notMerge: true });
  };

  Drawing.prototype.resize = function () {
    if (this.instance) {
      this.instance.resize();
    }
  };

  /* -- wiring ------------------------------------------------------------- */

  var drawings = [];

  function start(region) {
    if (region.dataset.mvpEchartsStarted) {
      return;
    }
    region.dataset.mvpEchartsStarted = "1";

    var payload = readPayload(region);
    if (!payload) {
      return;
    }

    /*
     * The region owns the two questions that come before drawing — has the
     * library arrived, and is there a box to draw into — and answers them by
     * moving to `ready`. A region that never gets there has already put its own
     * message in the page, so there is nothing to add here.
     */
    var begin = function () {
      if (!payload.options) {
        reportEmpty(region, payload.empty);
        return;
      }
      var drawing = new Drawing(region, payload);
      drawings.push(drawing);
      drawing.draw();
      region.addEventListener("mvp-chart-region:resize", function () {
        drawing.resize();
      });
    };

    if (region.dataset.mvpChartRegionState === "ready") {
      begin();
      return;
    }
    region.addEventListener("mvp-chart-region:state", function (event) {
      if (event.detail && event.detail.state === "ready") {
        begin();
      }
    });
  }

  /*
   * A theme change repaints every chart on the page.
   *
   * The switcher writes one attribute on the document element and the browser
   * recalculates every `var()` on the page — except the ones inside a canvas,
   * which is not CSS and holds whatever it was last given. Watching the
   * attribute is what keeps a chart part of the page rather than a picture
   * stuck in the theme it was born in.
   */
  function watchTheme() {
    if (!window.MutationObserver) {
      return;
    }
    new window.MutationObserver(function () {
      drawings.forEach(function (drawing) {
        try {
          drawing.draw();
        } catch (error) {
          /* One chart failing to repaint leaves the others repainted. */
        }
      });
    }).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
  }

  function initAll(root) {
    var regions = (root || document).querySelectorAll(CHART_SELECTOR);
    Array.prototype.forEach.call(regions, function (region) {
      try {
        start(region);
      } catch (error) {
        if (window.console && window.console.error) {
          window.console.error("chart failed to start", region.id, error);
        }
      }
    });
  }

  window.mvpEcharts = { version: 1, init: initAll };

  watchTheme();

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAll();
    });
  } else {
    initAll();
  }
})();
