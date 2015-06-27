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
    return (0, _utils.formatNumber)(d.value);
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

var API_DOMAIN = 'http://localhost:5000';

function drawCharts() {
  var totalsCall = $.get(API_DOMAIN + '/api/dashboard/totals');
  var overTimeCall = $.get(API_DOMAIN + '/api/dashboard/over-time');

  totalsCall.done(function (data) {
    var wordsPerSource = data.data;
    $('#corpus-size').text((0, _utils.formatNumber)((0, _utils.totalWords)(wordsPerSource)));
    (0, _charts.countHistogram)(wordsPerSource);
  });

  // TODO: Probably shouldn't require the first call to be ready, but need to
  // fix layout.
  $.when(totalsCall, overTimeCall).done(function (_, deferredResult) {
    var wordsPerDay = deferredResult[0].data;
    (0, _charts.activityCharts)(wordsPerDay);
  });
}

$(document).ready(function () {
  return drawCharts();
});

},{"./charts":1,"./utils":3}],3:[function(require,module,exports){
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.totalWords = totalWords;
exports.formatNumber = formatNumber;

function totalWords(wordsPerSource) {
  var total = 0;
  wordsPerSource.forEach(function (source) {
    return total += source.value;
  });
  return total;
}

function formatNumber(number) {
  var millions = Math.round(number / 1000000);
  var formatted = millions.toString().replace(/(\d)(?=(\d{3})+$)/g, "$1.") + "M";
  return formatted;
}

},{}]},{},[2])
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvY2hhcnRzLmpzIiwiL2hvbWUvYWd1c3Rpbi9wcm95L2NvZGUvZnJvbnRlbmQvc3JjL2pzL21haW4uanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7OztRQ0lnQixjQUFjLEdBQWQsY0FBYztRQTZCZCxjQUFjLEdBQWQsY0FBYzs7cUJBakNTLFNBQVM7Ozs7QUFJekMsU0FBUyxjQUFjLENBQUMsY0FBYyxFQUFFO0FBQzdDLGdCQUFjLENBQUMsSUFBSSxDQUFDLFVBQUMsQ0FBQyxFQUFFLENBQUM7V0FBSyxDQUFDLENBQUMsS0FBSyxHQUFHLENBQUMsQ0FBQyxLQUFLO0dBQUEsQ0FBQyxDQUFDOztBQUVqRCxNQUFJLEtBQUssR0FBRyxFQUFFLENBQUMsS0FBSyxDQUFDLE1BQU0sRUFBRSxDQUN4QixNQUFNLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLEdBQUcsQ0FBQyxjQUFjLEVBQUUsVUFBQSxDQUFDO1dBQUksQ0FBQyxDQUFDLEtBQUs7R0FBQSxDQUFDLENBQUMsQ0FBQyxDQUNqRCxLQUFLLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLENBQUMsQ0FBQzs7QUFFcEIsTUFBSSxTQUFTLEdBQUcsRUFBRSxDQUFDLE1BQU0sQ0FBQyxjQUFjLENBQUMsQ0FDdEMsU0FBUyxDQUFDLGVBQWUsQ0FBQyxDQUN4QixJQUFJLENBQUMsY0FBYyxDQUFDLENBQ3RCLEtBQUssRUFBRSxDQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUMsQ0FDbkIsSUFBSSxDQUFDLE9BQU8sRUFBRSxjQUFjLENBQUMsQ0FDN0IsSUFBSSxDQUFDLGFBQWEsRUFBRSxVQUFBLENBQUM7V0FB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LFFBQVEsQ0FBQyxDQUFDLEtBQUssQ0FBQztTQUFNLFVBQVUsRUFBRTtDQUFBLENBQUMsQ0FBQzs7Ozs7Ozs7UUMxQnRCLFVBQVUsR0FBVixVQUFVO1FBT1YsWUFBWSxHQUFaLFlBQVk7O0FBUHJCLFNBQVMsVUFBVSxDQUFDLGNBQWMsRUFBRTtBQUN6QyxNQUFJLEtBQUssR0FBRyxDQUFDLENBQUM7QUFDZCxnQkFBYyxDQUFDLE9BQU8sQ0FBQyxVQUFBLE1BQU07V0FBSSxLQUFLLElBQUksTUFBTSxDQUFDLEtBQUs7R0FBQSxDQUFDLENBQUM7QUFDeEQsU0FBTyxLQUFLLENBQUM7Q0FDZDs7QUFHTSxTQUFTLFlBQVksQ0FBQyxNQUFNLEVBQUU7QUFDbkMsTUFBSSxRQUFRLEdBQUcsSUFBSSxDQUFDLEtBQUssQ0FBQyxNQUFNLEdBQUcsT0FBTyxDQUFDLENBQUM7QUFDNUMsTUFBSSxTQUFTLEdBQUcsUUFBUSxDQUFDLFFBQVEsRUFBRSxDQUFDLE9BQU8sQ0FBQyxvQkFBb0IsRUFBRSxLQUFLLENBQUMsR0FBRyxHQUFHLENBQUM7QUFDL0UsU0FBTyxTQUFTLENBQUM7Q0FDbEIiLCJmaWxlIjoiZ2VuZXJhdGVkLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXNDb250ZW50IjpbIihmdW5jdGlvbiBlKHQsbixyKXtmdW5jdGlvbiBzKG8sdSl7aWYoIW5bb10pe2lmKCF0W29dKXt2YXIgYT10eXBlb2YgcmVxdWlyZT09XCJmdW5jdGlvblwiJiZyZXF1aXJlO2lmKCF1JiZhKXJldHVybiBhKG8sITApO2lmKGkpcmV0dXJuIGkobywhMCk7dmFyIGY9bmV3IEVycm9yKFwiQ2Fubm90IGZpbmQgbW9kdWxlICdcIitvK1wiJ1wiKTt0aHJvdyBmLmNvZGU9XCJNT0RVTEVfTk9UX0ZPVU5EXCIsZn12YXIgbD1uW29dPXtleHBvcnRzOnt9fTt0W29dWzBdLmNhbGwobC5leHBvcnRzLGZ1bmN0aW9uKGUpe3ZhciBuPXRbb11bMV1bZV07cmV0dXJuIHMobj9uOmUpfSxsLGwuZXhwb3J0cyxlLHQsbixyKX1yZXR1cm4gbltvXS5leHBvcnRzfXZhciBpPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7Zm9yKHZhciBvPTA7bzxyLmxlbmd0aDtvKyspcyhyW29dKTtyZXR1cm4gc30pIiwiaW1wb3J0IHt0b3RhbFdvcmRzLCBmb3JtYXROdW1iZXJ9IGZyb20gJy4vdXRpbHMnO1xuXG5cbi8qIENyZWF0ZXMgdGhlIGhpc3RvZ3JhbSBjaGFydCB3aXRoIHRoZSBjb3VudHMgcGVyIHNvdXJjZS4gKi9cbmV4cG9ydCBmdW5jdGlvbiBjb3VudEhpc3RvZ3JhbSh3b3Jkc1BlclNvdXJjZSkge1xuICB3b3Jkc1BlclNvdXJjZS5zb3J0KChhLCBiKSA9PiBhLnZhbHVlIDwgYi52YWx1ZSk7XG5cbiAgbGV0IHNjYWxlID0gZDMuc2NhbGUubGluZWFyKClcbiAgICAgIC5kb21haW4oWzAsIGQzLm1heCh3b3Jkc1BlclNvdXJjZSwgZCA9PiBkLnZhbHVlKV0pXG4gICAgICAucmFuZ2UoWzAsIDgwXSk7XG5cbiAgbGV0IGNvbnRhaW5lciA9IGQzLnNlbGVjdCgnLnNvdXJjZS1saXN0JylcbiAgICAuc2VsZWN0QWxsKCcuc291cmNlLWVudHJ5JylcbiAgICAgIC5kYXRhKHdvcmRzUGVyU291cmNlKVxuICAgIC5lbnRlcigpLmFwcGVuZCgnZGl2JylcbiAgICAgIC5hdHRyKCdjbGFzcycsICdzb3VyY2UtZW50cnknKVxuICAgICAgLmF0dHIoJ2RhdGEtc291cmNlJywgZCA9PiBkLnNvdXJjZSlcbiAgICAuYXBwZW5kKCdkaXYnKVxuICAgICAgLmF0dHIoJ2NsYXNzJywgJ2Jhci1jb250YWluZXInKTtcblxuICBjb250YWluZXIuYXBwZW5kKCdkaXYnKVxuICAgICAgLmF0dHIoJ2NsYXNzJywgKGQsIGlkeCkgPT4gYGJhciBiYXItJHtpZHggJSA1ICsgMX1gKVxuICAgICAgLmF0dHIoJ3RpdGxlJywgZCA9PiBkLnNvdXJjZSlcbiAgICAgIC50ZXh0KGQgPT4gZC5zb3VyY2UpXG4gICAgICAuc3R5bGUoJ3dpZHRoJywgZCA9PiBzY2FsZShkLnZhbHVlKSArICclJyk7XG5cbiAgY29udGFpbmVyLmFwcGVuZCgnZGl2JylcbiAgICAgIC5hdHRyKCdjbGFzcycsICdiYXItdmFsdWUnKVxuICAgICAgLnRleHQoZCA9PiBmb3JtYXROdW1iZXIoZC52YWx1ZSkpO1xufVxuXG5cbi8qIENyZWF0ZXMgdGhlIGFjdGl2aXR5IGNoYXJ0cyBmb3IgZWFjaCBzb3VyY2UuICovXG5leHBvcnQgZnVuY3Rpb24gYWN0aXZpdHlDaGFydHMod29yZHNQZXJEYXkpIHtcbiAgbGV0IHdpZHRoID0gNzA7XG4gIGxldCBoZWlnaHQgPSAyODtcblxuICBmb3IgKGxldCBzb3VyY2VEYXRhIG9mIHdvcmRzUGVyRGF5KSB7XG4gICAgbGV0IHNvdXJjZSA9IHNvdXJjZURhdGEudmFsdWU7XG5cbiAgICBsZXQgc3ZnID0gZDMuc2VsZWN0KCcuc291cmNlLWVudHJ5W2RhdGEtc291cmNlPVwiJyArIHNvdXJjZURhdGEuc291cmNlICsgJ1wiXScpXG4gICAgICAuaW5zZXJ0KCdkaXYnLCAnZGl2JylcbiAgICAgICAgLmF0dHIoJ2NsYXNzJywgJ292ZXItdGltZS1jaGFydCcpXG4gICAgICAuYXBwZW5kKCdzdmcnKVxuICAgICAgICAuYXR0cignY2xhc3MnLCAnY2hhcnQnKVxuICAgICAgICAuYXR0cignd2lkdGgnLCB3aWR0aClcbiAgICAgICAgLmF0dHIoJ2hlaWdodCcsIGhlaWdodCk7XG5cbiAgICBsZXQgeCA9IGQzLnNjYWxlLm9yZGluYWwoKVxuICAgICAgICAuZG9tYWluKHNvdXJjZS5tYXAoZCA9PiBkLmRheSkpXG4gICAgICAgIC5yYW5nZVJvdW5kQmFuZHMoWzAsIHdpZHRoXSk7XG5cbiAgICBsZXQgeSA9IGQzLnNjYWxlLmxpbmVhcigpXG4gICAgICAgIC5kb21haW4oWzAsIGQzLm1heChzb3VyY2UubWFwKGQgPT4gZC52YWx1ZSkpXSlcbiAgICAgICAgLnJhbmdlKFtoZWlnaHQsIDBdKTtcblxuICAgIHN2Zy5zZWxlY3RBbGwoJy5iYXInKVxuICAgICAgICAuZGF0YShzb3VyY2UpXG4gICAgLmVudGVyKCkuYXBwZW5kKCdyZWN0JylcbiAgICAgICAgLmF0dHIoJ2NsYXNzJywgJ2JhcicpXG4gICAgICAgIC5hdHRyKCd4JywgZCA9PiB4KGQuZGF5KSlcbiAgICAgICAgLmF0dHIoJ3knLCBoZWlnaHQpXG4gICAgICAgIC5hdHRyKCd3aWR0aCcsIHgucmFuZ2VCYW5kKCkpXG4gICAgICAgIC5hdHRyKCdoZWlnaHQnLCBkID0+IGhlaWdodCAtIHkoZC52YWx1ZSkpXG4gICAgICAudHJhbnNpdGlvbigpXG4gICAgICAgIC5kdXJhdGlvbigyMDAwKVxuICAgICAgICAuYXR0cigneScsIGQgPT4geShkLnZhbHVlKSk7XG4gIH1cbn1cbiIsImltcG9ydCB7dG90YWxXb3JkcywgZm9ybWF0TnVtYmVyfSBmcm9tICcuL3V0aWxzJztcbmltcG9ydCB7Y291bnRIaXN0b2dyYW0sIGFjdGl2aXR5Q2hhcnRzfSBmcm9tICcuL2NoYXJ0cyc7XG5cblxuY29uc3QgQVBJX0RPTUFJTiA9ICdodHRwOi8vbG9jYWxob3N0OjUwMDAnXG5cblxuZnVuY3Rpb24gZHJhd0NoYXJ0cygpIHtcbiAgbGV0IHRvdGFsc0NhbGwgPSAkLmdldChgJHtBUElfRE9NQUlOfS9hcGkvZGFzaGJvYXJkL3RvdGFsc2ApO1xuICBsZXQgb3ZlclRpbWVDYWxsID0gJC5nZXQoYCR7QVBJX0RPTUFJTn0vYXBpL2Rhc2hib2FyZC9vdmVyLXRpbWVgKTtcblxuICB0b3RhbHNDYWxsLmRvbmUoZGF0YSA9PiB7XG4gICAgbGV0IHdvcmRzUGVyU291cmNlID0gZGF0YS5kYXRhO1xuICAgICQoJyNjb3JwdXMtc2l6ZScpLnRleHQoZm9ybWF0TnVtYmVyKHRvdGFsV29yZHMod29yZHNQZXJTb3VyY2UpKSk7XG4gICAgY291bnRIaXN0b2dyYW0od29yZHNQZXJTb3VyY2UpO1xuICB9KTtcblxuICAvLyBUT0RPOiBQcm9iYWJseSBzaG91bGRuJ3QgcmVxdWlyZSB0aGUgZmlyc3QgY2FsbCB0byBiZSByZWFkeSwgYnV0IG5lZWQgdG9cbiAgLy8gZml4IGxheW91dC5cbiAgJC53aGVuKHRvdGFsc0NhbGwsIG92ZXJUaW1lQ2FsbCkuZG9uZSgoXywgZGVmZXJyZWRSZXN1bHQpID0+IHtcbiAgICBsZXQgd29yZHNQZXJEYXkgPSBkZWZlcnJlZFJlc3VsdFswXS5kYXRhO1xuICAgIGFjdGl2aXR5Q2hhcnRzKHdvcmRzUGVyRGF5KTtcbiAgfSk7XG59XG5cblxuJChkb2N1bWVudCkucmVhZHkoKCkgPT4gZHJhd0NoYXJ0cygpKTtcbiIsImV4cG9ydCBmdW5jdGlvbiB0b3RhbFdvcmRzKHdvcmRzUGVyU291cmNlKSB7XG4gIHZhciB0b3RhbCA9IDA7XG4gIHdvcmRzUGVyU291cmNlLmZvckVhY2goc291cmNlID0+IHRvdGFsICs9IHNvdXJjZS52YWx1ZSk7XG4gIHJldHVybiB0b3RhbDtcbn1cblxuXG5leHBvcnQgZnVuY3Rpb24gZm9ybWF0TnVtYmVyKG51bWJlcikge1xuICB2YXIgbWlsbGlvbnMgPSBNYXRoLnJvdW5kKG51bWJlciAvIDEwMDAwMDApO1xuICB2YXIgZm9ybWF0dGVkID0gbWlsbGlvbnMudG9TdHJpbmcoKS5yZXBsYWNlKC8oXFxkKSg/PShcXGR7M30pKyQpL2csICckMS4nKSArIFwiTVwiO1xuICByZXR1cm4gZm9ybWF0dGVkO1xufVxuIl19
