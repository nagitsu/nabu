'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:CorpusCtrl
 * @description
 * # CorpusCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('CorpusCtrl', function ($rootScope, $scope, $mdDialog, Corpus) {
    $scope.resultsTable = {
        page: 1,
        limit: 25 // This is hard-coded in the server
    };
    $scope.loading = false;
    $scope.dialogLoading = false;

    $scope.basicQuery = {
        'query': {
            'match' : {
                'content' : ''
            }
        }
    };

    $scope.search = function () {
        $scope.loading = true;
        Corpus.search($scope.basicQuery).then(function(results){
            $scope.resultsTable.page = 1;
            $scope.results = results;
            $scope.loading = false;
        });
    };

    $scope.onPaginationChange = function (page, limit) {
        var offset = (page - 1) * $scope.resultsTable.limit;
        Corpus.search($scope.basicQuery, offset).then(function(results){
            $scope.results = results;
        });
    };

    $scope.documentDetailDialog = function(ev, docId) {
        if ($scope.dialogLoading) {
            return;
        }
        $scope.dialogLoading = true;
        $mdDialog.show({
            controller: 'DocumentDetailDialogCtrl',
            templateUrl: 'views/document-detail.html',
            targetEvent: ev,
            clickOutsideToClose: true,
            resolve: {
                docData: function(Corpus){
                    return Corpus.documentRetrieve(docId);
                }
            },
            onComplete: function() {
                $scope.dialogLoading = false;
            }
        });
    };
  });
