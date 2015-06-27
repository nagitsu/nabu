import {totalWords, formatNumber} from './utils';
import {countHistogram, activityCharts} from './charts';


const API_DOMAIN = 'http://localhost:5000'


function drawCharts() {
  let totalsCall = $.get(`${API_DOMAIN}/api/dashboard/totals`);
  let overTimeCall = $.get(`${API_DOMAIN}/api/dashboard/over-time`);

  totalsCall.done(data => {
    let wordsPerSource = data.data;
    $('#corpus-size').text(formatNumber(totalWords(wordsPerSource)));
    countHistogram(wordsPerSource);
  });

  // TODO: Probably shouldn't require the first call to be ready, but need to
  // fix layout.
  $.when(totalsCall, overTimeCall).done((_, deferredResult) => {
    let wordsPerDay = deferredResult[0].data;
    activityCharts(wordsPerDay);
  });
}


$(document).ready(() => drawCharts());
