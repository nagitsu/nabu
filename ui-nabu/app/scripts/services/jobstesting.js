(function () {

'use strict';

/**
 * @ngdoc service
 * @name nabuApp.JobsTesting
 * @description
 * # JobsTesting
 * Factory in the nabuApp.
 */
angular.module('nabuApp')
  .factory('JobsTesting', function (Restangular) {
    return {
      list: function (status) {
        var apiCall = Restangular.all('jobs').one('testing');
        if (status) {
          var params = {status: status};
          return apiCall.get(params);
        } else {
          return apiCall.get();
        }
      },

      create: function (embeddingId, testsetId) {
        var newTestingJob = {
            'embedding_id': embeddingId,
            'testset_id': testsetId
        };
        return Restangular.all('jobs').all('testing').post(newTestingJob);
      },

      retrieve: function (testingJobId) {
        return Restangular.all('jobs').one('testing', testingJobId).get();
      },

      delete: function (testingJobId) {
        return Restangular.all('jobs').one('testing', testingJobId).remove();
      },
    };
  });
})(angular);
