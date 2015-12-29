(function () {

'use strict';

/**
 * @ngdoc service
 * @name nabuApp.Results
 * @description
 * # Results
 * Service in the nabuApp.
 */
angular.module('nabuApp')
  .service('Results', function (Restangular) {
    return {
      list: function (embeddingId) {
        if (embeddingId) {
          return Restangular.one('results').get({embedding: embeddingId});
        } else {
          return Restangular.one('results').get();
        }
      },

      retrieve: function (embeddingId, testSetId) {
        return Restangular.one('results', embeddingId).one('', testSetId).get();
      },

      delete: function (embeddingId, testSetId) {
        return Restangular.one('results', embeddingId).one('', testSetId).remove();
      },
    };
  });
})(angular);
