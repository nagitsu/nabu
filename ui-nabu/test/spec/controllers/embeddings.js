'use strict';

describe('Controller: EmbeddingsCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var EmbeddingsCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    EmbeddingsCtrl = $controller('EmbeddingsCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(EmbeddingsCtrl.awesomeThings.length).toBe(3);
  });
});
