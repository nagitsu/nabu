(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
'use strict';

Object.defineProperty(exports, '__esModule', {
  value: true
});
exports.countHistogram = countHistogram;
exports.activityCharts = activityCharts;

var _utils = require('./utils');

/* Creates the histogram chart with the counts per source. */

function countHistogram(wordsPerSource) {
  wordsPerSource.sort(function (a, b) {
    return a.value < b.value;
  });

  var scale = d3.scale.linear().domain([0, d3.max(wordsPerSource, function (d) {
    return d.value;
  })]).range([0, 80]);

  var container = d3.select('.source-list').selectAll('.source-entry').data(wordsPerSource).enter().append('div').attr('class', 'source-entry').attr('data-source', function (d) {
    return d.source;
  }).append('div').attr('class', 'bar-container');

  container.append('div').attr('class', function (d, idx) {
    return 'bar bar-' + (idx % 5 + 1);
  }).attr('title', function (d) {
    return d.source;
  }).text(function (d) {
    return d.source;
  }).style('width', function (d) {
    return scale(d.value) + '%';
  });

  container.append('div').attr('class', 'bar-value').text(function (d) {
    return (0, _utils.humanizeNumber)(d.value);
  });
}

/* Creates the activity charts for each source. */

function activityCharts(wordsPerDay) {
  var width = 70;
  var height = 28;

  var _iteratorNormalCompletion = true;
  var _didIteratorError = false;
  var _iteratorError = undefined;

  try {
    var _loop = function () {
      var sourceData = _step.value;

      var source = sourceData.value;

      var svg = d3.select('.source-entry[data-source="' + sourceData.source + '"]').insert('div', 'div').attr('class', 'over-time-chart').append('svg').attr('class', 'chart').attr('width', width).attr('height', height);

      var x = d3.scale.ordinal().domain(source.map(function (d) {
        return d.day;
      })).rangeRoundBands([0, width]);

      var y = d3.scale.linear().domain([0, d3.max(source.map(function (d) {
        return d.value;
      }))]).range([height, 0]);

      svg.selectAll('.bar').data(source).enter().append('rect').attr('class', 'bar').attr('x', function (d) {
        return x(d.day);
      }).attr('y', height).attr('width', x.rangeBand()).attr('height', function (d) {
        return height - y(d.value);
      }).transition().duration(2000).attr('y', function (d) {
        return y(d.value);
      });
    };

    for (var _iterator = wordsPerDay[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
      _loop();
    }
  } catch (err) {
    _didIteratorError = true;
    _iteratorError = err;
  } finally {
    try {
      if (!_iteratorNormalCompletion && _iterator['return']) {
        _iterator['return']();
      }
    } finally {
      if (_didIteratorError) {
        throw _iteratorError;
      }
    }
  }
}

},{"./utils":3}],2:[function(require,module,exports){
'use strict';

var _utils = require('./utils');

var _charts = require('./charts');

var API_DOMAIN = 'http://golbat.ydns.eu';

function drawCharts() {
  var totalsCall = $.get(API_DOMAIN + '/api/dashboard/totals');
  var overTimeCall = $.get(API_DOMAIN + '/api/dashboard/over-time');

  totalsCall.done(function (data) {
    return (0, _charts.countHistogram)(data.data);
  });

  // TODO: Probably shouldn't require the first call to be ready, but need to
  // fix layout.
  $.when(totalsCall, overTimeCall).done(function (_, deferredResult) {
    var wordsPerDay = deferredResult[0].data;
    (0, _charts.activityCharts)(wordsPerDay);
  });
}

function displayEmbeddings() {
  return $.get(API_DOMAIN + '/api/embedding').then(function (data) {
    // Empty the embedding list.
    $('.embedding-list').empty();
    var embeddings = data.result;

    var trained = embeddings.filter(function (e) {
      return e.state == 'SUCCESS';
    });
    var training = embeddings.filter(function (e) {
      return e.state == 'PROGRESS';
    });
    var waiting = embeddings.filter(function (e) {
      return e.state == 'PENDING';
    });
    var notTrained = embeddings.filter(function (e) {
      return e.state == 'NOT_STARTED';
    });
    var failed = embeddings.filter(function (e) {
      return e.state == 'FAILURE';
    });

    if (trained.length > 0) {
      var trainedNode = $('<div class="embedding-group trained">' + '<div class="embedding-group-header">Trained</div>' + '</div>');
      var _iteratorNormalCompletion = true;
      var _didIteratorError = false;
      var _iteratorError = undefined;

      try {
        for (var _iterator = trained[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
          var embedding = _step.value;

          var newNode = $('<div class="embedding embedding-striped"></div>');
          newNode.text(embedding.description);
          newNode.prepend($('<span class="embedding-id">(' + embedding.id + ')</span>'));
          trainedNode.append(newNode);
        }
      } catch (err) {
        _didIteratorError = true;
        _iteratorError = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion && _iterator['return']) {
            _iterator['return']();
          }
        } finally {
          if (_didIteratorError) {
            throw _iteratorError;
          }
        }
      }

      $('.embedding-list').append(trainedNode);
    }

    if (training.length > 0) {
      var trainingNode = $('<div class="embedding-group training">' + '<div class="embedding-group-header">Training</div>' + '</div>');
      var _iteratorNormalCompletion2 = true;
      var _didIteratorError2 = false;
      var _iteratorError2 = undefined;

      try {
        var _loop = function () {
          var embedding = _step2.value;

          var newNode = $('<div class="embedding embedding-progress"></div>');

          var progress = (embedding.progress * 100).toFixed(2) + '%';
          newNode.css('background-size', progress + ' 100%');

          newNode.text(progress + ' - ' + embedding.description);
          newNode.prepend($('<span class="embedding-id">(' + embedding.id + ')</span>'));

          var cancelButton = $('<a href="#" class="embedding-action embedding-cancel">Cancel</a>');
          cancelButton.click(function (e) {
            e.preventDefault();
            $.post(API_DOMAIN + '/api/embedding/' + embedding.id + '/train-cancel');
          });
          newNode.append(cancelButton);

          trainingNode.append(newNode);
        };

        for (var _iterator2 = training[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
          _loop();
        }
      } catch (err) {
        _didIteratorError2 = true;
        _iteratorError2 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion2 && _iterator2['return']) {
            _iterator2['return']();
          }
        } finally {
          if (_didIteratorError2) {
            throw _iteratorError2;
          }
        }
      }

      $('.embedding-list').append(trainingNode);
    }

    if (waiting.length > 0) {
      var waitingNode = $('<div class="embedding-group waiting">' + '<div class="embedding-group-header">Waiting</div>' + '</div>');
      var _iteratorNormalCompletion3 = true;
      var _didIteratorError3 = false;
      var _iteratorError3 = undefined;

      try {
        var _loop2 = function () {
          var embedding = _step3.value;

          var newNode = $('<div class="embedding embedding-striped"></div>');
          newNode.text(embedding.description);
          newNode.prepend($('<span class="embedding-id">(' + embedding.id + ')</span>'));

          var cancelButton = $('<a href="#" class="embedding-action embedding-cancel">Cancel</a>');
          cancelButton.click(function (e) {
            e.preventDefault();
            $.post(API_DOMAIN + '/api/embedding/' + embedding.id + '/train-cancel');
          });
          newNode.append(cancelButton);

          waitingNode.append(newNode);
        };

        for (var _iterator3 = waiting[Symbol.iterator](), _step3; !(_iteratorNormalCompletion3 = (_step3 = _iterator3.next()).done); _iteratorNormalCompletion3 = true) {
          _loop2();
        }
      } catch (err) {
        _didIteratorError3 = true;
        _iteratorError3 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion3 && _iterator3['return']) {
            _iterator3['return']();
          }
        } finally {
          if (_didIteratorError3) {
            throw _iteratorError3;
          }
        }
      }

      $('.embedding-list').append(waitingNode);
    }

    if (failed.length > 0) {
      var failedNode = $('<div class="embedding-group failed">' + '<div class="embedding-group-header">Failed</div>' + '</div>');
      var _iteratorNormalCompletion4 = true;
      var _didIteratorError4 = false;
      var _iteratorError4 = undefined;

      try {
        var _loop3 = function () {
          var embedding = _step4.value;

          var newNode = $('<div class="embedding embedding-striped"></div>');
          newNode.text(embedding.description);
          newNode.prepend($('<span class="embedding-id">(' + embedding.id + ')</span>'));

          var retryButton = $('<a href="#" class="embedding-action embedding-train">Retry</a>');
          retryButton.click(function (e) {
            e.preventDefault();
            $.post(API_DOMAIN + '/api/embedding/' + embedding.id + '/train-start');
          });
          newNode.append(retryButton);

          failedNode.append(newNode);
        };

        for (var _iterator4 = failed[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
          _loop3();
        }
      } catch (err) {
        _didIteratorError4 = true;
        _iteratorError4 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion4 && _iterator4['return']) {
            _iterator4['return']();
          }
        } finally {
          if (_didIteratorError4) {
            throw _iteratorError4;
          }
        }
      }

      $('.embedding-list').append(failedNode);
    }

    if (notTrained.length > 0) {
      var notTrainedNode = $('<div class="embedding-group not-trained">' + '<div class="embedding-group-header">Not trained yet</div>' + '</div>');
      var _iteratorNormalCompletion5 = true;
      var _didIteratorError5 = false;
      var _iteratorError5 = undefined;

      try {
        var _loop4 = function () {
          var embedding = _step5.value;

          var newNode = $('<div class="embedding embedding-striped"></div>');
          newNode.text(embedding.description);
          newNode.prepend($('<span class="embedding-id">(' + embedding.id + ')</span>'));

          var trainButton = $('<a href="#" class="embedding-action embedding-train">Train</a>');
          trainButton.click(function (e) {
            e.preventDefault();
            $.post(API_DOMAIN + '/api/embedding/' + embedding.id + '/train-start');
          });
          newNode.append(trainButton);

          notTrainedNode.append(newNode);
        };

        for (var _iterator5 = notTrained[Symbol.iterator](), _step5; !(_iteratorNormalCompletion5 = (_step5 = _iterator5.next()).done); _iteratorNormalCompletion5 = true) {
          _loop4();
        }
      } catch (err) {
        _didIteratorError5 = true;
        _iteratorError5 = err;
      } finally {
        try {
          if (!_iteratorNormalCompletion5 && _iterator5['return']) {
            _iterator5['return']();
          }
        } finally {
          if (_didIteratorError5) {
            throw _iteratorError5;
          }
        }
      }

      $('.embedding-list').append(notTrainedNode);
    }
  });
}

