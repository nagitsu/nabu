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
    $stateParams, $timeout, $scope, $mdDialog, Enums, Embeddings, embeddingList
  ) {
    // Properties

    $scope.dialogLoading = false;
    $scope.embeddings = embeddingList;

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
                    $scope.embeddings = response.data;
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
  });
})(angular);
