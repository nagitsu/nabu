(function () {

'use strict';

/**
 * @ngdoc service
 * @name nabuApp.JobsTraining
 * @description
 * # JobsTraining
 * Factory in the nabuApp.
 */
angular.module('nabuApp')
  .factory('JobsTraining', function (Restangular) {
    return {
      list: function (status) {
        var apiCall = Restangular.all('jobs').one('training');
        if (status) {
          var params = {status: status};
          return apiCall.get(params);
        } else {
          return apiCall.get();
        }
      },

      create: function (newTrainingJob) {
        return Restangular.all('jobs').all('training').post(newTrainingJob);
      },

      retrieve: function (trainingJobId) {
        return Restangular.all('jobs').one('training', trainingJobId).get();
      },

      delete: function (trainingJobId) {
        return Restangular.all('jobs').one('training', trainingJobId).remove();
      },
    };
  });
})(angular);
