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
        return Restangular.all('corpus').all('search/').post(
          query, {offset: offset}
        );
      }
    };
  });
