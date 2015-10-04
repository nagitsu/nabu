'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:CorpusCtrl
 * @description
 * # CorpusCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('CorpusCtrl', function ($scope) {
    $scope.query = {
        page: 1,
        limit: 10
    };
    $scope.results = {
        meta: {
            total: 10,
        },
        data: [
            {
                text: "Cosa muy cososa",
                source: "180.com.uy"
            },
            {
                text: "Otro",
                source: "180.com.uy"
            },
            {
                text: "Tres",
                source: "180.com.uy"
            },
            {
                text: "Cuatro",
                source: "180.com.uy"
            }
        ]
    };
  });