function updateCounter() {
  return $.get(API_DOMAIN + '/api/dashboard/word-count').then(function (data) {
    $('#corpus-size').text((0, _utils.formatNumber)(data.word_count));
  });
}

function runAndRepeat(func, interval) {
  func().then(function () {
    return window.setInterval(func, interval);
  });
}

$(document).ready(function () {
  runAndRepeat(updateCounter, 1000);
  runAndRepeat(displayEmbeddings, 1000);
  drawCharts();
});

},{"./charts":1,"./utils":3}],3:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.formatNumber = formatNumber;
exports.humanizeNumber = humanizeNumber;

function formatNumber(number) {
  return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function humanizeNumber(number) {
  var millions = Math.round(number / 1000000);
  var formatted = millions.toString().replace(/(\d)(?=(\d{3})+$)/g, "$1.") + "M";
  return formatted;
}

},{}]},{},[2])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvY2hhcnRzLmpzIiwiL2hvbWUvYWd1c3Rpbi9wcm95L2NvZGUvZnJvbnRlbmQvc3JjL2pzL21haW4uanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7OztRQ0lnQixjQUFjLEdBQWQsY0FBYztRQTZCZCxjQUFjLEdBQWQsY0FBYzs7cUJBakNELFNBQVM7Ozs7QUFJL0IsU0FBUyxjQUFjLENBQUMsY0FBYyxFQUFFO0FBQzdDLGdCQUFjLENBQUMsSUFBSSxDQUFDLFVBQUMsQ0FBQyxFQUFFLENBQUM7V0FBSyxDQUFDLENBQUMsS0FBSyxHQUFHLENBQUMsQ0FBQyxLQUFLO0dBQUEsQ0FBQyxDQUFDOztBQUVqRCxNQUFJLEtBQUssR0FBRyxFQUFFLENBQUMsS0FBSyxDQUFDLE1BQU0sRUFBRSxDQUN4QixNQUFNLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLEdBQUcsQ0FBQyxjQUFjLEVBQUUsVUFBQSxDQUFDO1dBQUksQ0FBQyxDQUFDLEtBQUs7R0FBQSxDQUFDLENBQUMsQ0FBQyxDQUNqRCxLQUFLLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLENBQUMsQ0FBQzs7QUFFcEIsTUFBSSxTQUFTLEdBQUcsRUFBRSxDQUFDLE1BQU0sQ0FBQyxjQUFjLENBQUMsQ0FDdEMsU0FBUyxDQUFDLGVBQWUsQ0FBQyxDQUN4QixJQUFJLENBQUMsY0FBYyxDQUFDLENBQ3RCLEtBQUssRUFBRSxDQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUMsQ0FDbkIsSUFBSSxDQUFDLE9BQU8sRUFBRSxjQUFjLENBQUMsQ0FDN0IsSUFBSSxDQUFDLGFBQWEsRUFBRSxVQUFBLENBQUM7V0FB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LFNBQVMsWUFBWSxDQUFDLE1BQU0sRUFBRTtBQUNuQyxTQUFPLE1BQU0sQ0FBQyxRQUFRLEVBQUUsQ0FBQyxPQUFPLENBQUMsdUJBQXVCLEVBQUUsR0FBRyxDQUFDLENBQUM7Q0FDaEU7O0FBR00sU0FBUyxjQUFjLENBQUMsTUFBTSxFQUFFO0FBQ3JDLE1BQUksUUFBUSxHQUFHLElBQUksQ0FBQyxLQUFLLENBQUMsTUFBTSxHQUFHLE9BQU8sQ0FBQyxDQUFDO0FBQzVDLE1BQUksU0FBUyxHQUFHLFFBQVEsQ0FBQyxRQUFRLEVBQUUsQ0FBQyxPQUFPLENBQUMsb0JBQW9CLEVBQUUsS0FBSyxDQUFDLEdBQUcsR0FBRyxDQUFDO0FBQy9FLFNBQU8sU0FBUyxDQUFDO0NBQ2xCIiwiZmlsZSI6ImdlbmVyYXRlZC5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzQ29udGVudCI6WyIoZnVuY3Rpb24gZSh0LG4scil7ZnVuY3Rpb24gcyhvLHUpe2lmKCFuW29dKXtpZighdFtvXSl7dmFyIGE9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtpZighdSYmYSlyZXR1cm4gYShvLCEwKTtpZihpKXJldHVybiBpKG8sITApO3ZhciBmPW5ldyBFcnJvcihcIkNhbm5vdCBmaW5kIG1vZHVsZSAnXCIrbytcIidcIik7dGhyb3cgZi5jb2RlPVwiTU9EVUxFX05PVF9GT1VORFwiLGZ9dmFyIGw9bltvXT17ZXhwb3J0czp7fX07dFtvXVswXS5jYWxsKGwuZXhwb3J0cyxmdW5jdGlvbihlKXt2YXIgbj10W29dWzFdW2VdO3JldHVybiBzKG4/bjplKX0sbCxsLmV4cG9ydHMsZSx0LG4scil9cmV0dXJuIG5bb10uZXhwb3J0c312YXIgaT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2Zvcih2YXIgbz0wO288ci5sZW5ndGg7bysrKXMocltvXSk7cmV0dXJuIHN9KSIsImltcG9ydCB7aHVtYW5pemVOdW1iZXJ9IGZyb20gJy4vdXRpbHMnO1xuXG5cbi8qIENyZWF0ZXMgdGhlIGhpc3RvZ3JhbSBjaGFydCB3aXRoIHRoZSBjb3VudHMgcGVyIHNvdXJjZS4gKi9cbmV4cG9ydCBmdW5jdGlvbiBjb3VudEhpc3RvZ3JhbSh3b3Jkc1BlclNvdXJjZSkge1xuICB3b3Jkc1BlclNvdXJjZS5zb3J0KChhLCBiKSA9PiBhLnZhbHVlIDwgYi52YWx1ZSk7XG5cbiAgbGV0IHNjYWxlID0gZDMuc2NhbGUubGluZWFyKClcbiAgICAgIC5kb21haW4oWzAsIGQzLm1heCh3b3Jkc1BlclNvdXJjZSwgZCA9PiBkLnZhbHVlKV0pXG4gICAgICAucmFuZ2UoWzAsIDgwXSk7XG5cbiAgbGV0IGNvbnRhaW5lciA9IGQzLnNlbGVjdCgnLnNvdXJjZS1saXN0JylcbiAgICAuc2VsZWN0QWxsKCcuc291cmNlLWVudHJ5JylcbiAgICAgIC5kYXRhKHdvcmRzUGVyU291cmNlKVxuICAgIC5lbnRlcigpLmFwcGVuZCgnZGl2JylcbiAgICAgIC5hdHRyKCdjbGFzcycsICdzb3VyY2UtZW50cnknKVxuICAgICAgLmF0dHIoJ2RhdGEtc291cmNlJywgZCA9PiBkLnNvdXJjZSlcbiAgICAuYXBwZW5kKCdkaXYnKVxuICAgICAgLmF0dHIoJ2NsYXNzJywgJ2Jhci1jb250YWluZXInKTtcblxuICBjb250YWluZXIuYXBwZW5kKCdkaXYnKVxuICAgICAgLmF0dHIoJ2NsYXNzJywgKGQsIGlkeCkgPT4gYGJhciBiYXItJHtpZHggJSA1ICsgMX1gKVxuICAgICAgLmF0dHIoJ3RpdGxlJywgZCA9PiBkLnNvdXJjZSlcbiAgICAgIC50ZXh0KGQgPT4gZC5zb3VyY2UpXG4gICAgICAuc3R5bGUoJ3dpZHRoJywgZCA9PiBzY2FsZShkLnZhbHVlKSArICclJyk7XG5cbiAgY29udGFpbmVyLmFwcGVuZCgnZGl2JylcbiAgICAgIC5hdHRyKCdjbGFzcycsICdiYXItdmFsdWUnKVxuICAgICAgLnRleHQoZCA9PiBodW1hbml6ZU51bWJlcihkLnZhbHVlKSk7XG59XG5cblxuLyogQ3JlYXRlcyB0aGUgYWN0aXZpdHkgY2hhcnRzIGZvciBlYWNoIHNvdXJjZS4gKi9cbmV4cG9ydCBmdW5jdGlvbiBhY3Rpdml0eUNoYXJ0cyh3b3Jkc1BlckRheSkge1xuICBsZXQgd2lkdGggPSA3MDtcbiAgbGV0IGhlaWdodCA9IDI4O1xuXG4gIGZvciAobGV0IHNvdXJjZURhdGEgb2Ygd29yZHNQZXJEYXkpIHtcbiAgICBsZXQgc291cmNlID0gc291cmNlRGF0YS52YWx1ZTtcblxuICAgIGxldCBzdmcgPSBkMy5zZWxlY3QoJy5zb3VyY2UtZW50cnlbZGF0YS1zb3VyY2U9XCInICsgc291cmNlRGF0YS5zb3VyY2UgKyAnXCJdJylcbiAgICAgIC5pbnNlcnQoJ2RpdicsICdkaXYnKVxuICAgICAgICAuYXR0cignY2xhc3MnLCAnb3Zlci10aW1lLWNoYXJ0JylcbiAgICAgIC5hcHBlbmQoJ3N2ZycpXG4gICAgICAgIC5hdHRyKCdjbGFzcycsICdjaGFydCcpXG4gICAgICAgIC5hdHRyKCd3aWR0aCcsIHdpZHRoKVxuICAgICAgICAuYXR0cignaGVpZ2h0JywgaGVpZ2h0KTtcblxuICAgIGxldCB4ID0gZDMuc2NhbGUub3JkaW5hbCgpXG4gICAgICAgIC5kb21haW4oc291cmNlLm1hcChkID0+IGQuZGF5KSlcbiAgICAgICAgLnJhbmdlUm91bmRCYW5kcyhbMCwgd2lkdGhdKTtcblxuICAgIGxldCB5ID0gZDMuc2NhbGUubGluZWFyKClcbiAgICAgICAgLmRvbWFpbihbMCwgZDMubWF4KHNvdXJjZS5tYXAoZCA9PiBkLnZhbHVlKSldKVxuICAgICAgICAucmFuZ2UoW2hlaWdodCwgMF0pO1xuXG4gICAgc3ZnLnNlbGVjdEFsbCgnLmJhcicpXG4gICAgICAgIC5kYXRhKHNvdXJjZSlcbiAgICAuZW50ZXIoKS5hcHBlbmQoJ3JlY3QnKVxuICAgICAgICAuYXR0cignY2xhc3MnLCAnYmFyJylcbiAgICAgICAgLmF0dHIoJ3gnLCBkID0+IHgoZC5kYXkpKVxuICAgICAgICAuYXR0cigneScsIGhlaWdodClcbiAgICAgICAgLmF0dHIoJ3dpZHRoJywgeC5yYW5nZUJhbmQoKSlcbiAgICAgICAgLmF0dHIoJ2hlaWdodCcsIGQgPT4gaGVpZ2h0IC0geShkLnZhbHVlKSlcbiAgICAgIC50cmFuc2l0aW9uKClcbiAgICAgICAgLmR1cmF0aW9uKDIwMDApXG4gICAgICAgIC5hdHRyKCd5JywgZCA9PiB5KGQudmFsdWUpKTtcbiAgfVxufVxuIiwiaW1wb3J0IHtmb3JtYXROdW1iZXJ9IGZyb20gJy4vdXRpbHMnO1xuaW1wb3J0IHtjb3VudEhpc3RvZ3JhbSwgYWN0aXZpdHlDaGFydHN9IGZyb20gJy4vY2hhcnRzJztcblxuXG5jb25zdCBBUElfRE9NQUlOID0gJ2h0dHA6Ly9nb2xiYXQueWRucy5ldSc7XG5cblxuZnVuY3Rpb24gZHJhd0NoYXJ0cygpIHtcbiAgbGV0IHRvdGFsc0NhbGwgPSAkLmdldChgJHtBUElfRE9NQUlOfS9hcGkvZGFzaGJvYXJkL3RvdGFsc2ApO1xuICBsZXQgb3ZlclRpbWVDYWxsID0gJC5nZXQoYCR7QVBJX0RPTUFJTn0vYXBpL2Rhc2hib2FyZC9vdmVyLXRpbWVgKTtcblxuICB0b3RhbHNDYWxsLmRvbmUoZGF0YSA9PiBjb3VudEhpc3RvZ3JhbShkYXRhLmRhdGEpKTtcblxuICAvLyBUT0RPOiBQcm9iYWJseSBzaG91bGRuJ3QgcmVxdWlyZSB0aGUgZmlyc3QgY2FsbCB0byBiZSByZWFkeSwgYnV0IG5lZWQgdG9cbiAgLy8gZml4IGxheW91dC5cbiAgJC53aGVuKHRvdGFsc0NhbGwsIG92ZXJUaW1lQ2FsbCkuZG9uZSgoXywgZGVmZXJyZWRSZXN1bHQpID0+IHtcbiAgICBsZXQgd29yZHNQZXJEYXkgPSBkZWZlcnJlZFJlc3VsdFswXS5kYXRhO1xuICAgIGFjdGl2aXR5Q2hhcnRzKHdvcmRzUGVyRGF5KTtcbiAgfSk7XG59XG5cblxuZnVuY3Rpb24gZGlzcGxheUVtYmVkZGluZ3MoKSB7XG4gIHJldHVybiAkLmdldChgJHtBUElfRE9NQUlOfS9hcGkvZW1iZWRkaW5nYCkudGhlbihkYXRhID0+IHtcbiAgICAvLyBFbXB0eSB0aGUgZW1iZWRkaW5nIGxpc3QuXG4gICAgJCgnLmVtYmVkZGluZy1saXN0JykuZW1wdHkoKTtcbiAgICBsZXQgZW1iZWRkaW5ncyA9IGRhdGEucmVzdWx0O1xuXG4gICAgbGV0IHRyYWluZWQgPSBlbWJlZGRpbmdzLmZpbHRlcihlID0+IGUuc3RhdGUgPT0gJ1NVQ0NFU1MnKTtcbiAgICBsZXQgdHJhaW5pbmcgPSBlbWJlZGRpbmdzLmZpbHRlcihlID0+IGUuc3RhdGUgPT0gJ1BST0dSRVNTJyk7XG4gICAgbGV0IHdhaXRpbmcgPSBlbWJlZGRpbmdzLmZpbHRlcihlID0+IGUuc3RhdGUgPT0gJ1BFTkRJTkcnKTtcbiAgICBsZXQgbm90VHJhaW5lZCA9IGVtYmVkZGluZ3MuZmlsdGVyKGUgPT4gZS5zdGF0ZSA9PSAnTk9UX1NUQVJURUQnKTtcbiAgICBsZXQgZmFpbGVkID0gZW1iZWRkaW5ncy5maWx0ZXIoZSA9PiBlLnN0YXRlID09ICdGQUlMVVJFJyk7XG5cbiAgICBpZiAodHJhaW5lZC5sZW5ndGggPiAwKSB7XG4gICAgICBsZXQgdHJhaW5lZE5vZGUgPSAkKFxuICAgICAgICAnPGRpdiBjbGFzcz1cImVtYmVkZGluZy1ncm91cCB0cmFpbmVkXCI+JyArXG4gICAgICAgICAgJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmctZ3JvdXAtaGVhZGVyXCI+VHJhaW5lZDwvZGl2PicgK1xuICAgICAgICAnPC9kaXY+J1xuICAgICAgKTtcbiAgICAgIGZvciAobGV0IGVtYmVkZGluZyBvZiB0cmFpbmVkKSB7XG4gICAgICAgIGxldCBuZXdOb2RlID0gJCgnPGRpdiBjbGFzcz1cImVtYmVkZGluZyBlbWJlZGRpbmctc3RyaXBlZFwiPjwvZGl2PicpO1xuICAgICAgICBuZXdOb2RlLnRleHQoZW1iZWRkaW5nLmRlc2NyaXB0aW9uKTtcbiAgICAgICAgbmV3Tm9kZS5wcmVwZW5kKCQoYDxzcGFuIGNsYXNzPVwiZW1iZWRkaW5nLWlkXCI+KCR7ZW1iZWRkaW5nLmlkfSk8L3NwYW4+YCkpO1xuICAgICAgICB0cmFpbmVkTm9kZS5hcHBlbmQobmV3Tm9kZSk7XG4gICAgICB9XG4gICAgICAkKCcuZW1iZWRkaW5nLWxpc3QnKS5hcHBlbmQodHJhaW5lZE5vZGUpO1xuICAgIH1cblxuICAgIGlmICh0cmFpbmluZy5sZW5ndGggPiAwKSB7XG4gICAgICBsZXQgdHJhaW5pbmdOb2RlID0gJChcbiAgICAgICAgJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmctZ3JvdXAgdHJhaW5pbmdcIj4nICtcbiAgICAgICAgICAnPGRpdiBjbGFzcz1cImVtYmVkZGluZy1ncm91cC1oZWFkZXJcIj5UcmFpbmluZzwvZGl2PicgK1xuICAgICAgICAnPC9kaXY+J1xuICAgICAgKTtcbiAgICAgIGZvciAobGV0IGVtYmVkZGluZyBvZiB0cmFpbmluZykge1xuICAgICAgICBsZXQgbmV3Tm9kZSA9ICQoJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmcgZW1iZWRkaW5nLXByb2dyZXNzXCI+PC9kaXY+Jyk7XG5cbiAgICAgICAgbGV0IHByb2dyZXNzID0gKGVtYmVkZGluZy5wcm9ncmVzcyAqIDEwMCkudG9GaXhlZCgyKSArIFwiJVwiO1xuICAgICAgICBuZXdOb2RlLmNzcygnYmFja2dyb3VuZC1zaXplJywgYCR7cHJvZ3Jlc3N9IDEwMCVgKTtcblxuICAgICAgICBuZXdOb2RlLnRleHQoYCR7cHJvZ3Jlc3N9IC0gJHtlbWJlZGRpbmcuZGVzY3JpcHRpb259YCk7XG4gICAgICAgIG5ld05vZGUucHJlcGVuZCgkKGA8c3BhbiBjbGFzcz1cImVtYmVkZGluZy1pZFwiPigke2VtYmVkZGluZy5pZH0pPC9zcGFuPmApKTtcblxuICAgICAgICBsZXQgY2FuY2VsQnV0dG9uID0gJCgnPGEgaHJlZj1cIiNcIiBjbGFzcz1cImVtYmVkZGluZy1hY3Rpb24gZW1iZWRkaW5nLWNhbmNlbFwiPkNhbmNlbDwvYT4nKVxuICAgICAgICBjYW5jZWxCdXR0b24uY2xpY2soZSA9PiB7XG4gICAgICAgICAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICQucG9zdChgJHtBUElfRE9NQUlOfS9hcGkvZW1iZWRkaW5nLyR7ZW1iZWRkaW5nLmlkfS90cmFpbi1jYW5jZWxgKVxuICAgICAgICB9KTtcbiAgICAgICAgbmV3Tm9kZS5hcHBlbmQoY2FuY2VsQnV0dG9uKTtcblxuICAgICAgICB0cmFpbmluZ05vZGUuYXBwZW5kKG5ld05vZGUpO1xuICAgICAgfVxuICAgICAgJCgnLmVtYmVkZGluZy1saXN0JykuYXBwZW5kKHRyYWluaW5nTm9kZSk7XG4gICAgfVxuXG4gICAgaWYgKHdhaXRpbmcubGVuZ3RoID4gMCkge1xuICAgICAgbGV0IHdhaXRpbmdOb2RlID0gJChcbiAgICAgICAgJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmctZ3JvdXAgd2FpdGluZ1wiPicgK1xuICAgICAgICAgICc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nLWdyb3VwLWhlYWRlclwiPldhaXRpbmc8L2Rpdj4nICtcbiAgICAgICAgJzwvZGl2PidcbiAgICAgICk7XG4gICAgICBmb3IgKGxldCBlbWJlZGRpbmcgb2Ygd2FpdGluZykge1xuICAgICAgICBsZXQgbmV3Tm9kZSA9ICQoJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmcgZW1iZWRkaW5nLXN0cmlwZWRcIj48L2Rpdj4nKTtcbiAgICAgICAgbmV3Tm9kZS50ZXh0KGVtYmVkZGluZy5kZXNjcmlwdGlvbik7XG4gICAgICAgIG5ld05vZGUucHJlcGVuZCgkKGA8c3BhbiBjbGFzcz1cImVtYmVkZGluZy1pZFwiPigke2VtYmVkZGluZy5pZH0pPC9zcGFuPmApKTtcblxuICAgICAgICBsZXQgY2FuY2VsQnV0dG9uID0gJCgnPGEgaHJlZj1cIiNcIiBjbGFzcz1cImVtYmVkZGluZy1hY3Rpb24gZW1iZWRkaW5nLWNhbmNlbFwiPkNhbmNlbDwvYT4nKVxuICAgICAgICBjYW5jZWxCdXR0b24uY2xpY2soZSA9PiB7XG4gICAgICAgICAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICQucG9zdChgJHtBUElfRE9NQUlOfS9hcGkvZW1iZWRkaW5nLyR7ZW1iZWRkaW5nLmlkfS90cmFpbi1jYW5jZWxgKVxuICAgICAgICB9KTtcbiAgICAgICAgbmV3Tm9kZS5hcHBlbmQoY2FuY2VsQnV0dG9uKTtcblxuICAgICAgICB3YWl0aW5nTm9kZS5hcHBlbmQobmV3Tm9kZSk7XG4gICAgICB9XG4gICAgICAkKCcuZW1iZWRkaW5nLWxpc3QnKS5hcHBlbmQod2FpdGluZ05vZGUpO1xuICAgIH1cblxuICAgIGlmIChmYWlsZWQubGVuZ3RoID4gMCkge1xuICAgICAgbGV0IGZhaWxlZE5vZGUgPSAkKFxuICAgICAgICAnPGRpdiBjbGFzcz1cImVtYmVkZGluZy1ncm91cCBmYWlsZWRcIj4nICtcbiAgICAgICAgICAnPGRpdiBjbGFzcz1cImVtYmVkZGluZy1ncm91cC1oZWFkZXJcIj5GYWlsZWQ8L2Rpdj4nICtcbiAgICAgICAgJzwvZGl2PidcbiAgICAgICk7XG4gICAgICBmb3IgKGxldCBlbWJlZGRpbmcgb2YgZmFpbGVkKSB7XG4gICAgICAgIGxldCBuZXdOb2RlID0gJCgnPGRpdiBjbGFzcz1cImVtYmVkZGluZyBlbWJlZGRpbmctc3RyaXBlZFwiPjwvZGl2PicpO1xuICAgICAgICBuZXdOb2RlLnRleHQoZW1iZWRkaW5nLmRlc2NyaXB0aW9uKTtcbiAgICAgICAgbmV3Tm9kZS5wcmVwZW5kKCQoYDxzcGFuIGNsYXNzPVwiZW1iZWRkaW5nLWlkXCI+KCR7ZW1iZWRkaW5nLmlkfSk8L3NwYW4+YCkpO1xuXG4gICAgICAgIGxldCByZXRyeUJ1dHRvbiA9ICQoJzxhIGhyZWY9XCIjXCIgY2xhc3M9XCJlbWJlZGRpbmctYWN0aW9uIGVtYmVkZGluZy10cmFpblwiPlJldHJ5PC9hPicpXG4gICAgICAgIHJldHJ5QnV0dG9uLmNsaWNrKGUgPT4ge1xuICAgICAgICAgIGUucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAkLnBvc3QoYCR7QVBJX0RPTUFJTn0vYXBpL2VtYmVkZGluZy8ke2VtYmVkZGluZy5pZH0vdHJhaW4tc3RhcnRgKVxuICAgICAgICB9KTtcbiAgICAgICAgbmV3Tm9kZS5hcHBlbmQocmV0cnlCdXR0b24pO1xuXG4gICAgICAgIGZhaWxlZE5vZGUuYXBwZW5kKG5ld05vZGUpO1xuICAgICAgfVxuICAgICAgJCgnLmVtYmVkZGluZy1saXN0JykuYXBwZW5kKGZhaWxlZE5vZGUpO1xuICAgIH1cblxuICAgIGlmIChub3RUcmFpbmVkLmxlbmd0aCA+IDApIHtcbiAgICAgIGxldCBub3RUcmFpbmVkTm9kZSA9ICQoXG4gICAgICAgICc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nLWdyb3VwIG5vdC10cmFpbmVkXCI+JyArXG4gICAgICAgICAgJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmctZ3JvdXAtaGVhZGVyXCI+Tm90IHRyYWluZWQgeWV0PC9kaXY+JyArXG4gICAgICAgICc8L2Rpdj4nXG4gICAgICApO1xuICAgICAgZm9yIChsZXQgZW1iZWRkaW5nIG9mIG5vdFRyYWluZWQpIHtcbiAgICAgICAgbGV0IG5ld05vZGUgPSAkKCc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nIGVtYmVkZGluZy1zdHJpcGVkXCI+PC9kaXY+Jyk7XG4gICAgICAgIG5ld05vZGUudGV4dChlbWJlZGRpbmcuZGVzY3JpcHRpb24pO1xuICAgICAgICBuZXdOb2RlLnByZXBlbmQoJChgPHNwYW4gY2xhc3M9XCJlbWJlZGRpbmctaWRcIj4oJHtlbWJlZGRpbmcuaWR9KTwvc3Bhbj5gKSk7XG5cbiAgICAgICAgbGV0IHRyYWluQnV0dG9uID0gJCgnPGEgaHJlZj1cIiNcIiBjbGFzcz1cImVtYmVkZGluZy1hY3Rpb24gZW1iZWRkaW5nLXRyYWluXCI+VHJhaW48L2E+JylcbiAgICAgICAgdHJhaW5CdXR0b24uY2xpY2soZSA9PiB7XG4gICAgICAgICAgZS5wcmV2ZW50RGVmYXVsdCgpO1xuICAgICAgICAgICQucG9zdChgJHtBUElfRE9NQUlOfS9hcGkvZW1iZWRkaW5nLyR7ZW1iZWRkaW5nLmlkfS90cmFpbi1zdGFydGApXG4gICAgICAgIH0pO1xuICAgICAgICBuZXdOb2RlLmFwcGVuZCh0cmFpbkJ1dHRvbik7XG5cbiAgICAgICAgbm90VHJhaW5lZE5vZGUuYXBwZW5kKG5ld05vZGUpO1xuICAgICAgfVxuICAgICAgJCgnLmVtYmVkZGluZy1saXN0JykuYXBwZW5kKG5vdFRyYWluZWROb2RlKTtcbiAgICB9XG4gIH0pO1xufVxuXG5cbmZ1bmN0aW9uIHVwZGF0ZUNvdW50ZXIoKSB7XG4gIHJldHVybiAkLmdldChgJHtBUElfRE9NQUlOfS9hcGkvZGFzaGJvYXJkL3dvcmQtY291bnRgKS50aGVuKGRhdGEgPT4ge1xuICAgICQoJyNjb3JwdXMtc2l6ZScpLnRleHQoZm9ybWF0TnVtYmVyKGRhdGEud29yZF9jb3VudCkpO1xuICB9KTtcbn1cblxuXG5mdW5jdGlvbiBydW5BbmRSZXBlYXQoZnVuYywgaW50ZXJ2YWwpIHtcbiAgZnVuYygpLnRoZW4oKCkgPT4gd2luZG93LnNldEludGVydmFsKGZ1bmMsIGludGVydmFsKSk7XG59XG5cblxuJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24gKCkge1xuICBydW5BbmRSZXBlYXQodXBkYXRlQ291bnRlciwgMTAwMCk7XG4gIHJ1bkFuZFJlcGVhdChkaXNwbGF5RW1iZWRkaW5ncywgMTAwMCk7XG4gIGRyYXdDaGFydHMoKTtcbn0pO1xuIiwiZXhwb3J0IGZ1bmN0aW9uIGZvcm1hdE51bWJlcihudW1iZXIpIHtcbiAgcmV0dXJuIG51bWJlci50b1N0cmluZygpLnJlcGxhY2UoL1xcQig/PShcXGR7M30pKyg/IVxcZCkpL2csIFwiLFwiKTtcbn1cblxuXG5leHBvcnQgZnVuY3Rpb24gaHVtYW5pemVOdW1iZXIobnVtYmVyKSB7XG4gIHZhciBtaWxsaW9ucyA9IE1hdGgucm91bmQobnVtYmVyIC8gMTAwMDAwMCk7XG4gIHZhciBmb3JtYXR0ZWQgPSBtaWxsaW9ucy50b1N0cmluZygpLnJlcGxhY2UoLyhcXGQpKD89KFxcZHszfSkrJCkvZywgJyQxLicpICsgXCJNXCI7XG4gIHJldHVybiBmb3JtYXR0ZWQ7XG59XG4iXX0=
