(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:DashboardCtrl
 * @description
 * # DashboardCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('DashboardCtrl', function ($interval, $scope, Corpus, corpusStats) {
    $scope.corpusStats = mapCorpusStats(corpusStats);
    $scope.corpusSize = corpusStats.size;

    $scope.corpusGraphSeries = ['Scraped items'];
    $scope.corpusGraphLabels = getDateRange(
        moment().subtract(10, 'days'), moment().add(1, 'days'), 'DD/MM'
    );

    // We want some real-time-like behavior here, so we poll the server
    // periodically to show new corpus stats numbers.
    $scope.corpusTimer = $interval(function () {
        Corpus.stats().then(function(response) {
          $scope.corpusStats = mapCorpusStats(response.data);
          $scope.corpusSize = response.data.size;
        });
    }, 10000);

    function mapCorpusStats(stats) {
        var statsMap = {};
        _.forEach(stats.by_source, function(sourceData) {
            statsMap[sourceData.source] = {};
            statsMap[sourceData.source].size = sourceData.size;
        });

        _.forEach(stats.over_time, function(sourceData) {
            statsMap[sourceData.source].over_time = [sourceData.values];
        });

        return statsMap;
    }

    function getDateRange(startDate, endDate, dateFormat) {
        var dates = [],
            end = moment(endDate),
            diff = endDate.diff(startDate, 'days');

        if(!startDate.isValid() || !endDate.isValid() || diff <= 0) {
            return;
        }

        for(var i = 0; i < diff; i++) {
            dates.push(end.subtract(1,'d').format(dateFormat));
        }

        return _.reverse(dates);
    }
  });
})(angular, moment);
