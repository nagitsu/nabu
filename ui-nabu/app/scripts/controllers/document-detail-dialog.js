(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:DocumentDetailDialogCtrl
 * @description
 * # DocumentDetailDialogCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('DocumentDetailDialogCtrl', function ($scope, $mdDialog, docData) {
    $scope.corpusDoc = docData.data;

    $scope.cancel = function() {
        $mdDialog.cancel();
    };
  });
})(angular);
