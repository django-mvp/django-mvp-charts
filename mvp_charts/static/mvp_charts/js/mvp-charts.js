/*
 * Draw every chart on the page and keep each at the size of its box. Failures
 * go to the console: what a page shows when something breaks is the project's
 * call. Each figure fires `mvp-chart:drawn` with its ECharts instance.
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
    // Whatever renderer this names must be registered in the page's ECharts:
    // always in a full build, in a bundle only if it imported it.
    var chart = window.echarts.init(surface, null, {
      renderer: figure.dataset.mvpChartRenderer,
    });
    chart.setOption(JSON.parse(options.textContent));

    // After the chart is on the surface, never before: a figure that goes
    // empty and stays empty is worse than one that never stopped waiting.
    var placeholder = figure.querySelector("[data-mvp-chart-placeholder]");
    if (placeholder) {
      placeholder.remove();
    }

    // The surface rather than the figure: a caption that wraps to another
    // line takes its room from the chart while the figure keeps its size.
    if (window.ResizeObserver) {
      new window.ResizeObserver(function () {
        chart.resize();
        reportIfFlat(figure, surface);
      }).observe(surface);
    }

    // Last, so a listener gets a chart that is drawn, uncovered and following
    // its box. It bubbles, so one listener on the document hears every chart.
    figure.dispatchEvent(
      new window.CustomEvent("mvp-chart:drawn", {
        bubbles: true,
        detail: { chart: chart },
      })
    );
  }

  /*
   * Warn once about a surface with width but no height, the one failure that
   * leaves no other trace. A hidden panel measures 0x0 and is not reported.
   */
  function reportIfFlat(figure, surface) {
    if (figure.dataset.mvpChartFlatReported) {
      return;
    }
    var box = surface.getBoundingClientRect();
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
