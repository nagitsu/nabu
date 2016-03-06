(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:EmbeddingDetailCtrl
 * @description
 * # EmbeddingDetailCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('EmbeddingDetailCtrl', function (
    $scope, $state, $interval, $mdDialog, VerifyDelete, JobsTraining,
    Embeddings, embedding, evaluationResults, testList, modelEnums, corpusEnums
  ) {
    $scope.embedding = embedding;
    if (embedding.training_job) {
      $scope.jobProgress = embedding.training_job.progress;
    }

    // Here we build a map for TestSet data: TestSet.id -> TestSet.data
    $scope.testsets = _.fromPairs(_.map(testList, function(item) {
        return [item.id, item];
    }));

    // Augment the evaluation results with testset names and descriptions.
    evaluationResults.forEach(function (elem) {
      elem.testsetName = $scope.testsets[elem.testset_id].name;
      elem.testsetDescription = $scope.testsets[elem.testset_id].description;
    });
    // Default ordering by name.
    evaluationResults.sort(function (a, b) {
      return (a.testsetName < b.testsetName) ? -1 : 1;
    });
    $scope.evaluationResults = evaluationResults;

    $scope.searchQuery = angular.toJson($scope.embedding.corpus.query, true);
    $scope.aceLoaded = function(_editor) {
        // Options
        _editor.setReadOnly(true);
        _editor.$blockScrolling = Infinity;
    };

    $scope.verboseNames = getVerboseNames(modelEnums, corpusEnums);

    $scope.formatDate = function(date) {
      return moment(date).format('DD/MM/YYYY HH:mm');
    };

    $scope.trainEmbedding = function() {
        var newJob = {"embedding_id": $scope.embedding.id};
        JobsTraining.create(newJob).then(function() {
            console.log("Embedding marked for training.");
            Embeddings.retrieve($scope.embedding.id).then(function(emb) {
                $scope.embedding = emb.data;
            });
        });
    };

    $scope.updateEmbedding = function() {
        // In this case we can only update the description attribute.
        var editEmb = {"description": $scope.embedding.description};
        Embeddings.update($scope.embedding.id, editEmb).then(function(emb) {
            $scope.embedding = emb.data;
        });
    };

    $scope.deleteEmbedding = function() {
        var msg = 'Are you sure you want to delete this embedding?';
        new VerifyDelete(msg, 'Embedding').then(function() {
            Embeddings.delete($scope.embedding.id).then(function() {
                $state.go("initial.tabs.embeddings");
            });
        });
    };

    $scope.testResultDialog = function(ev, testsetId) {
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
              $scope.embedding.id, testsetId
            ).then(function(response) {
              return response.data;
            });
          }
        },
        locals: {
          embedding: $scope.embedding,
          test: $scope.testsets[testsetId]
        },
        onComplete: function() {
          $scope.dialogLoading = false;
        }
      });
    };


    // Periodically update the progress.

    $scope.trainingTimer = $interval(function () {
      var trainingJobId = $scope.embedding.training_job.id;
      JobsTraining.retrieve(trainingJobId).then(function(response) {
        $scope.jobProgress = response.data.progress;
      });
    }, 4000);


    function getVerboseNames(modelEnums, corpusEnums) {
      var verboseNames = {};

      modelEnums.filter(function (elem) {
        return elem.model == embedding.model;
      })[0].parameters.forEach(function (elem) {
        verboseNames[elem.name] = elem.verbose_name;
      });

      corpusEnums.forEach(function (elem) {
        verboseNames[elem.name] = elem.verbose_name;
      });

      return verboseNames;
    }
  });
})(angular);
