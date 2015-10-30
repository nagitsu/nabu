'use strict';

/**
 * @ngdoc service
 * @name nabuApp.Embeddings
 * @description
 * # Embeddings
 * Factory in the nabuApp.
 */
angular.module('nabuApp')
  .factory('Embeddings', function (Restangular) {
    return {
      list: function () {
        return Restangular.one('embeddings').get();
      },

      create: function (newEmbedding) {
        return Restangular.all('embeddings').post(newEmbedding);
      },

      retrieve: function (embeddingId) {
        return Restangular.one('embeddings', embeddingId).get();
      },

      update: function (embeddingId, data) {
        return Restangular.one('embeddings', embeddingId).post('', data);
      },

      delete: function (embeddingId) {
        return Restangular.one('embeddings', embeddingId).remove();
      },
    };
  });
