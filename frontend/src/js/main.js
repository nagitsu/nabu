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


function displayEmbeddings() {
  return $.get(`${API_DOMAIN}/api/embedding`).then(data => {
    // Empty the embedding list.
    $('.embedding-list').empty();
    let embeddings = data.result;

    let trained = embeddings.filter(e => e.state == 'SUCCESS');
    let training = embeddings.filter(e => e.state == 'PROGRESS');
    let waiting = embeddings.filter(e => e.state == 'PENDING');
    let notTrained = embeddings.filter(e => e.state == 'NOT_STARTED');
    let failed = embeddings.filter(e => e.state == 'FAILURE');

    if (trained.length > 0) {
      let trainedNode = $(
        '<div class="embedding-group trained">' +
          '<div class="embedding-group-header">Trained</div>' +
        '</div>'
      );
      for (let embedding of trained) {
        let newNode = $('<div class="embedding embedding-striped"></div>');
        newNode.text(embedding.description);
        newNode.prepend($(`<span class="embedding-id">(${embedding.id})</span>`));
        trainedNode.append(newNode);
      }
      $('.embedding-list').append(trainedNode);
    }

    if (training.length > 0) {
      let trainingNode = $(
        '<div class="embedding-group training">' +
          '<div class="embedding-group-header">Training</div>' +
        '</div>'
      );
      for (let embedding of training) {
        let newNode = $('<div class="embedding embedding-progress"></div>');

        let progress = (embedding.progress * 100).toFixed(2) + "%";
        newNode.css('background-size', `${progress} 100%`);

        newNode.text(`${progress} - ${embedding.description}`);
        newNode.prepend($(`<span class="embedding-id">(${embedding.id})</span>`));

        let cancelButton = $('<a href="#" class="embedding-action embedding-cancel">Cancel</a>')
        cancelButton.click(e => {
          e.preventDefault();
          $.post(`${API_DOMAIN}/api/embedding/${embedding.id}/train-cancel`)
        });
        newNode.append(cancelButton);

        trainingNode.append(newNode);
      }
      $('.embedding-list').append(trainingNode);
    }

    if (waiting.length > 0) {
      let waitingNode = $(
        '<div class="embedding-group waiting">' +
          '<div class="embedding-group-header">Waiting</div>' +
        '</div>'
      );
      for (let embedding of waiting) {
        let newNode = $('<div class="embedding embedding-striped"></div>');
        newNode.text(embedding.description);
        newNode.prepend($(`<span class="embedding-id">(${embedding.id})</span>`));

        let cancelButton = $('<a href="#" class="embedding-action embedding-cancel">Cancel</a>')
        cancelButton.click(e => {
          e.preventDefault();
          $.post(`${API_DOMAIN}/api/embedding/${embedding.id}/train-cancel`)
        });
        newNode.append(cancelButton);

        waitingNode.append(newNode);
      }
      $('.embedding-list').append(waitingNode);
    }

    if (failed.length > 0) {
      let failedNode = $(
        '<div class="embedding-group failed">' +
          '<div class="embedding-group-header">Failed</div>' +
        '</div>'
      );
      for (let embedding of failed) {
        let newNode = $('<div class="embedding embedding-striped"></div>');
        newNode.text(embedding.description);
        newNode.prepend($(`<span class="embedding-id">(${embedding.id})</span>`));

        let retryButton = $('<a href="#" class="embedding-action embedding-train">Retry</a>')
        retryButton.click(e => {
          e.preventDefault();
          $.post(`${API_DOMAIN}/api/embedding/${embedding.id}/train-start`)
        });
        newNode.append(retryButton);

        failedNode.append(newNode);
      }
      $('.embedding-list').append(failedNode);
    }

    if (notTrained.length > 0) {
      let notTrainedNode = $(
        '<div class="embedding-group not-trained">' +
          '<div class="embedding-group-header">Not trained yet</div>' +
        '</div>'
      );
      for (let embedding of notTrained) {
        let newNode = $('<div class="embedding embedding-striped"></div>');
        newNode.text(embedding.description);
        newNode.prepend($(`<span class="embedding-id">(${embedding.id})</span>`));

        let trainButton = $('<a href="#" class="embedding-action embedding-train">Train</a>')
        trainButton.click(e => {
          e.preventDefault();
          $.post(`${API_DOMAIN}/api/embedding/${embedding.id}/train-start`)
        });
        newNode.append(trainButton);

        notTrainedNode.append(newNode);
      }
      $('.embedding-list').append(notTrainedNode);
    }
  });
}


function updateCounter() {
  return $.get(`${API_DOMAIN}/api/dashboard/word-count`).then(data => {
    $('#corpus-size').text(formatNumber(data.word_count));
  });
}


function runAndRepeat(func, interval) {
  func().then(() => window.setInterval(func, interval));
}


$(document).ready(function () {
  runAndRepeat(updateCounter, 1000);
  runAndRepeat(displayEmbeddings, 1000);
  drawCharts();
});
