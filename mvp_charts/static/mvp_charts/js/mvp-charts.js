/*
 * Draw every chart on the page, and keep each one at the size of its box.
 *
 * The server has already built the options — this reads them and hands them
 * to ECharts. Anything that goes wrong goes to the console: a message drawn
 * into the page would be this package deciding what a project shows its
 * readers when something is broken, and that is the project's decision.
 *
 * No dependencies, and safe to evaluate twice.
 */
(function () {
  "use strict";

  function draw(figure) {
    if (figure.dataset.mvpChartDrawn) {
      return;
    }
    figure.dataset.mvpChartDrawn = "1";

    var surface = figure.querySelector("[data-mvp-chart-surface]");
    var options = figure.querySelector("[data-mvp-chart-options]");
    var chart = window.echarts.init(surface);
    chart.setOption(JSON.parse(options.textContent));

    if (window.ResizeObserver) {
      new window.ResizeObserver(function () {
        chart.resize();
      }).observe(figure);
    }
  }

  function drawAll(root) {
    var figures = (root || document).querySelectorAll("[data-mvp-chart]");
    if (!figures.length) {
      return;
    }
    if (!window.echarts) {
      window.console.error(
        "mvp-charts: window.echarts is not loaded. Load ECharts before this " +
          "file, or expose it as window.echarts from your bundle."
      );
      return;
    }
    // One chart failing leaves the others on the page working.
    Array.prototype.forEach.call(figures, function (figure) {
      try {
        draw(figure);
      } catch (error) {
        window.console.error("mvp-charts: " + figure.id + " did not draw", error);
      }
    });
  }

  window.mvpCharts = { draw: drawAll };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () {
      drawAll();
    });
  } else {
    drawAll();
  }
})();
