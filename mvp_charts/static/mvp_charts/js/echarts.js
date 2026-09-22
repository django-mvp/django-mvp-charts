/*
 * Drawing into a chart region with ECharts.
 *
 * The server decided everything it can: which chart type, which values, which
 * axes, and which renderer. This file does the two things only a running page
 * can.
 *
 *   1. Hand the options to ECharts once the region says it is ready.
 *   2. Redraw at the new size on every resize the region reports.
 *
 * Colour is not here either. Series take ECharts' own palette unless the chart
 * named one, and this package makes no attempt to follow the daisyUI theme: a
 * project that wants its charts to match its site sets `color` on a series or
 * `options.color` on the chart.
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
    this.instance = window.echarts.init(this.surface, null, {
      renderer: this.payload.renderer,
    });
    var options = this.payload.options;
    /*
     * Two things the server cannot know, filled in here rather than guessed
     * there: the page's own typeface, because a canvas inherits nothing from
     * the document, and whether this reader has asked for less motion.
     */
    options.textStyle = options.textStyle || {};
    if (!options.textStyle.fontFamily) {
      options.textStyle.fontFamily = getComputedStyle(document.body).fontFamily;
    }
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches
    ) {
      options.animation = false;
    }
    this.instance.setOption(options);
  };

  Drawing.prototype.resize = function () {
    if (this.instance) {
      this.instance.resize();
    }
  };

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
      var drawing = new Drawing(region, payload);
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
   * One chart failing to start leaves the others drawn.
   */
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

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAll();
    });
  } else {
    initAll();
  }
})();
