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

    if (notTrained.length > 0) {
      var notTrainedNode = $('<div class="embedding-group not-trained">' + '<div class="embedding-group-header">Not trained yet</div>' + '</div>');
      var _iteratorNormalCompletion4 = true;
      var _didIteratorError4 = false;
      var _iteratorError4 = undefined;

      try {
        var _loop3 = function () {
          var embedding = _step4.value;

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

        for (var _iterator4 = notTrained[Symbol.iterator](), _step4; !(_iteratorNormalCompletion4 = (_step4 = _iterator4.next()).done); _iteratorNormalCompletion4 = true) {
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
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvY2hhcnRzLmpzIiwiL2hvbWUvYWd1c3Rpbi9wcm95L2NvZGUvZnJvbnRlbmQvc3JjL2pzL21haW4uanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7OztRQ0lnQixjQUFjLEdBQWQsY0FBYztRQTZCZCxjQUFjLEdBQWQsY0FBYzs7cUJBakNELFNBQVM7Ozs7QUFJL0IsU0FBUyxjQUFjLENBQUMsY0FBYyxFQUFFO0FBQzdDLGdCQUFjLENBQUMsSUFBSSxDQUFDLFVBQUMsQ0FBQyxFQUFFLENBQUM7V0FBSyxDQUFDLENBQUMsS0FBSyxHQUFHLENBQUMsQ0FBQyxLQUFLO0dBQUEsQ0FBQyxDQUFDOztBQUVqRCxNQUFJLEtBQUssR0FBRyxFQUFFLENBQUMsS0FBSyxDQUFDLE1BQU0sRUFBRSxDQUN4QixNQUFNLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLEdBQUcsQ0FBQyxjQUFjLEVBQUUsVUFBQSxDQUFDO1dBQUksQ0FBQyxDQUFDLEtBQUs7R0FBQSxDQUFDLENBQUMsQ0FBQyxDQUNqRCxLQUFLLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLENBQUMsQ0FBQzs7QUFFcEIsTUFBSSxTQUFTLEdBQUcsRUFBRSxDQUFDLE1BQU0sQ0FBQyxjQUFjLENBQUMsQ0FDdEMsU0FBUyxDQUFDLGVBQWUsQ0FBQyxDQUN4QixJQUFJLENBQUMsY0FBYyxDQUFDLENBQ3RCLEtBQUssRUFBRSxDQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUMsQ0FDbkIsSUFBSSxDQUFDLE9BQU8sRUFBRSxjQUFjLENBQUMsQ0FDN0IsSUFBSSxDQUFDLGFBQWEsRUFBRSxVQUFBLENBQUM7V0FB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RSxJQUFJLENBQUMsQ0FBQztBQUN0QyxZQUFVLEVBQUUsQ0FBQztDQUNkLENBQUMsQ0FBQzs7Ozs7Ozs7UUM1SWEsWUFBWSxHQUFaLFlBQVk7UUFLWixjQUFjLEdBQWQsY0FBYzs7QUFMdkIsU0FBUyxZQUFZLENBQUMsTUFBTSxFQUFFO0FBQ25DLFNBQU8sTUFBTSxDQUFDLFFBQVEsRUFBRSxDQUFDLE9BQU8sQ0FBQyx1QkFBdUIsRUFBRSxHQUFHLENBQUMsQ0FBQztDQUNoRTs7QUFHTSxTQUFTLGNBQWMsQ0FBQyxNQUFNLEVBQUU7QUFDckMsTUFBSSxRQUFRLEdBQUcsSUFBSSxDQUFDLEtBQUssQ0FBQyxNQUFNLEdBQUcsT0FBTyxDQUFDLENBQUM7QUFDNUMsTUFBSSxTQUFTLEdBQUcsUUFBUSxDQUFDLFFBQVEsRUFBRSxDQUFDLE9BQU8sQ0FBQyxvQkFBb0IsRUFBRSxLQUFLLENBQUMsR0FBRyxHQUFHLENBQUM7QUFDL0UsU0FBTyxTQUFTLENBQUM7Q0FDbEIiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiaW1wb3J0IHtodW1hbml6ZU51bWJlcn0gZnJvbSAnLi91dGlscyc7XG5cblxuLyogQ3JlYXRlcyB0aGUgaGlzdG9ncmFtIGNoYXJ0IHdpdGggdGhlIGNvdW50cyBwZXIgc291cmNlLiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGNvdW50SGlzdG9ncmFtKHdvcmRzUGVyU291cmNlKSB7XG4gIHdvcmRzUGVyU291cmNlLnNvcnQoKGEsIGIpID0+IGEudmFsdWUgPCBiLnZhbHVlKTtcblxuICBsZXQgc2NhbGUgPSBkMy5zY2FsZS5saW5lYXIoKVxuICAgICAgLmRvbWFpbihbMCwgZDMubWF4KHdvcmRzUGVyU291cmNlLCBkID0+IGQudmFsdWUpXSlcbiAgICAgIC5yYW5nZShbMCwgODBdKTtcblxuICBsZXQgY29udGFpbmVyID0gZDMuc2VsZWN0KCcuc291cmNlLWxpc3QnKVxuICAgIC5zZWxlY3RBbGwoJy5zb3VyY2UtZW50cnknKVxuICAgICAgLmRhdGEod29yZHNQZXJTb3VyY2UpXG4gICAgLmVudGVyKCkuYXBwZW5kKCdkaXYnKVxuICAgICAgLmF0dHIoJ2NsYXNzJywgJ3NvdXJjZS1lbnRyeScpXG4gICAgICAuYXR0cignZGF0YS1zb3VyY2UnLCBkID0+IGQuc291cmNlKVxuICAgIC5hcHBlbmQoJ2RpdicpXG4gICAgICAuYXR0cignY2xhc3MnLCAnYmFyLWNvbnRhaW5lcicpO1xuXG4gIGNvbnRhaW5lci5hcHBlbmQoJ2RpdicpXG4gICAgICAuYXR0cignY2xhc3MnLCAoZCwgaWR4KSA9PiBgYmFyIGJhci0ke2lkeCAlIDUgKyAxfWApXG4gICAgICAuYXR0cigndGl0bGUnLCBkID0+IGQuc291cmNlKVxuICAgICAgLnRleHQoZCA9PiBkLnNvdXJjZSlcbiAgICAgIC5zdHlsZSgnd2lkdGgnLCBkID0+IHNjYWxlKGQudmFsdWUpICsgJyUnKTtcblxuICBjb250YWluZXIuYXBwZW5kKCdkaXYnKVxuICAgICAgLmF0dHIoJ2NsYXNzJywgJ2Jhci12YWx1ZScpXG4gICAgICAudGV4dChkID0+IGh1bWFuaXplTnVtYmVyKGQudmFsdWUpKTtcbn1cblxuXG4vKiBDcmVhdGVzIHRoZSBhY3Rpdml0eSBjaGFydHMgZm9yIGVhY2ggc291cmNlLiAqL1xuZXhwb3J0IGZ1bmN0aW9uIGFjdGl2aXR5Q2hhcnRzKHdvcmRzUGVyRGF5KSB7XG4gIGxldCB3aWR0aCA9IDcwO1xuICBsZXQgaGVpZ2h0ID0gMjg7XG5cbiAgZm9yIChsZXQgc291cmNlRGF0YSBvZiB3b3Jkc1BlckRheSkge1xuICAgIGxldCBzb3VyY2UgPSBzb3VyY2VEYXRhLnZhbHVlO1xuXG4gICAgbGV0IHN2ZyA9IGQzLnNlbGVjdCgnLnNvdXJjZS1lbnRyeVtkYXRhLXNvdXJjZT1cIicgKyBzb3VyY2VEYXRhLnNvdXJjZSArICdcIl0nKVxuICAgICAgLmluc2VydCgnZGl2JywgJ2RpdicpXG4gICAgICAgIC5hdHRyKCdjbGFzcycsICdvdmVyLXRpbWUtY2hhcnQnKVxuICAgICAgLmFwcGVuZCgnc3ZnJylcbiAgICAgICAgLmF0dHIoJ2NsYXNzJywgJ2NoYXJ0JylcbiAgICAgICAgLmF0dHIoJ3dpZHRoJywgd2lkdGgpXG4gICAgICAgIC5hdHRyKCdoZWlnaHQnLCBoZWlnaHQpO1xuXG4gICAgbGV0IHggPSBkMy5zY2FsZS5vcmRpbmFsKClcbiAgICAgICAgLmRvbWFpbihzb3VyY2UubWFwKGQgPT4gZC5kYXkpKVxuICAgICAgICAucmFuZ2VSb3VuZEJhbmRzKFswLCB3aWR0aF0pO1xuXG4gICAgbGV0IHkgPSBkMy5zY2FsZS5saW5lYXIoKVxuICAgICAgICAuZG9tYWluKFswLCBkMy5tYXgoc291cmNlLm1hcChkID0+IGQudmFsdWUpKV0pXG4gICAgICAgIC5yYW5nZShbaGVpZ2h0LCAwXSk7XG5cbiAgICBzdmcuc2VsZWN0QWxsKCcuYmFyJylcbiAgICAgICAgLmRhdGEoc291cmNlKVxuICAgIC5lbnRlcigpLmFwcGVuZCgncmVjdCcpXG4gICAgICAgIC5hdHRyKCdjbGFzcycsICdiYXInKVxuICAgICAgICAuYXR0cigneCcsIGQgPT4geChkLmRheSkpXG4gICAgICAgIC5hdHRyKCd5JywgaGVpZ2h0KVxuICAgICAgICAuYXR0cignd2lkdGgnLCB4LnJhbmdlQmFuZCgpKVxuICAgICAgICAuYXR0cignaGVpZ2h0JywgZCA9PiBoZWlnaHQgLSB5KGQudmFsdWUpKVxuICAgICAgLnRyYW5zaXRpb24oKVxuICAgICAgICAuZHVyYXRpb24oMjAwMClcbiAgICAgICAgLmF0dHIoJ3knLCBkID0+IHkoZC52YWx1ZSkpO1xuICB9XG59XG4iLCJpbXBvcnQge2Zvcm1hdE51bWJlcn0gZnJvbSAnLi91dGlscyc7XG5pbXBvcnQge2NvdW50SGlzdG9ncmFtLCBhY3Rpdml0eUNoYXJ0c30gZnJvbSAnLi9jaGFydHMnO1xuXG5cbmNvbnN0IEFQSV9ET01BSU4gPSAnaHR0cDovL2dvbGJhdC55ZG5zLmV1JztcblxuXG5mdW5jdGlvbiBkcmF3Q2hhcnRzKCkge1xuICBsZXQgdG90YWxzQ2FsbCA9ICQuZ2V0KGAke0FQSV9ET01BSU59L2FwaS9kYXNoYm9hcmQvdG90YWxzYCk7XG4gIGxldCBvdmVyVGltZUNhbGwgPSAkLmdldChgJHtBUElfRE9NQUlOfS9hcGkvZGFzaGJvYXJkL292ZXItdGltZWApO1xuXG4gIHRvdGFsc0NhbGwuZG9uZShkYXRhID0+IGNvdW50SGlzdG9ncmFtKGRhdGEuZGF0YSkpO1xuXG4gIC8vIFRPRE86IFByb2JhYmx5IHNob3VsZG4ndCByZXF1aXJlIHRoZSBmaXJzdCBjYWxsIHRvIGJlIHJlYWR5LCBidXQgbmVlZCB0b1xuICAvLyBmaXggbGF5b3V0LlxuICAkLndoZW4odG90YWxzQ2FsbCwgb3ZlclRpbWVDYWxsKS5kb25lKChfLCBkZWZlcnJlZFJlc3VsdCkgPT4ge1xuICAgIGxldCB3b3Jkc1BlckRheSA9IGRlZmVycmVkUmVzdWx0WzBdLmRhdGE7XG4gICAgYWN0aXZpdHlDaGFydHMod29yZHNQZXJEYXkpO1xuICB9KTtcbn1cblxuXG5mdW5jdGlvbiBkaXNwbGF5RW1iZWRkaW5ncygpIHtcbiAgcmV0dXJuICQuZ2V0KGAke0FQSV9ET01BSU59L2FwaS9lbWJlZGRpbmdgKS50aGVuKGRhdGEgPT4ge1xuICAgIC8vIEVtcHR5IHRoZSBlbWJlZGRpbmcgbGlzdC5cbiAgICAkKCcuZW1iZWRkaW5nLWxpc3QnKS5lbXB0eSgpO1xuICAgIGxldCBlbWJlZGRpbmdzID0gZGF0YS5yZXN1bHQ7XG5cbiAgICBsZXQgdHJhaW5lZCA9IGVtYmVkZGluZ3MuZmlsdGVyKGUgPT4gZS5zdGF0ZSA9PSAnU1VDQ0VTUycpO1xuICAgIGxldCB0cmFpbmluZyA9IGVtYmVkZGluZ3MuZmlsdGVyKGUgPT4gZS5zdGF0ZSA9PSAnUFJPR1JFU1MnKTtcbiAgICBsZXQgd2FpdGluZyA9IGVtYmVkZGluZ3MuZmlsdGVyKGUgPT4gZS5zdGF0ZSA9PSAnUEVORElORycpO1xuICAgIGxldCBub3RUcmFpbmVkID0gZW1iZWRkaW5ncy5maWx0ZXIoZSA9PiBlLnN0YXRlID09ICdOT1RfU1RBUlRFRCcpO1xuXG4gICAgaWYgKHRyYWluZWQubGVuZ3RoID4gMCkge1xuICAgICAgbGV0IHRyYWluZWROb2RlID0gJChcbiAgICAgICAgJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmctZ3JvdXAgdHJhaW5lZFwiPicgK1xuICAgICAgICAgICc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nLWdyb3VwLWhlYWRlclwiPlRyYWluZWQ8L2Rpdj4nICtcbiAgICAgICAgJzwvZGl2PidcbiAgICAgICk7XG4gICAgICBmb3IgKGxldCBlbWJlZGRpbmcgb2YgdHJhaW5lZCkge1xuICAgICAgICBsZXQgbmV3Tm9kZSA9ICQoJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmcgZW1iZWRkaW5nLXN0cmlwZWRcIj48L2Rpdj4nKTtcbiAgICAgICAgbmV3Tm9kZS50ZXh0KGVtYmVkZGluZy5kZXNjcmlwdGlvbik7XG4gICAgICAgIG5ld05vZGUucHJlcGVuZCgkKGA8c3BhbiBjbGFzcz1cImVtYmVkZGluZy1pZFwiPigke2VtYmVkZGluZy5pZH0pPC9zcGFuPmApKTtcbiAgICAgICAgdHJhaW5lZE5vZGUuYXBwZW5kKG5ld05vZGUpO1xuICAgICAgfVxuICAgICAgJCgnLmVtYmVkZGluZy1saXN0JykuYXBwZW5kKHRyYWluZWROb2RlKTtcbiAgICB9XG5cbiAgICBpZiAodHJhaW5pbmcubGVuZ3RoID4gMCkge1xuICAgICAgbGV0IHRyYWluaW5nTm9kZSA9ICQoXG4gICAgICAgICc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nLWdyb3VwIHRyYWluaW5nXCI+JyArXG4gICAgICAgICAgJzxkaXYgY2xhc3M9XCJlbWJlZGRpbmctZ3JvdXAtaGVhZGVyXCI+VHJhaW5pbmc8L2Rpdj4nICtcbiAgICAgICAgJzwvZGl2PidcbiAgICAgICk7XG4gICAgICBmb3IgKGxldCBlbWJlZGRpbmcgb2YgdHJhaW5pbmcpIHtcbiAgICAgICAgbGV0IG5ld05vZGUgPSAkKCc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nIGVtYmVkZGluZy1wcm9ncmVzc1wiPjwvZGl2PicpO1xuXG4gICAgICAgIGxldCBwcm9ncmVzcyA9IChlbWJlZGRpbmcucHJvZ3Jlc3MgKiAxMDApLnRvRml4ZWQoMikgKyBcIiVcIjtcbiAgICAgICAgbmV3Tm9kZS5jc3MoJ2JhY2tncm91bmQtc2l6ZScsIGAke3Byb2dyZXNzfSAxMDAlYCk7XG5cbiAgICAgICAgbmV3Tm9kZS50ZXh0KGAke3Byb2dyZXNzfSAtICR7ZW1iZWRkaW5nLmRlc2NyaXB0aW9ufWApO1xuICAgICAgICBuZXdOb2RlLnByZXBlbmQoJChgPHNwYW4gY2xhc3M9XCJlbWJlZGRpbmctaWRcIj4oJHtlbWJlZGRpbmcuaWR9KTwvc3Bhbj5gKSk7XG5cbiAgICAgICAgbGV0IGNhbmNlbEJ1dHRvbiA9ICQoJzxhIGhyZWY9XCIjXCIgY2xhc3M9XCJlbWJlZGRpbmctYWN0aW9uIGVtYmVkZGluZy1jYW5jZWxcIj5DYW5jZWw8L2E+JylcbiAgICAgICAgY2FuY2VsQnV0dG9uLmNsaWNrKGUgPT4ge1xuICAgICAgICAgIGUucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAkLnBvc3QoYCR7QVBJX0RPTUFJTn0vYXBpL2VtYmVkZGluZy8ke2VtYmVkZGluZy5pZH0vdHJhaW4tY2FuY2VsYClcbiAgICAgICAgfSk7XG4gICAgICAgIG5ld05vZGUuYXBwZW5kKGNhbmNlbEJ1dHRvbik7XG5cbiAgICAgICAgdHJhaW5pbmdOb2RlLmFwcGVuZChuZXdOb2RlKTtcbiAgICAgIH1cbiAgICAgICQoJy5lbWJlZGRpbmctbGlzdCcpLmFwcGVuZCh0cmFpbmluZ05vZGUpO1xuICAgIH1cblxuICAgIGlmICh3YWl0aW5nLmxlbmd0aCA+IDApIHtcbiAgICAgIGxldCB3YWl0aW5nTm9kZSA9ICQoXG4gICAgICAgICc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nLWdyb3VwIHdhaXRpbmdcIj4nICtcbiAgICAgICAgICAnPGRpdiBjbGFzcz1cImVtYmVkZGluZy1ncm91cC1oZWFkZXJcIj5XYWl0aW5nPC9kaXY+JyArXG4gICAgICAgICc8L2Rpdj4nXG4gICAgICApO1xuICAgICAgZm9yIChsZXQgZW1iZWRkaW5nIG9mIHdhaXRpbmcpIHtcbiAgICAgICAgbGV0IG5ld05vZGUgPSAkKCc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nIGVtYmVkZGluZy1zdHJpcGVkXCI+PC9kaXY+Jyk7XG4gICAgICAgIG5ld05vZGUudGV4dChlbWJlZGRpbmcuZGVzY3JpcHRpb24pO1xuICAgICAgICBuZXdOb2RlLnByZXBlbmQoJChgPHNwYW4gY2xhc3M9XCJlbWJlZGRpbmctaWRcIj4oJHtlbWJlZGRpbmcuaWR9KTwvc3Bhbj5gKSk7XG5cbiAgICAgICAgbGV0IGNhbmNlbEJ1dHRvbiA9ICQoJzxhIGhyZWY9XCIjXCIgY2xhc3M9XCJlbWJlZGRpbmctYWN0aW9uIGVtYmVkZGluZy1jYW5jZWxcIj5DYW5jZWw8L2E+JylcbiAgICAgICAgY2FuY2VsQnV0dG9uLmNsaWNrKGUgPT4ge1xuICAgICAgICAgIGUucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAkLnBvc3QoYCR7QVBJX0RPTUFJTn0vYXBpL2VtYmVkZGluZy8ke2VtYmVkZGluZy5pZH0vdHJhaW4tY2FuY2VsYClcbiAgICAgICAgfSk7XG4gICAgICAgIG5ld05vZGUuYXBwZW5kKGNhbmNlbEJ1dHRvbik7XG5cbiAgICAgICAgd2FpdGluZ05vZGUuYXBwZW5kKG5ld05vZGUpO1xuICAgICAgfVxuICAgICAgJCgnLmVtYmVkZGluZy1saXN0JykuYXBwZW5kKHdhaXRpbmdOb2RlKTtcbiAgICB9XG5cbiAgICBpZiAobm90VHJhaW5lZC5sZW5ndGggPiAwKSB7XG4gICAgICBsZXQgbm90VHJhaW5lZE5vZGUgPSAkKFxuICAgICAgICAnPGRpdiBjbGFzcz1cImVtYmVkZGluZy1ncm91cCBub3QtdHJhaW5lZFwiPicgK1xuICAgICAgICAgICc8ZGl2IGNsYXNzPVwiZW1iZWRkaW5nLWdyb3VwLWhlYWRlclwiPk5vdCB0cmFpbmVkIHlldDwvZGl2PicgK1xuICAgICAgICAnPC9kaXY+J1xuICAgICAgKTtcbiAgICAgIGZvciAobGV0IGVtYmVkZGluZyBvZiBub3RUcmFpbmVkKSB7XG4gICAgICAgIGxldCBuZXdOb2RlID0gJCgnPGRpdiBjbGFzcz1cImVtYmVkZGluZyBlbWJlZGRpbmctc3RyaXBlZFwiPjwvZGl2PicpO1xuICAgICAgICBuZXdOb2RlLnRleHQoZW1iZWRkaW5nLmRlc2NyaXB0aW9uKTtcbiAgICAgICAgbmV3Tm9kZS5wcmVwZW5kKCQoYDxzcGFuIGNsYXNzPVwiZW1iZWRkaW5nLWlkXCI+KCR7ZW1iZWRkaW5nLmlkfSk8L3NwYW4+YCkpO1xuXG4gICAgICAgIGxldCB0cmFpbkJ1dHRvbiA9ICQoJzxhIGhyZWY9XCIjXCIgY2xhc3M9XCJlbWJlZGRpbmctYWN0aW9uIGVtYmVkZGluZy10cmFpblwiPlRyYWluPC9hPicpXG4gICAgICAgIHRyYWluQnV0dG9uLmNsaWNrKGUgPT4ge1xuICAgICAgICAgIGUucHJldmVudERlZmF1bHQoKTtcbiAgICAgICAgICAkLnBvc3QoYCR7QVBJX0RPTUFJTn0vYXBpL2VtYmVkZGluZy8ke2VtYmVkZGluZy5pZH0vdHJhaW4tc3RhcnRgKVxuICAgICAgICB9KTtcbiAgICAgICAgbmV3Tm9kZS5hcHBlbmQodHJhaW5CdXR0b24pO1xuXG4gICAgICAgIG5vdFRyYWluZWROb2RlLmFwcGVuZChuZXdOb2RlKTtcbiAgICAgIH1cbiAgICAgICQoJy5lbWJlZGRpbmctbGlzdCcpLmFwcGVuZChub3RUcmFpbmVkTm9kZSk7XG4gICAgfVxuICB9KTtcbn1cblxuXG5mdW5jdGlvbiB1cGRhdGVDb3VudGVyKCkge1xuICByZXR1cm4gJC5nZXQoYCR7QVBJX0RPTUFJTn0vYXBpL2Rhc2hib2FyZC93b3JkLWNvdW50YCkudGhlbihkYXRhID0+IHtcbiAgICAkKCcjY29ycHVzLXNpemUnKS50ZXh0KGZvcm1hdE51bWJlcihkYXRhLndvcmRfY291bnQpKTtcbiAgfSk7XG59XG5cblxuZnVuY3Rpb24gcnVuQW5kUmVwZWF0KGZ1bmMsIGludGVydmFsKSB7XG4gIGZ1bmMoKS50aGVuKCgpID0+IHdpbmRvdy5zZXRJbnRlcnZhbChmdW5jLCBpbnRlcnZhbCkpO1xufVxuXG5cbiQoZG9jdW1lbnQpLnJlYWR5KGZ1bmN0aW9uICgpIHtcbiAgcnVuQW5kUmVwZWF0KHVwZGF0ZUNvdW50ZXIsIDEwMDApO1xuICBydW5BbmRSZXBlYXQoZGlzcGxheUVtYmVkZGluZ3MsIDEwMDApO1xuICBkcmF3Q2hhcnRzKCk7XG59KTtcbiIsImV4cG9ydCBmdW5jdGlvbiBmb3JtYXROdW1iZXIobnVtYmVyKSB7XG4gIHJldHVybiBudW1iZXIudG9TdHJpbmcoKS5yZXBsYWNlKC9cXEIoPz0oXFxkezN9KSsoPyFcXGQpKS9nLCBcIixcIik7XG59XG5cblxuZXhwb3J0IGZ1bmN0aW9uIGh1bWFuaXplTnVtYmVyKG51bWJlcikge1xuICB2YXIgbWlsbGlvbnMgPSBNYXRoLnJvdW5kKG51bWJlciAvIDEwMDAwMDApO1xuICB2YXIgZm9ybWF0dGVkID0gbWlsbGlvbnMudG9TdHJpbmcoKS5yZXBsYWNlKC8oXFxkKSg/PShcXGR7M30pKyQpL2csICckMS4nKSArIFwiTVwiO1xuICByZXR1cm4gZm9ybWF0dGVkO1xufVxuIl19
