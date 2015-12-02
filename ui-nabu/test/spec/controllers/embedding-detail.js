'use strict';

describe('Controller: EmbeddingDetailCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var EmbeddingDetailCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    EmbeddingDetailCtrl = $controller('EmbeddingDetailCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(EmbeddingDetailCtrl.awesomeThings.length).toBe(3);
  });
});
