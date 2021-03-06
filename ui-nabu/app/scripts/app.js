(function () {

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
    'restangular',
    'ui.ace',
    'chart.js'
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
                  sources.sort();
                  return sources;
                });
              }
            }
          }
        },
        params: {
          esQuery: null
        }
      })
      .state('initial.tabs.dashboard', {
        url: '/dashboard',
        views: {
          'dashboard': {
            templateUrl: "views/dashboard.html",
            controller: 'DashboardCtrl',
            resolve: {
              corpusStats: function (Corpus) {
                return Corpus.stats().then(function(response) {
                  return response.data;
                });
              }
            }
          }
        }
      })
      .state('initial.tabs.embeddings', {
        url: '/embeddings',
        views: {
          'embeddings': {
            templateUrl: "views/embeddings.html",
            controller: 'EmbeddingsCtrl',
            resolve: {
              embeddingList: function (Embeddings) {
                return Embeddings.list().then(function(response) {
                  return response.data;
                });
              },
              pendingTrainingJobs: function (JobsTraining) {
                return JobsTraining.list('queued').then(function(response) {
                  return response.data;
                });
              }
            }
          }
        },
        params: {
          newEmbQuery: null
        }
      })
      .state('initial.tabs.embeddings-detail', {
        url: '/embeddings/:embeddingId',
        views: {
          'embedding-detail': {
            templateUrl: "views/embedding-detail.html",
            controller: 'EmbeddingDetailCtrl',
            resolve: {
              embedding: function (Embeddings, $stateParams) {
                return Embeddings.retrieve($stateParams.embeddingId).then(function(response) {
                  return response.data;
                });
              },
              evaluationResults: function (Results, $stateParams) {
                return Results.list($stateParams.embeddingId).then(function(response) {
                  return response.data;
                });
              },
              testList: function (TestSets) {
                return TestSets.list().then(function(response) {
                  return response.data;
                });
              },
              modelEnums: function(Enums) {
                return Enums.models().then(function(response) {
                  return response.data;
                });
              },
              corpusEnums: function(Enums) {
                return Enums.corpus().then(function(response) {
                  return response.data;
                });
              }
            }
          }
        }
      })
      .state('initial.tabs.tests', {
        url: '/tests',
        views: {
          'tests': {
            templateUrl: "views/tests.html",
            controller: 'TestsCtrl',
            resolve: {
              testsList: function (TestSets) {
                return TestSets.list().then(function(response) {
                  return response.data;
                });
              },
              pendingTestJobs: function (JobsTesting) {
                return JobsTesting.list('queued').then(function(response) {
                  return response.data;
                });
              }
            }
          }
        }
      })
      .state('initial.tabs.tests-detail', {
        url: '/tests/:testId',
        views: {
          'test-detail': {
            templateUrl: "views/test-detail.html",
            controller: 'TestDetailCtrl',
            resolve: {
              testset: function (TestSets, $stateParams) {
                return TestSets.retrieve($stateParams.testId).then(function(response) {
                  return response.data;
                });
              },
              evaluationResults: function (Results, $stateParams) {
                return Results.list(null, $stateParams.testId).then(function(response) {
                  return response.data;
                });
              },
              embeddingList: function (Embeddings) {
                return Embeddings.list().then(function(response) {
                  return response.data;
                });
              },
              pendingTestJobs: function (JobsTesting, $stateParams) {
                return JobsTesting.list('queued', $stateParams.testId).then(function(response) {
                  return response.data;
                });
              },
              modelEnums: function(Enums) {
                return Enums.models().then(function(response) {
                  return response.data;
                });
              },
            }
          }
        }
      });
  })
  .config(function($mdThemingProvider) {
    // Available palettes:
    // red, pink, purple, deep-purple, indigo, blue, light-blue,
    // cyan, teal, green, light-green, lime, yellow, amber, orange,
    // deep-orange, brown, grey, blue-grey
    $mdThemingProvider.theme('default');
  })
  .run(function(Restangular){
    Restangular.setBaseUrl('http://golbat.ydns.eu/api');
    Restangular.setRequestSuffix('/'); // The server expects a trailing slash
  });
})(angular, _);
