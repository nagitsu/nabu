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
    $scope, $state, $mdDialog, VerifyDelete, TestSets, Results, testset,
    evaluationResults, embeddingList
  ) {
    $scope.dialogLoading = false;
    $scope.testSet = testset;
    $scope.evaluationResults = evaluationResults;
    // Here we build a map for Embeddings data: Embedding.id -> Embedding.data
    $scope.embeddings = _.fromPairs(_.map(embeddingList, function(item) {
        return [item.id, item];
    }));

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

    $scope.testResultDialog = function(ev, embeddingId) {
        if ($scope.dialogLoading) {
            return;
        }
        $scope.dialogLoading = true;
        $mdDialog.show({
            controller: 'TestResultDialogCtrl',
            templateUrl: 'views/test-result-dialog.html',
            targetEvent: ev,
            clickOutsideToClose: true,
            resolve: {
                resultData: function(Results) {
                    return Results.retrieve(
                        embeddingId, $scope.testSet.id
                    ).then(function(response) {
                        return response.data;
                    });
                }
            },
            locals: {
                embedding: $scope.embeddings[embeddingId],
                test: $scope.testSet
            },
            onComplete: function() {
                $scope.dialogLoading = false;
            }
        });
    };

    $scope.newEmbeddingTestDialog = function(ev) {
        if ($scope.dialogLoading) {
            return;
        }
        $scope.dialogLoading = true;
        $mdDialog.show({
            controller: 'NewEmbeddingTestDialogCtrl',
            templateUrl: 'views/test-embedding-new.html',
            targetEvent: ev,
            clickOutsideToClose: true,
            locals: {
                embeddings: embeddingList,
                test: $scope.testSet
            },
            onComplete: function() {
                $scope.dialogLoading = false;
            }
        });
    };
  });
})(angular);
