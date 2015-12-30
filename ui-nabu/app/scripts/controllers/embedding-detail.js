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
    $scope, $state, VerifyDelete, JobsTraining, Embeddings, embedding,
    evaluationResults, testList
  ) {
    $scope.embedding = embedding;
    $scope.evaluationResults = evaluationResults;
    // Here we build a map for TestSet data: TestSet.id -> TestSet.data
    $scope.testSet = _.object(_.map(testList, function(item) {
        return [item.id, item];
    }));

    $scope.searchQuery = angular.toJson($scope.embedding.corpus.query, true);
    $scope.aceLoaded = function(_editor) {
        // Options
        _editor.setReadOnly(true);
        _editor.$blockScrolling = Infinity;
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
  });
})(angular);
