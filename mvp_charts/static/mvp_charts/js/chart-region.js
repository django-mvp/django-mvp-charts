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

  function initRegion(region) {
    if (region.dataset[STATE]) {
      return;
    }
    setState(region, "waiting");
    whenLibraryArrives(function () {
      setState(region, "ready");
    });
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
