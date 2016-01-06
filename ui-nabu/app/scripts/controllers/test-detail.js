(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TestDetailCtrl
 * @description
 * # TestDetailCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('TestDetailCtrl', function ($scope, $state, TestSets, testset) {
    $scope.testSet = testset;
    console.log($scope.testSet);
  });
})(angular);
