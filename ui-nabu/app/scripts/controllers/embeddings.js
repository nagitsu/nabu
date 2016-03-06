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
  .controller('EmbeddingsCtrl', function (
    $stateParams, $timeout, $interval, $scope, $mdDialog, Enums, Embeddings,
    JobsTraining, embeddingList, pendingTrainingJobs
  ) {
    // Properties

    $scope.dialogLoading = false;
    $scope.embeddings = sortEmbeddings(embeddingList);
    $scope.trainingJobs = buildJobMap(pendingTrainingJobs);


    // Methods

    $scope.newEmbeddingDialog = function(ev) {
        if ($scope.dialogLoading) {
            return;
        }
        $scope.dialogLoading = true;
        $mdDialog.show({
            controller: 'EmbeddingNewDialogCtrl',
            templateUrl: 'views/embedding-new.html',
            targetEvent: ev,
            clickOutsideToClose: true,
            resolve: {
                modelEnums: function(Enums) {
                    return Enums.models();
                },
                corpusEnums: function(Enums) {
                    return Enums.corpus();
                }
            },
            locals: {
                Embeddings: Embeddings,
                newEmbQuery: $stateParams.newEmbQuery
            },
            onComplete: function() {
                $scope.dialogLoading = false;
            }
        }).then(function(newObjCreated) {
            // If we get here, the new embedding was created successfully.
            if (newObjCreated) {
                // Refresh embeddings list.
                Embeddings.list().then(function(response) {
                    $scope.embeddings = sortEmbeddings(response.data);
                });
                JobsTraining.list('queued').then(function(response) {
                    $scope.trainingJobs = buildJobMap(response.data);
                });
            }
        });
    };


    // Initial behaviour

    // We got an advanced query in the params so we open the 'new embedding' dialog.
    if ($stateParams.newEmbQuery) {
        // We use timeout to break out of the current $apply() cycle.
        $timeout(function() {
            angular.element('#new-embedding-btn').trigger('click');
        }, 100);
    }


    // Periodically update the progress.

    $scope.trainingTimer = $interval(function () {
        JobsTraining.list('queued').then(function(response) {
            $scope.trainingJobs = buildJobMap(response.data);
        });
    }, 4000);


    // Utility functions

    function sortEmbeddings(embeddingList) {
        // Display training embeddings first.
        var statusOrder = ['TRAINING', 'TRAINED', 'UNTRAINED'];
        embeddingList.sort(function (a, b) {
            return statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status);
        });
        return embeddingList;
    }

    function buildJobMap(pendingTrainingJobs) {
        // Training jobs indexed by embedding ID.
        var jobsMap = {};
        pendingTrainingJobs.forEach(function (job) {
            jobsMap[job.embedding_id] = job;
        });
        return jobsMap;
    }

  });
})(angular);
