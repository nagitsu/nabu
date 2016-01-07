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
  .controller('TestDetailCtrl', function (
    $scope, $state, VerifyDelete, TestSets, testset
  ) {
    $scope.testSet = testset;

    $scope.updateTestSet = function() {
        // In this case we can only update description and name attributes.
        var editTest = {
            "name": $scope.testSet.name,
            "description": $scope.testSet.description
        };
        TestSets.update($scope.testSet.id, editTest).then(function(test) {
            $scope.testSet = test.data;
        });
    };

    $scope.deleteTestSet = function() {
        var msg = 'Are you sure you want to delete this test set?';
        new VerifyDelete(msg, 'Test Set').then(function() {
            TestSets.delete($scope.testSet.id).then(function() {
                $state.go("initial.tabs.tests");
            });
        });
    };
  });
})(angular);
