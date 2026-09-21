/*
 * Stands in for the charting library, arriving as a separate file the way a
 * project's own bundle does.
 *
 * The region reads one global and calls nothing on it, so what the object
 * contains is irrelevant to every assertion here — and serving a stand-in
 * rather than fetching ECharts keeps the suite off the network, where a
 * failure would say nothing about this package.
 */
window.echarts = { version: "stand-in" };
