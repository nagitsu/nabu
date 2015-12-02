(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TestsCtrl
 * @description
 * # TestsCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('TestsCtrl', function ($scope, testsList) {
    $scope.tests = testsList;
  });
})(angular);
