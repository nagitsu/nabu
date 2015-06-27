import {totalWords, formatNumber} from './utils';


/* Creates the histogram chart with the counts per source. */
export function countHistogram(wordsPerSource) {
  wordsPerSource.sort((a, b) => a.value < b.value);

  let scale = d3.scale.linear()
      .domain([0, d3.max(wordsPerSource, d => d.value)])
      .range([0, 80]);

  let container = d3.select('.source-list')
    .selectAll('.source-entry')
      .data(wordsPerSource)
    .enter().append('div')
      .attr('class', 'source-entry')
      .attr('data-source', d => d.source)
    .append('div')
      .attr('class', 'bar-container');

  container.append('div')
      .attr('class', (d, idx) => `bar bar-${idx % 5 + 1}`)
      .attr('title', d => d.source)
      .text(d => d.source)
      .style('width', d => scale(d.value) + '%');

  container.append('div')
      .attr('class', 'bar-value')
      .text(d => formatNumber(d.value));
}


/* Creates the activity charts for each source. */
export function activityCharts(wordsPerDay) {
  let width = 70;
  let height = 28;

  for (let sourceData of wordsPerDay) {
    let source = sourceData.value;

    let svg = d3.select('.source-entry[data-source="' + sourceData.source + '"]')
      .insert('div', 'div')
        .attr('class', 'over-time-chart')
      .append('svg')
        .attr('class', 'chart')
        .attr('width', width)
        .attr('height', height);

    let x = d3.scale.ordinal()
        .domain(source.map(d => d.day))
        .rangeRoundBands([0, width]);

    let y = d3.scale.linear()
        .domain([0, d3.max(source.map(d => d.value))])
        .range([height, 0]);

    svg.selectAll('.bar')
        .data(source)
    .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', d => x(d.day))
        .attr('y', height)
        .attr('width', x.rangeBand())
        .attr('height', d => height - y(d.value))
      .transition()
        .duration(2000)
        .attr('y', d => y(d.value));
  }
}
