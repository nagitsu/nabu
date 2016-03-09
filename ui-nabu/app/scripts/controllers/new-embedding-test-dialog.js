(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:NewEmbeddingTestDialogCtrl
 * @description
 * # NewEmbeddingTestDialogCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('NewEmbeddingTestDialogCtrl', function (
    $scope, $mdDialog, JobsTesting, embeddings, test
  ) {
    $scope.embeddings = embeddings;
    $scope.test = test;

    $scope.evaluationMethod;
    $scope.embeddingId;

    $scope.create = function() {
      $scope.showErrors = false;

      var embeddingId = $scope.evaluationMethod;
      if ($scope.evaluationMethod === 'single') {
        embeddingId = $scope.embeddingId;
      }

      JobsTesting.create(embeddingId, $scope.test.id).then(function(createdTest) {
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
