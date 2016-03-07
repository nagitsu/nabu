(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:EvaluateOnTestsetDialogCtrl
 * @description
 * # EvaluateOnTestsetDialogCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('EvaluateOnTestsetDialogCtrl', function (
    $scope, $mdDialog, JobsTesting, embedding, tests
  ) {
    $scope.embedding = embedding;
    $scope.tests = tests;

    $scope.evaluationMethod;
    $scope.testsetId;

    $scope.create = function() {
      $scope.showErrors = false;

      var testsetId = $scope.evaluationMethod;
      if ($scope.evaluationMethod === 'single') {
        testsetId = $scope.testsetId
      }

      JobsTesting.create($scope.embedding.id, testsetId).then(function(createdTest) {
          // Successful creation, notify parent controller.
          $mdDialog.hide(true);
      }, function() {
          // There was an error creating the new test.
          $scope.showErrors = true;
      });
    };

    $scope.cancel = function() {
      $mdDialog.cancel();
    };
  });
})(angular);
