(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TestNewDialogCtrl
 * @description
 * # TestNewDialogCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('TestNewDialogCtrl', function ($scope, $mdDialog, TestSets) {
    $scope.showErrors = false;
    $scope.uploadFileName = 'Please select a test set file.';

    $scope.uploadFile = function(event) {
        $scope.uploadFileName = event.target.files[0].name;
        $scope.newTestSet.file = event.target.files[0];
    };

    $scope.newTestSet = {
        'name': '',
        'description': '',
        'type': '',
        'file': ''
    };

    $scope.create = function() {
        $scope.showErrors = false;
        TestSets.create($scope.newTestSet).then(function(createdTestSet) {
            // Successful creation, notify parent controller.
            $mdDialog.hide(true);
        }, function() {
            // There was an error creating the new test set.
            $scope.showErrors = true;
        });
    };

    $scope.cancel = function() {
        $mdDialog.cancel();
    };
  });
})(angular);
