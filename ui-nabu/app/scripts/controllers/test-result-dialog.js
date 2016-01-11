(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TestResultDialogCtrl
 * @description
 * # TestResultDialogCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('TestResultDialogCtrl', function ($scope, $mdDialog, resultData, embedding, test) {
    $scope.resultData = resultData;
    $scope.embedding = embedding;
    $scope.test = test;

    $scope.cancel = function() {
        $mdDialog.cancel();
    };
  });
})(angular);
