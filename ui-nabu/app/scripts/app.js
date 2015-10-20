'use strict';

/**
 * @ngdoc overview
 * @name nabuApp
 * @description
 * # nabuApp
 *
 * Main module of the application.
 */
angular
  .module('nabuApp', [
    'ngAnimate',
    'ngCookies',
    'ngMessages',
    'ngResource',
    'ngRoute',
    'ngSanitize',
    'ngTouch',
    'ngMaterial',
    'ui.router',
    'ui.bootstrap',
    'md.data.table',
    'restangular'
  ])
  .config(function($stateProvider, $urlRouterProvider) {
    $urlRouterProvider.otherwise("/dashboard");
    $stateProvider
      .state('initial', {
        abstract: true,
        templateUrl: "views/main.html"
      })
      .state('initial.tabs', {
        abstract: true,
        templateUrl: "views/tabs.html",
        controller: 'TabsCtrl'
      })
      .state('initial.tabs.corpus', {
        url: '/corpus',
        views: {
          'corpusSearch': {
            templateUrl: "views/corpus-search.html",
            controller: 'CorpusCtrl',
            resolve: {
              sourceList: function (Corpus) {
                return Corpus.stats().then(function(response) {
                  var sources = [];
                  _.each(response.data.by_source, function(item) {
                    sources.push(item.source);
                  });
                  return sources;
                });
              }
            }
          }
        }
      })
      .state('initial.tabs.dashboard', {
        url: '/dashboard',
        views: {
          'dashboard': {
            templateUrl: "views/dashboard.html",
            controller: function($scope) {
              $scope.items = ["A", "List", "Of", "Items"];
            }
          }
        }
      })
      .state('initial.tabs.embeddings', {
        url: '/embeddings',
        views: {
          'embeddings': {
            templateUrl: "views/embeddings.html",
            controller: function($scope) {
              $scope.items = ["A", "List", "Of", "Items"];
            }
          }
        }
      })
      .state('initial.tabs.tests', {
        url: '/tests',
        views: {
          'tests': {
            templateUrl: "views/tests.html",
            controller: function($scope) {
              $scope.items = ["A", "List", "Of", "Items"];
            }
          }
        }
      });
      // .state('initial.tabs.corpus-search', {
      //   url: '/corpus',
      //   // abstract: true,
      //   templateUrl: "views/corpus-search.html",
      //   controller: function($scope) {
      //     $scope.items = ["A", "List", "Of", "Items"];
      //   }
      // });
      // .state('initial.sidenav.home', {
      //   abstract: true,
      //   url: '/',
      //   templateUrl: "views/main.html",
      //   controller: function($scope) {
      //     $scope.items = ["A", "List", "Of", "Items"];
      //   }
      // });
  })
  .config(function($mdThemingProvider) {
    // Available palettes:
    // red, pink, purple, deep-purple, indigo, blue, light-blue,
    // cyan, teal, green, light-green, lime, yellow, amber, orange,
    // deep-orange, brown, grey, blue-grey
    $mdThemingProvider.theme('default')
      .primaryPalette('light-blue')
      .accentPalette('orange');
  })
  .run(function(Restangular){
    Restangular.setBaseUrl('http://golbat.ydns.eu/api');
    Restangular.setRequestSuffix('/'); // The server expects a trailing slash
  });
