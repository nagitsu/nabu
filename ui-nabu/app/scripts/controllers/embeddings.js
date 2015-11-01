(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:EmbeddingsCtrl
 * @description
 * # EmbeddingsCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('EmbeddingsCtrl', function ($scope, Embeddings, embeddingList) {
    $scope.embeddings = embeddingList;
  });
})(angular);
