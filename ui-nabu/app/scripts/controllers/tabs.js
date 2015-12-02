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
        'dashboard',
        'corpus',
        'embeddings',
        'tests'
    ];

    $scope.changeTab = function(tab) {
        var stateToGo = 'initial.tabs.' + tab;
        $state.go(stateToGo);
    };

    var tabNameMatches = $state.current.name.match(/tabs\.(\w+)(\.|$|-)/);
    // tabNameMatches = ['...', 'Tab name here', '...']
    $scope.selectedIndex = $scope.tabs.indexOf(tabNameMatches[1]);
  });
})(angular);
