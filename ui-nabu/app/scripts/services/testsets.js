(function () {

'use strict';

/**
 * @ngdoc service
 * @name nabuApp.TestSets
 * @description
 * # TestSets
 * Service in the nabuApp.
 */
angular.module('nabuApp')
  .service('TestSets', function (Restangular) {
    return {
      list: function () {
        return Restangular.one('testsets').get();
      },

      create: function (newTestset) {
        return Restangular.all('testsets').post(newTestset);
      },

      retrieve: function (testsetId) {
        return Restangular.one('testsets', testsetId).get();
      },

      update: function (testsetId, data) {
        return Restangular.one('testsets', testsetId).post('', data);
      },

      delete: function (testsetId) {
        return Restangular.one('testsets', testsetId).remove();
      },
    };
  });
})(angular);
