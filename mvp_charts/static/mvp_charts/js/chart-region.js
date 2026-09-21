/*
 * Chart regions: the things about a region that only exist in a browser.
 *
 * The server renders a region's markup, its accessible name, its text
 * alternative and the wording of every message it can show. It cannot know
 * whether the charting library arrived, whether the wrapper resolved to a
 * usable height, or what size that wrapper is now. Those are this file's only
 * jobs.
 *
 * No dependencies, and safe to evaluate twice.
 */
(function () {
  "use strict";

  if (window.mvpChartRegion) {
    return;
  }

  var REGION_SELECTOR = "[data-mvp-chart-region]";
  var STATE = "mvpChartRegionState";

  /* How often to look for a library that has not arrived yet. */
  var LIBRARY_POLL_MS = 100;

  /*
   * How long after the page has finished loading to keep waiting.
   *
   * Long enough that a bundle fetched over a slow connection is not accused
   * of not existing, short enough that someone staring at an empty box is
   * told why within a few seconds. Only reached when the page has already
   * fired `load`, so it is a grace window on top of that rather than a
   * timeout from first paint.
   */
  var LIBRARY_GRACE_MS = 3000;

  /*
   * A region reads one thing, and it is the same sentence for both ways the
   * library can arrive: a public copy the project put in its own base
   * template, or the project's own bundle. Neither route is named anywhere,
   * which is what makes "no declaration either way" true rather than a claim.
   */
  function libraryIsPresent() {
    return Boolean(window.echarts);
  }

  function setState(region, state) {
    region.dataset[STATE] = state;
    region.dispatchEvent(
      new CustomEvent("mvp-chart-region:state", {
        bubbles: true,
        detail: { state: state },
      })
    );
  }

  /*
   * Wait rather than judge.
   *
   * A bundle can load after the markup does, which is ordinary in a project
   * doing nothing unusual. A region that decided at its first instant would
   * accuse a correctly configured project of a fault it does not have, and
   * that message is worse than no message: it sends someone to fix something
   * that is not broken. So a region that finds nothing keeps looking.
   */
  function whenLibraryArrives(onArrival) {
    if (libraryIsPresent()) {
      onArrival();
      return function () {};
    }
    var polling = window.setInterval(function () {
      if (libraryIsPresent()) {
        window.clearInterval(polling);
        onArrival();
      }
    }, LIBRARY_POLL_MS);
    return function () {
      window.clearInterval(polling);
    };
  }

  /*
   * Put a message where the chart would have been.
   *
   * In the page, not in the console: the person who can act on this is
   * usually looking at the page, and a console message is invisible to
   * everyone who does not already suspect something is wrong. Identical in
   * development and in production for the same reason — a blank rectangle in
   * production is exactly as undiagnosable as one in development.
   *
   * The wording comes from the server, so it is translated and asserted
   * without a browser. This function decides only when to show it.
   */
  function report(region, kind) {
    var surface = region.querySelector("[data-mvp-chart-region-surface]");
    if (!surface) {
      return;
    }
    var message = region.getAttribute("data-mvp-chart-region-" + kind);
    surface.textContent = "";
    var note = document.createElement("p");
    note.className = "text-error p-4 text-sm";
    note.setAttribute("role", "status");
    note.textContent = message || "";
    surface.appendChild(note);
    setState(region, kind);
  }

  /*
   * A region with no height cannot show a message about having no height, so
   * it is given just enough room to be read. This is the one place the
   * package sets a height, and it applies only where the alternative is an
   * invisible failure.
   */
  function makeMessageReadable(region) {
    region.style.minHeight = "4rem";
  }

  function hasUsableHeight(region) {
    return region.getBoundingClientRect().height >= 1;
  }

  /*
   * Judge the height at first visibility, not at first paint.
   *
   * A region inside a collapsed panel or an unselected tab has no height for
   * reasons that are not a mistake, and measuring at load would report every
   * one of them. Once a region has been seen with a usable height it is never
   * judged again: losing height later is a panel closing, which is the page
   * working as designed.
   */
  function watchHeight(region) {
    var settled = false;
    var judge = function () {
      if (settled) {
        return true;
      }
      if (!isVisible(region)) {
        return false;
      }
      settled = true;
      if (!hasUsableHeight(region)) {
        makeMessageReadable(region);
        report(region, "no-height");
      }
      return true;
    };
    if (judge()) {
      return;
    }
    if (!window.IntersectionObserver) {
      return;
    }
    var observer = new window.IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i += 1) {
        if (entries[i].isIntersecting && judge()) {
          observer.disconnect();
          return;
        }
      }
    });
    observer.observe(region);
  }

  function isVisible(region) {
    var box = region.getBoundingClientRect();
    return box.width > 0 || box.height > 0;
  }

  /*
   * Tell whoever is drawing what size they have now.
   *
   * A chart type has to redraw when its box changes, and no chart type
   * exists yet — so this is the contract being designed before there is a
   * consumer for it, which is the only order that leaves the consumer
   * nothing to work around. The event carries the measured box, because the
   * alternative is every listener measuring the same element again.
   *
   * No coalescing layer here, deliberately. A drag-resize writes a stream of
   * sizes, and the obvious defence is to batch them through
   * requestAnimationFrame — but ResizeObserver already delivers at most one
   * callback per frame, carrying the size the element ended up at rather
   * than each size it passed through. The batching was written, and then
   * removed once the test for it passed with it gone: a layer whose removal
   * changes nothing observable is a layer to take out.
   */
  function watchSize(region) {
    if (!window.ResizeObserver) {
      return;
    }
    var observer = new window.ResizeObserver(function () {
      var box = region.getBoundingClientRect();
      region.dispatchEvent(
        new CustomEvent("mvp-chart-region:resize", {
          bubbles: true,
          detail: { width: box.width, height: box.height },
        })
      );
    });
    observer.observe(region);
  }

  function initRegion(region) {
    if (region.dataset[STATE]) {
      return;
    }
    setState(region, "waiting");
    watchHeight(region);
    watchSize(region);

    var stopWaiting = whenLibraryArrives(function () {
      if (region.dataset[STATE] !== "no-height") {
        setState(region, "ready");
      }
    });

    /*
     * Give up only once waiting has stopped being a reasonable explanation:
     * after the page has finished loading, and then after a grace window on
     * top of that. Before both, a missing library is a bundle still on its
     * way.
     */
    afterLoad(function () {
      window.setTimeout(function () {
        /*
         * Stop looking first, whatever the verdict turns out to be. A region
         * that has already reported having no height will never draw however
         * the library question resolves, and leaving the poll running for it
         * means a page in that state keeps waking the browser every tenth of
         * a second for as long as it is open.
         */
        stopWaiting();
        if (libraryIsPresent() || region.dataset[STATE] === "no-height") {
          return;
        }
        report(region, "missing-library");
      }, LIBRARY_GRACE_MS);
    });
  }

  function afterLoad(run) {
    if (document.readyState === "complete") {
      run();
      return;
    }
    window.addEventListener("load", run, { once: true });
  }

  /*
   * One region failing leaves the others working. Each is set up inside its
   * own try/catch so a fault in one — for any reason, including one nobody
   * has thought of — cannot take the page's other charts down with it.
   */
  function initAll(root) {
    var regions = (root || document).querySelectorAll(REGION_SELECTOR);
    Array.prototype.forEach.call(regions, function (region) {
      try {
        initRegion(region);
      } catch (error) {
        if (window.console && window.console.error) {
          window.console.error("chart region failed to start", region.id, error);
        }
      }
    });
  }

  window.mvpChartRegion = { version: 1, init: initAll };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAll();
    });
  } else {
    initAll();
  }
})();
