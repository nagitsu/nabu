(function () {

'use strict';

/**
 * @ngdoc service
 * @name nabuApp.Enums
 * @description
 * # Enums
 * Service in the nabuApp.
 */
angular.module('nabuApp')
  .service('Enums', function (Restangular) {
    return {
      models: function () {
        return Restangular.all('enums').one('models').get();
      },

      corpus: function () {
        return Restangular.all('enums').one('corpus').get();
      },

      tests: function () {
        return Restangular.all('enums').one('tests').get();
      },
    };
  });
})(angular);
