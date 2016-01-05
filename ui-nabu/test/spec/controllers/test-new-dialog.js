'use strict';

describe('Controller: TestNewDialogCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var TestNewDialogCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    TestNewDialogCtrl = $controller('TestNewDialogCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(TestNewDialogCtrl.awesomeThings.length).toBe(3);
  });
});
