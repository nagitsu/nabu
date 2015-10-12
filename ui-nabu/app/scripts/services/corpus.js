'use strict';

/**
 * @ngdoc service
 * @name nabuApp.Corpus
 * @description
 * # Corpus
 * Factory in the nabuApp.
 */
angular.module('nabuApp')
  .factory('Corpus', function (Restangular) {
    return {
      search: function (query, offset) {
        if (!offset) {
          offset = 0;
        }
        return Restangular.all('corpus').all('search').post(
          query, {offset: offset}
        );
      },

      stats: function () {
        return Restangular.all('corpus').one('stats').get();
      },

      documentRetrieve: function (docId) {
        return Restangular.all('corpus').one('document', docId).get();
      },

      enums: function () {
        return Restangular.all('corpus').one('enums').get();
      },
    };
  });
