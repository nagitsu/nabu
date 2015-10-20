'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:CorpusCtrl
 * @description
 * # CorpusCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
  .controller('CorpusCtrl', function ($scope, $mdDialog, Corpus, sourceList) {
    $scope.resultsTable = {
        page: 1,
        limit: 25 // This is hard-coded in the server
    };
    $scope.loading = false;
    $scope.dialogLoading = false;
    $scope.sourceList = sourceList;

    $scope.searchQuery = {
        query: '',
        sources: []
    };

    $scope.basicQuery = {
        'query': {
            'match' : {
                'content' : ''
            }
        }
    };

    $scope.filterSourceQuery = {
        'query': {
          'bool': {
             'must': [
                {
                   'terms': {
                      'data_source': [],
                      'minimum_should_match' : 1
                   }
                },
                {
                   'match': {
                      'content': ''
                   }
                }
             ]
          }
       }
    };

    $scope.search = function () {
        var q;
        $scope.loading = true;

        if ($scope.searchQuery.sources.length){
            // We must filter by data source
            q = $scope.filterSourceQuery;
            q.query.bool.must[1].match.content = $scope.searchQuery.query;
            q.query.bool.must[0].terms.data_source = $scope.searchQuery.sources;
        } else {
            q = $scope.basicQuery;
            q.query.match.content = $scope.searchQuery.query;
        }

        Corpus.search(q).then(function(results){
            $scope.resultsTable.page = 1;
            $scope.results = results;
            $scope.loading = false;
        });
    };

    $scope.onPaginationChange = function (page, limit) {
        var offset = (page - 1) * $scope.resultsTable.limit;
        return Corpus.search($scope.basicQuery, offset).then(function(results){
            $scope.results = results;
        });
    };

    $scope.onOrderChange = function (order) {
        /* The server doesn't support ordering at the moment. We leave this
         * placeholder here in case ordering is implemented in the future.
         */
         return null;
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
