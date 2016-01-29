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
  .controller('TabsCtrl', function ($rootScope, $scope, $state) {
    $scope.tabs = [
        'dashboard',
        'corpus',
        'embeddings',
        'tests'
    ];

    $scope.changeTab = function(tab) {
        var stateToGo = 'initial.tabs.' + tab;
        $state.go(stateToGo);
    };

    $scope.setCurrentTab = function(state) {
        var tabNameMatches = state.name.match(/tabs\.(\w+)(\.|$|-)/);
        // tabNameMatches = ['...', 'Tab name here', '...']
        $scope.selectedIndex = $scope.tabs.indexOf(tabNameMatches[1]);
    };

    $rootScope.$on('$stateChangeStart', function(
        event, toState, toParams, fromState, fromParams
    ) {
        $scope.setCurrentTab(toState);
    });

    // Set tab for cases where there was no initial state change.
    $scope.setCurrentTab($state.current);
  });
})(angular);
