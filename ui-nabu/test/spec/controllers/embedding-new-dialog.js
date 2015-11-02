'use strict';

describe('Controller: EmbeddingNewDialogCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var EmbeddingNewDialogCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    EmbeddingNewDialogCtrl = $controller('EmbeddingNewDialogCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(EmbeddingNewDialogCtrl.awesomeThings.length).toBe(3);
  });
});
