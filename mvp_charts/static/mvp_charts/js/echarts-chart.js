/*
 * Line charts: turning a region's data into a drawn ECharts chart.
 *
 * A region's own module (chart-region.js) decides whether the charting
 * library arrived, whether the wrapper resolved to a usable height, and what
 * size that wrapper is now. This module owns none of that: it waits for a
 * region to report `ready` on `mvp-chart-region:state`, initialises ECharts
 * on the drawing surface with the options its companion script carries, and
 * resizes on the region's own `mvp-chart-region:resize`. No library poll, no
 * height check and no resize observer of its own (D2).
 *
 * No dependencies, and safe to evaluate twice.
 */
(function () {
  "use strict";

  if (window.mvpEchartsChart) {
    return;
  }

  var OPTIONS_SELECTOR = "[data-mvp-echarts-options-for]";
  var INIT_FLAG = "mvpEchartsChartInit";

  function findRegion(script) {
    var id = script.getAttribute("data-mvp-echarts-options-for");
    return id ? document.getElementById(id) : null;
  }

  function drawingSurface(region) {
    return region && region.querySelector("[data-mvp-chart-region-surface]");
  }

  function initChart(script) {
    if (script.dataset[INIT_FLAG]) {
      return;
    }
    script.dataset[INIT_FLAG] = "1";

    var region = findRegion(script);
    var surface = drawingSurface(region);
    if (!region || !surface) {
      return;
    }

    var options = JSON.parse(script.textContent);
    var chart = null;

    function draw() {
      chart = window.echarts.init(surface);
      chart.setOption(options);
    }

    region.addEventListener("mvp-chart-region:state", function (event) {
      if (event.detail.state === "ready") {
        draw();
      }
    });
    region.addEventListener("mvp-chart-region:resize", function () {
      if (chart) {
        chart.resize();
      }
    });

    /*
     * A region already ready by the time this script runs has already
     * dispatched its `ready` event, which the listener above was attached
     * too late to catch — so the state is read directly as a fallback.
     */
    if (region.dataset.mvpChartRegionState === "ready") {
      draw();
    }
  }

  /*
   * One chart failing leaves the others working, for the same reason
   * chart-region.js isolates each region.
   */
  function initAll(root) {
    var scripts = (root || document).querySelectorAll(OPTIONS_SELECTOR);
    Array.prototype.forEach.call(scripts, function (script) {
      try {
        initChart(script);
      } catch (error) {
        if (window.console && window.console.error) {
          window.console.error("echarts chart failed to start", script.id, error);
        }
      }
    });
  }

  window.mvpEchartsChart = { version: 1, init: initAll };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      initAll();
    });
  } else {
    initAll();
  }
})();
