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

      retrieve: function (embeddingId) {
        // After the data object is retrieved we get an object that we can use
        // for updating by changing any part of it and then calling the save()
        // method. We can also delete it using the remove() method.
        return Restangular.one('embeddings', embeddingId).get();
      },

      create: function (newEmbedding) {
        return Restangular.all('embeddings').post(newEmbedding);
      },
    };
  });
