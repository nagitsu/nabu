'use strict';

describe('Controller: TabsCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var TabsCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    TabsCtrl = $controller('TabsCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(TabsCtrl.awesomeThings.length).toBe(3);
  });
});
