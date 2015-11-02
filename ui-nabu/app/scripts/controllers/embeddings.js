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
  .controller('EmbeddingsCtrl', function ($scope, $mdDialog, Enums, Embeddings, embeddingList) {
    $scope.dialogLoading = false;
    $scope.embeddings = embeddingList;

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
                }
            },
            onComplete: function() {
                $scope.dialogLoading = false;
            }
        });
    };
  });
})(angular);
