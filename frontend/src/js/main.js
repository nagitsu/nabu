import {formatNumber} from './utils';
import {countHistogram, activityCharts} from './charts';


const API_DOMAIN = 'http://golbat.ydns.eu';


function drawCharts() {
  let totalsCall = $.get(`${API_DOMAIN}/api/dashboard/totals`);
  let overTimeCall = $.get(`${API_DOMAIN}/api/dashboard/over-time`);

  totalsCall.done(data => countHistogram(data.data));

  // TODO: Probably shouldn't require the first call to be ready, but need to
  // fix layout.
  $.when(totalsCall, overTimeCall).done((_, deferredResult) => {
    let wordsPerDay = deferredResult[0].data;
    activityCharts(wordsPerDay);
  });
}


function updateCounter() {
  return $.get(`${API_DOMAIN}/api/dashboard/word-count`).then(data => {
    $('#corpus-size').text(formatNumber(data.word_count));
  });
}


function setUpCounter() {
  updateCounter().then(() => window.setInterval(updateCounter, 1000));
}


$(document).ready(function () {
  setUpCounter();
  drawCharts();
});
