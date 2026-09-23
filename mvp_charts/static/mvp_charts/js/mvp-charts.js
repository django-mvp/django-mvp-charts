/*
 * Draw every chart on the page, and keep each one at the size of its box.
 *
 * The server has already built the options — this reads them and hands them
 * to ECharts. Anything that goes wrong goes to the console: a message drawn
 * into the page would be this package deciding what a project shows its
 * readers when something is broken, and that is the project's decision.
 *
 * The one thing removed from the page here is a placeholder the page itself
 * asked for, once the chart it was standing in for has been drawn.
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

    // After the chart is on the surface, never before: a figure that goes
    // empty and stays empty is worse than one that never stopped waiting.
    var placeholder = figure.querySelector("[data-mvp-chart-placeholder]");
    if (placeholder) {
      placeholder.remove();
    }

    if (window.ResizeObserver) {
      new window.ResizeObserver(function () {
        chart.resize();
        reportIfFlat(figure);
      }).observe(figure);
    }
  }

  /*
   * A figure with width but no height, said once.
   *
   * This is the one way a chart fails that leaves no trace anywhere: the
   * options are correct, ECharts initialised, nothing threw, and the reader
   * sees blank page. It is almost always a percentage height inside an
   * ancestor sized by its own content.
   *
   * Width-but-no-height is the whole test, and it is what makes the check
   * safe to run on every resize. A chart inside a `display: none` panel or an
   * unselected tab measures 0x0 — both zero — which is not a mistake and not
   * reported. It is also self-correcting: the panel opening fires the
   * observer again with a real box, and the chart draws.
   */
  function reportIfFlat(figure) {
    if (figure.dataset.mvpChartFlatReported) {
      return;
    }
    var box = figure.getBoundingClientRect();
    if (box.width <= 0 || box.height >= 1) {
      return;
    }
    figure.dataset.mvpChartFlatReported = "1";
    window.console.warn(
      "mvp-charts: " +
        (figure.id || "a chart") +
        " has no height to draw into. Give it a height attribute, or give the " +
        "element around it a height a percentage can resolve against."
    );
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
