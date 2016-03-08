(function () {

'use strict';

/**
 * @ngdoc function
 * @name nabuApp.controller:TestsCtrl
 * @description
 * # TestsCtrl
 * Controller of the nabuApp
 */
angular.module('nabuApp')
    .controller('TestsCtrl', function (
      $scope, $interval, $mdDialog, Enums, TestSets, JobsTesting, testsList,
      pendingTestJobs
    ) {

    $scope.dialogLoading = false;
    $scope.testingJobs = buildJobMap(pendingTestJobs);
    $scope.tests = sortTests(testsList);

    $scope.isBeingRun = function (testId) {
      return $scope.testingJobs[testId] !== undefined;
    };

    $scope.getTestingProgress = function (testId) {
      return getTestingProgress($scope.testingJobs, testId);
    };

    $scope.getTestingJobCount = function (testId) {
      return $scope.testingJobs[testId].length;
    };

    $scope.getAllTestingJobCount = function () {
      return _.sum(_.map(_.values($scope.testingJobs), function (o) { return o.length; }));
    };

    $scope.newTestSetDialog = function (ev) {
      if ($scope.dialogLoading) {
        return;
      }
      $scope.dialogLoading = true;
      $mdDialog.show({
        controller: 'TestNewDialogCtrl',
        templateUrl: 'views/test-new.html',
        targetEvent: ev,
        clickOutsideToClose: true,
        resolve: {
          testEnums: function(Enums) {
            return Enums.tests();
          }
        },
        locals: {
          TestSets: TestSets
        },
        onComplete: function() {
          $scope.dialogLoading = false;
        }
      }).then(function(newObjCreated) {
        // If we get here, the new test set was created successfully.
        if (newObjCreated) {
          // Refresh tests list.
          TestSets.list().then(function(response) {
            $scope.tests = sortTests(response.data);
          });
        }
      });
    };


    // Periodically update the progress.
    $scope.testingTimer = $interval(function () {
      JobsTesting.list('queued').then(function(response) {
        $scope.testingJobs = buildJobMap(response.data);
      });
    }, 4000);


    // Utility functions.

    function sortTests(testsList) {
      // Sort by progress. If draw, sort alphabetically.
      testsList.sort(function (a, b) {
        var aProgress, bProgress;

        if (!$scope.testingJobs[a.id]) aProgress = -1;
        else aProgress = getTestingProgress($scope.testingJobs, a.id);

        if (!$scope.testingJobs[b.id]) bProgress = -1;
        else bProgress = getTestingProgress($scope.testingJobs, b.id);

        if (aProgress === bProgress) {
          return (a.name < b.name) ? -1 : 1;
        } else {
          return bProgress - aProgress;
        }
      });

      return testsList;
    }

    function getTestingProgress(jobMap, testId) {
      var jobProgress = jobMap[testId].map(function (tj) {
        return tj.progress;
      });
      return Math.max.apply(null, jobProgress);
    }

    function buildJobMap(pendingTestJobs) {
      var jobsMap = {};
      pendingTestJobs.forEach(function (job) {
        if (!jobsMap[job.testset_id]) {
          jobsMap[job.testset_id] = [];
        }
        jobsMap[job.testset_id].push(job);
      });
      return jobsMap;
    }
  });
})(angular);
