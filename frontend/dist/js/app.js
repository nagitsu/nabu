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

function updateCounter() {
  return $.get(API_DOMAIN + '/api/dashboard/word-count').then(function (data) {
    $('#corpus-size').text((0, _utils.formatNumber)(data.word_count));
  });
}

function setUpCounter() {
  updateCounter().then(function () {
    return window.setInterval(updateCounter, 1000);
  });
}

$(document).ready(function () {
  setUpCounter();
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
//# sourceMappingURL=data:application/json;charset:utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIm5vZGVfbW9kdWxlcy9icm93c2VyaWZ5L25vZGVfbW9kdWxlcy9icm93c2VyLXBhY2svX3ByZWx1ZGUuanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvY2hhcnRzLmpzIiwiL2hvbWUvYWd1c3Rpbi9wcm95L2NvZGUvZnJvbnRlbmQvc3JjL2pzL21haW4uanMiLCIvaG9tZS9hZ3VzdGluL3Byb3kvY29kZS9mcm9udGVuZC9zcmMvanMvdXRpbHMuanMiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7Ozs7OztRQ0lnQixjQUFjLEdBQWQsY0FBYztRQTZCZCxjQUFjLEdBQWQsY0FBYzs7cUJBakNELFNBQVM7Ozs7QUFJL0IsU0FBUyxjQUFjLENBQUMsY0FBYyxFQUFFO0FBQzdDLGdCQUFjLENBQUMsSUFBSSxDQUFDLFVBQUMsQ0FBQyxFQUFFLENBQUM7V0FBSyxDQUFDLENBQUMsS0FBSyxHQUFHLENBQUMsQ0FBQyxLQUFLO0dBQUEsQ0FBQyxDQUFDOztBQUVqRCxNQUFJLEtBQUssR0FBRyxFQUFFLENBQUMsS0FBSyxDQUFDLE1BQU0sRUFBRSxDQUN4QixNQUFNLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLEdBQUcsQ0FBQyxjQUFjLEVBQUUsVUFBQSxDQUFDO1dBQUksQ0FBQyxDQUFDLEtBQUs7R0FBQSxDQUFDLENBQUMsQ0FBQyxDQUNqRCxLQUFLLENBQUMsQ0FBQyxDQUFDLEVBQUUsRUFBRSxDQUFDLENBQUMsQ0FBQzs7QUFFcEIsTUFBSSxTQUFTLEdBQUcsRUFBRSxDQUFDLE1BQU0sQ0FBQyxjQUFjLENBQUMsQ0FDdEMsU0FBUyxDQUFDLGVBQWUsQ0FBQyxDQUN4QixJQUFJLENBQUMsY0FBYyxDQUFDLENBQ3RCLEtBQUssRUFBRSxDQUFDLE1BQU0sQ0FBQyxLQUFLLENBQUMsQ0FDbkIsSUFBSSxDQUFDLE9BQU8sRUFBRSxjQUFjLENBQUMsQ0FDN0IsSUFBSSxDQUFDLGFBQWEsRUFBRSxVQUFBLENBQUM7V0FB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SUFBSSxDQUFDLFVBQVUsQ0FBQyxDQUFDLENBQUM7R0FDdkQsQ0FBQyxDQUFDO0NBQ0o7O0FBR0QsU0FBUyxZQUFZLEdBQUc7QUFDdEIsZUFBYSxFQUFFLENBQUMsSUFBSSxDQUFDO1dBQU0sTUFBTSxDQUFDLFdBQVcsQ0FBQyxhQUFhLEVBQUUsSUFBSSxDQUFDO0dBQUEsQ0FBQyxDQUFDO0NBQ3JFOztBQUdELENBQUMsQ0FBQyxRQUFRLENBQUMsQ0FBQyxLQUFLLENBQUMsWUFBWTtBQUM1QixjQUFZLEVBQUUsQ0FBQztBQUNmLFlBQVUsRUFBRSxDQUFDO0NBQ2QsQ0FBQyxDQUFDOzs7Ozs7OztRQ3JDYSxZQUFZLEdBQVosWUFBWTtRQUtaLGNBQWMsR0FBZCxjQUFjOztBQUx2QixTQUFTLFlBQVksQ0FBQyxNQUFNLEVBQUU7QUFDbkMsU0FBTyxNQUFNLENBQUMsUUFBUSxFQUFFLENBQUMsT0FBTyxDQUFDLHVCQUF1QixFQUFFLEdBQUcsQ0FBQyxDQUFDO0NBQ2hFOztBQUdNLFNBQVMsY0FBYyxDQUFDLE1BQU0sRUFBRTtBQUNyQyxNQUFJLFFBQVEsR0FBRyxJQUFJLENBQUMsS0FBSyxDQUFDLE1BQU0sR0FBRyxPQUFPLENBQUMsQ0FBQztBQUM1QyxNQUFJLFNBQVMsR0FBRyxRQUFRLENBQUMsUUFBUSxFQUFFLENBQUMsT0FBTyxDQUFDLG9CQUFvQixFQUFFLEtBQUssQ0FBQyxHQUFHLEdBQUcsQ0FBQztBQUMvRSxTQUFPLFNBQVMsQ0FBQztDQUNsQiIsImZpbGUiOiJnZW5lcmF0ZWQuanMiLCJzb3VyY2VSb290IjoiIiwic291cmNlc0NvbnRlbnQiOlsiKGZ1bmN0aW9uIGUodCxuLHIpe2Z1bmN0aW9uIHMobyx1KXtpZighbltvXSl7aWYoIXRbb10pe3ZhciBhPXR5cGVvZiByZXF1aXJlPT1cImZ1bmN0aW9uXCImJnJlcXVpcmU7aWYoIXUmJmEpcmV0dXJuIGEobywhMCk7aWYoaSlyZXR1cm4gaShvLCEwKTt2YXIgZj1uZXcgRXJyb3IoXCJDYW5ub3QgZmluZCBtb2R1bGUgJ1wiK28rXCInXCIpO3Rocm93IGYuY29kZT1cIk1PRFVMRV9OT1RfRk9VTkRcIixmfXZhciBsPW5bb109e2V4cG9ydHM6e319O3Rbb11bMF0uY2FsbChsLmV4cG9ydHMsZnVuY3Rpb24oZSl7dmFyIG49dFtvXVsxXVtlXTtyZXR1cm4gcyhuP246ZSl9LGwsbC5leHBvcnRzLGUsdCxuLHIpfXJldHVybiBuW29dLmV4cG9ydHN9dmFyIGk9dHlwZW9mIHJlcXVpcmU9PVwiZnVuY3Rpb25cIiYmcmVxdWlyZTtmb3IodmFyIG89MDtvPHIubGVuZ3RoO28rKylzKHJbb10pO3JldHVybiBzfSkiLCJpbXBvcnQge2h1bWFuaXplTnVtYmVyfSBmcm9tICcuL3V0aWxzJztcblxuXG4vKiBDcmVhdGVzIHRoZSBoaXN0b2dyYW0gY2hhcnQgd2l0aCB0aGUgY291bnRzIHBlciBzb3VyY2UuICovXG5leHBvcnQgZnVuY3Rpb24gY291bnRIaXN0b2dyYW0od29yZHNQZXJTb3VyY2UpIHtcbiAgd29yZHNQZXJTb3VyY2Uuc29ydCgoYSwgYikgPT4gYS52YWx1ZSA8IGIudmFsdWUpO1xuXG4gIGxldCBzY2FsZSA9IGQzLnNjYWxlLmxpbmVhcigpXG4gICAgICAuZG9tYWluKFswLCBkMy5tYXgod29yZHNQZXJTb3VyY2UsIGQgPT4gZC52YWx1ZSldKVxuICAgICAgLnJhbmdlKFswLCA4MF0pO1xuXG4gIGxldCBjb250YWluZXIgPSBkMy5zZWxlY3QoJy5zb3VyY2UtbGlzdCcpXG4gICAgLnNlbGVjdEFsbCgnLnNvdXJjZS1lbnRyeScpXG4gICAgICAuZGF0YSh3b3Jkc1BlclNvdXJjZSlcbiAgICAuZW50ZXIoKS5hcHBlbmQoJ2RpdicpXG4gICAgICAuYXR0cignY2xhc3MnLCAnc291cmNlLWVudHJ5JylcbiAgICAgIC5hdHRyKCdkYXRhLXNvdXJjZScsIGQgPT4gZC5zb3VyY2UpXG4gICAgLmFwcGVuZCgnZGl2JylcbiAgICAgIC5hdHRyKCdjbGFzcycsICdiYXItY29udGFpbmVyJyk7XG5cbiAgY29udGFpbmVyLmFwcGVuZCgnZGl2JylcbiAgICAgIC5hdHRyKCdjbGFzcycsIChkLCBpZHgpID0+IGBiYXIgYmFyLSR7aWR4ICUgNSArIDF9YClcbiAgICAgIC5hdHRyKCd0aXRsZScsIGQgPT4gZC5zb3VyY2UpXG4gICAgICAudGV4dChkID0+IGQuc291cmNlKVxuICAgICAgLnN0eWxlKCd3aWR0aCcsIGQgPT4gc2NhbGUoZC52YWx1ZSkgKyAnJScpO1xuXG4gIGNvbnRhaW5lci5hcHBlbmQoJ2RpdicpXG4gICAgICAuYXR0cignY2xhc3MnLCAnYmFyLXZhbHVlJylcbiAgICAgIC50ZXh0KGQgPT4gaHVtYW5pemVOdW1iZXIoZC52YWx1ZSkpO1xufVxuXG5cbi8qIENyZWF0ZXMgdGhlIGFjdGl2aXR5IGNoYXJ0cyBmb3IgZWFjaCBzb3VyY2UuICovXG5leHBvcnQgZnVuY3Rpb24gYWN0aXZpdHlDaGFydHMod29yZHNQZXJEYXkpIHtcbiAgbGV0IHdpZHRoID0gNzA7XG4gIGxldCBoZWlnaHQgPSAyODtcblxuICBmb3IgKGxldCBzb3VyY2VEYXRhIG9mIHdvcmRzUGVyRGF5KSB7XG4gICAgbGV0IHNvdXJjZSA9IHNvdXJjZURhdGEudmFsdWU7XG5cbiAgICBsZXQgc3ZnID0gZDMuc2VsZWN0KCcuc291cmNlLWVudHJ5W2RhdGEtc291cmNlPVwiJyArIHNvdXJjZURhdGEuc291cmNlICsgJ1wiXScpXG4gICAgICAuaW5zZXJ0KCdkaXYnLCAnZGl2JylcbiAgICAgICAgLmF0dHIoJ2NsYXNzJywgJ292ZXItdGltZS1jaGFydCcpXG4gICAgICAuYXBwZW5kKCdzdmcnKVxuICAgICAgICAuYXR0cignY2xhc3MnLCAnY2hhcnQnKVxuICAgICAgICAuYXR0cignd2lkdGgnLCB3aWR0aClcbiAgICAgICAgLmF0dHIoJ2hlaWdodCcsIGhlaWdodCk7XG5cbiAgICBsZXQgeCA9IGQzLnNjYWxlLm9yZGluYWwoKVxuICAgICAgICAuZG9tYWluKHNvdXJjZS5tYXAoZCA9PiBkLmRheSkpXG4gICAgICAgIC5yYW5nZVJvdW5kQmFuZHMoWzAsIHdpZHRoXSk7XG5cbiAgICBsZXQgeSA9IGQzLnNjYWxlLmxpbmVhcigpXG4gICAgICAgIC5kb21haW4oWzAsIGQzLm1heChzb3VyY2UubWFwKGQgPT4gZC52YWx1ZSkpXSlcbiAgICAgICAgLnJhbmdlKFtoZWlnaHQsIDBdKTtcblxuICAgIHN2Zy5zZWxlY3RBbGwoJy5iYXInKVxuICAgICAgICAuZGF0YShzb3VyY2UpXG4gICAgLmVudGVyKCkuYXBwZW5kKCdyZWN0JylcbiAgICAgICAgLmF0dHIoJ2NsYXNzJywgJ2JhcicpXG4gICAgICAgIC5hdHRyKCd4JywgZCA9PiB4KGQuZGF5KSlcbiAgICAgICAgLmF0dHIoJ3knLCBoZWlnaHQpXG4gICAgICAgIC5hdHRyKCd3aWR0aCcsIHgucmFuZ2VCYW5kKCkpXG4gICAgICAgIC5hdHRyKCdoZWlnaHQnLCBkID0+IGhlaWdodCAtIHkoZC52YWx1ZSkpXG4gICAgICAudHJhbnNpdGlvbigpXG4gICAgICAgIC5kdXJhdGlvbigyMDAwKVxuICAgICAgICAuYXR0cigneScsIGQgPT4geShkLnZhbHVlKSk7XG4gIH1cbn1cbiIsImltcG9ydCB7Zm9ybWF0TnVtYmVyfSBmcm9tICcuL3V0aWxzJztcbmltcG9ydCB7Y291bnRIaXN0b2dyYW0sIGFjdGl2aXR5Q2hhcnRzfSBmcm9tICcuL2NoYXJ0cyc7XG5cblxuY29uc3QgQVBJX0RPTUFJTiA9ICdodHRwOi8vZ29sYmF0LnlkbnMuZXUnO1xuXG5cbmZ1bmN0aW9uIGRyYXdDaGFydHMoKSB7XG4gIGxldCB0b3RhbHNDYWxsID0gJC5nZXQoYCR7QVBJX0RPTUFJTn0vYXBpL2Rhc2hib2FyZC90b3RhbHNgKTtcbiAgbGV0IG92ZXJUaW1lQ2FsbCA9ICQuZ2V0KGAke0FQSV9ET01BSU59L2FwaS9kYXNoYm9hcmQvb3Zlci10aW1lYCk7XG5cbiAgdG90YWxzQ2FsbC5kb25lKGRhdGEgPT4gY291bnRIaXN0b2dyYW0oZGF0YS5kYXRhKSk7XG5cbiAgLy8gVE9ETzogUHJvYmFibHkgc2hvdWxkbid0IHJlcXVpcmUgdGhlIGZpcnN0IGNhbGwgdG8gYmUgcmVhZHksIGJ1dCBuZWVkIHRvXG4gIC8vIGZpeCBsYXlvdXQuXG4gICQud2hlbih0b3RhbHNDYWxsLCBvdmVyVGltZUNhbGwpLmRvbmUoKF8sIGRlZmVycmVkUmVzdWx0KSA9PiB7XG4gICAgbGV0IHdvcmRzUGVyRGF5ID0gZGVmZXJyZWRSZXN1bHRbMF0uZGF0YTtcbiAgICBhY3Rpdml0eUNoYXJ0cyh3b3Jkc1BlckRheSk7XG4gIH0pO1xufVxuXG5cbmZ1bmN0aW9uIHVwZGF0ZUNvdW50ZXIoKSB7XG4gIHJldHVybiAkLmdldChgJHtBUElfRE9NQUlOfS9hcGkvZGFzaGJvYXJkL3dvcmQtY291bnRgKS50aGVuKGRhdGEgPT4ge1xuICAgICQoJyNjb3JwdXMtc2l6ZScpLnRleHQoZm9ybWF0TnVtYmVyKGRhdGEud29yZF9jb3VudCkpO1xuICB9KTtcbn1cblxuXG5mdW5jdGlvbiBzZXRVcENvdW50ZXIoKSB7XG4gIHVwZGF0ZUNvdW50ZXIoKS50aGVuKCgpID0+IHdpbmRvdy5zZXRJbnRlcnZhbCh1cGRhdGVDb3VudGVyLCAxMDAwKSk7XG59XG5cblxuJChkb2N1bWVudCkucmVhZHkoZnVuY3Rpb24gKCkge1xuICBzZXRVcENvdW50ZXIoKTtcbiAgZHJhd0NoYXJ0cygpO1xufSk7XG4iLCJleHBvcnQgZnVuY3Rpb24gZm9ybWF0TnVtYmVyKG51bWJlcikge1xuICByZXR1cm4gbnVtYmVyLnRvU3RyaW5nKCkucmVwbGFjZSgvXFxCKD89KFxcZHszfSkrKD8hXFxkKSkvZywgXCIsXCIpO1xufVxuXG5cbmV4cG9ydCBmdW5jdGlvbiBodW1hbml6ZU51bWJlcihudW1iZXIpIHtcbiAgdmFyIG1pbGxpb25zID0gTWF0aC5yb3VuZChudW1iZXIgLyAxMDAwMDAwKTtcbiAgdmFyIGZvcm1hdHRlZCA9IG1pbGxpb25zLnRvU3RyaW5nKCkucmVwbGFjZSgvKFxcZCkoPz0oXFxkezN9KSskKS9nLCAnJDEuJykgKyBcIk1cIjtcbiAgcmV0dXJuIGZvcm1hdHRlZDtcbn1cbiJdfQ==
