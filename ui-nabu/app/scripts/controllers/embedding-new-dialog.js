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
  .controller('EmbeddingNewDialogCtrl', function ($scope, $mdDialog, modelEnums, corpusEnums) {
    // Transform the list of models data into a map that has model names as
    // keys and model parameters as values.
    $scope.models = _.object(_.map(modelEnums.data, function(item) {
        return [item.model, item];
    }));

    $scope.corpusPreprocessors = corpusEnums.data;

    $scope.newEmb = {
        'model': modelEnums.data[0].model,
        'description': '',
        'parameters': {},
        'preprocessing': {}
    };
    $scope.currentParams = [];

    $scope.$watch('newEmb.model', function(){
        // Update the list of model parameters when the selected model changes.
        $scope.newEmb.parameters = {};
        $scope.currentParams = $scope.models[$scope.newEmb.model].parameters;

        // Set default values for all fields.
        angular.forEach($scope.currentParams, function(param) {
          $scope.newEmb.parameters[param.name] = param.default;
        });
    });

    $scope.cancel = function() {
        $mdDialog.cancel();
    };
  });
})(angular, _);
