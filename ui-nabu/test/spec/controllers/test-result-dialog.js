'use strict';

describe('Controller: TestResultDialogCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var TestResultDialogCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    TestResultDialogCtrl = $controller('TestResultDialogCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(TestResultDialogCtrl.awesomeThings.length).toBe(3);
  });
});
