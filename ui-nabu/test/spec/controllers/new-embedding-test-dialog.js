'use strict';

describe('Controller: NewEmbeddingTestDialogCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var NewEmbeddingTestDialogCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    NewEmbeddingTestDialogCtrl = $controller('NewEmbeddingTestDialogCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(NewEmbeddingTestDialogCtrl.awesomeThings.length).toBe(3);
  });
});
