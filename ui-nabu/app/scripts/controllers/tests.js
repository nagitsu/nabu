(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TestsCtrl
 * @description
 * # TestsCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('TestsCtrl', function ($scope, $mdDialog, TestSets, testsList) {
    $scope.dialogLoading = false;
    $scope.tests = testsList;

    $scope.newTestSetDialog = function(ev) {
        if ($scope.dialogLoading) {
            return;
        }
        $scope.dialogLoading = true;
        $mdDialog.show({
            controller: 'TestNewDialogCtrl',
            templateUrl: 'views/test-new.html',
            targetEvent: ev,
            clickOutsideToClose: true,
            locals: {
                TestSets: TestSets
            },
            onComplete: function() {
                $scope.dialogLoading = false;
            }
        }).then(function(newObjCreated) {
            // If we get here, the new test set was created successfully.
            if (newObjCreated) {
                // Refresh tests list.
                TestSets.list().then(function(response) {
                    $scope.tests = response.data;
                });
            }
        });
    };
  });
})(angular);
