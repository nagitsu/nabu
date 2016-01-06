'use strict';

describe('Controller: TestDetailCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var TestDetailCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    TestDetailCtrl = $controller('TestDetailCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(TestDetailCtrl.awesomeThings.length).toBe(3);
  });
});
