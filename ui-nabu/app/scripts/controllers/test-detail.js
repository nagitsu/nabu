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
    $scope, $state, $mdDialog, $interval, VerifyDelete, TestSets, Results,
    JobsTesting, testset, evaluationResults, embeddingList, modelEnums,
    pendingTestJobs
  ) {
    $scope.dialogLoading = false;
    $scope.testSet = testset;

    // Here we build a map for Embeddings data: Embedding.id -> Embedding.data
    $scope.embeddings = _.fromPairs(_.map(embeddingList, function(item) {
        return [item.id, item];
    }));

    $scope.jobsInProgress = getJobsInProgress(pendingTestJobs);
    $scope.queuedJobs = getQueuedJobs(pendingTestJobs);

    // Augment the evaluation results with testset names and descriptions.
    evaluationResults.forEach(function (elem) {
      elem.embeddingModel = $scope.embeddings[elem.embedding_id].model;
      elem.embeddingDescription = $scope.embeddings[elem.embedding_id].description;
    });

    // Default ordering by model name.
    evaluationResults.sort(function (a, b) {
      return (a.embeddingModel < b.embeddingModel) ? -1 : 1;
    });
    $scope.evaluationResults = evaluationResults;

    $scope.verboseNames = getVerboseNames(modelEnums);

    $scope.formatDate = function(date) {
      return moment(date).format('DD/MM/YYYY HH:mm');
    };

    // Periodically update the progress.
    $scope.testingTimer = $interval(function () {
      JobsTesting.list('queued', $scope.testSet.id).then(function(response) {
        $scope.jobsInProgress = getJobsInProgress(response.data);
        $scope.queuedJobs = getQueuedJobs(response.data);
      });
    }, 4000);

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

    function getVerboseNames(modelEnums) {
      var verboseNames = {};

      modelEnums.forEach(function (elem) {
        verboseNames[elem.model] = elem.verbose_name;
      });

      return verboseNames;
    }

    function getJobsInProgress(testJobs) {
      var inProgress = [];
      testJobs.forEach(function (tj) {
        if (tj.progress > 0) {
          inProgress.push({
            embedding: {id: tj.embedding_id, name: $scope.embeddings[tj.embedding_id].name},
            progress: tj.progress
          });
        }
      });
      return inProgress;
    }

    function getQueuedJobs(testJobs) {
      var queued = [];
      testJobs.forEach(function (tj) {
        if (tj.progress < 0.01) {  // It's a float, use a tolerance.
          queued.push({
            embedding: {id: tj.embedding_id, name: $scope.embeddings[tj.embedding_id].name}
          });
        }
      });
      return queued;
    }
  });
})(angular);
