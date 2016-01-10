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
      list: function (embeddingId, testSetId) {
        var queryParams = {};
        if (embeddingId) queryParams.embedding = embeddingId;
        if (testSetId) queryParams.testset = testSetId;

        return Restangular.one('results').get(queryParams);
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
