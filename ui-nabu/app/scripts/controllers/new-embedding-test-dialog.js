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

    $scope.newTest = {
        embeddingId: $scope.embeddings[0].id
    };

    $scope.create = function() {
        $scope.showErrors = false;
        JobsTesting.create($scope.newTest.embeddingId, $scope.test.id).then(function(createdTest) {
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
