'use strict';

describe('Controller: TestsCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var TestsCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    TestsCtrl = $controller('TestsCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(TestsCtrl.awesomeThings.length).toBe(3);
  });
});
