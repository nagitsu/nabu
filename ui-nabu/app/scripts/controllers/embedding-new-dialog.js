(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:EmbeddingNewDialogCtrl
 * @description
 * # EmbeddingNewDialogCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('EmbeddingNewDialogCtrl', function (
    $scope, $mdDialog, Embeddings, modelEnums, corpusEnums, newEmbQuery
  ) {
    // Properties

    $scope.showErrors = false;
    // Transform the list of models data into a map that has model names as
    // keys and model parameters as values.
    $scope.models = _.fromPairs(_.map(modelEnums.data, function(item) {
        return [item.model, item];
    }));

    $scope.corpusPreprocessors = corpusEnums.data;

    $scope.newEmb = {
        'model': modelEnums.data[0].model,
        'description': '',
        'parameters': {},
        'preprocessing': {},
        'query': {}
    };
    $scope.currentParams = [];

    // Initial behaviour

    $scope.$watch('newEmb.model', function(){
        // Update the list of model parameters when the selected model changes.
        $scope.newEmb.parameters = {};
        $scope.currentParams = $scope.models[$scope.newEmb.model].parameters;

        // Set default values for all fields.
        angular.forEach($scope.currentParams, function(param) {
          $scope.newEmb.parameters[param.name] = param.default;
        });
    });

    $scope.$watch('searchQuery', function(){
        // Transform text query into JSON object.
        $scope.newEmb.query = angular.fromJson($scope.searchQuery);
    });

    if (newEmbQuery) {
        // Use provided query.
        $scope.searchQuery = angular.toJson(newEmbQuery, true);
    } else {
        // Default query.
        $scope.searchQuery = angular.toJson({'match': {'content': ''}}, true);
    }

    // Methods

    $scope.aceLoaded = function(_editor) {
        // Options
        _editor.$blockScrolling = Infinity;
    };

    $scope.create = function() {
        $scope.showErrors = false;
        Embeddings.create($scope.newEmb).then(function(createdEmb) {
            // Successful creation, notify parent controller.
            $mdDialog.hide(true);
        }, function() {
            // There was an error creating the new embedding.
            $scope.showErrors = true;
        });
    };

    $scope.cancel = function() {
        $mdDialog.cancel();
    };
  });
})(angular, _);
