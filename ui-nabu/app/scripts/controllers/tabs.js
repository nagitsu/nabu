(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TabsCtrl
 * @description
 * # TabsCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('TabsCtrl', function ($scope, $state) {
    $scope.tabs = [
        'initial.tabs.dashboard',
        'initial.tabs.corpus',
        'initial.tabs.embeddings',
        'initial.tabs.tests'
    ];

    $scope.changeTab = function(tab) {
        var stateToGo = 'initial.tabs.' + tab;
        $state.go(stateToGo);
    };

    $scope.selectedTab = $scope.tabs.indexOf($state.current.name);
  });
})(angular);
