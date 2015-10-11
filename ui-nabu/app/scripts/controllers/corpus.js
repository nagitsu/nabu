'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:CorpusCtrl
 * @description
 * # CorpusCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('CorpusCtrl', function ($scope, Corpus) {
    $scope.query = {
        page: 1,
        limit: 25 // This is hard-coded in the server
    };

    $scope.basicQuery = {
        'query': {
            'match' : {
                'content' : ''
            }
        }
    };

    $scope.search = function () {
        Corpus.search($scope.basicQuery).then(function(results){
            $scope.query.page = 1;
            $scope.results = results;
        });
    };

    $scope.onPaginationChange = function (page, limit) {
        var offset = (page - 1) * $scope.query.limit;
        Corpus.search($scope.basicQuery, offset).then(function(results){
            $scope.results = results;
        });
    };
  });
