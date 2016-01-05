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
        // Restangular (and also $http) asks for a little extra effort in order
        // to upload files.
        var data = new FormData();
        data.append('name', newTestset.name);
        data.append('type', newTestset.type);
        data.append('file', newTestset.file);
        data.append('description', newTestset.description);

        return Restangular.all('testsets')
          .withHttpConfig({transformRequest: angular.identity})
          .customPOST(data, '', undefined, {'Content-Type': undefined});
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
