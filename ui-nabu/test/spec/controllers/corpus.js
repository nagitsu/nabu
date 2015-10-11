'use strict';

describe('Controller: CorpusCtrl', function () {

  // load the controller's module
  beforeEach(module('nabuApp'));

  var CorpusCtrl,
    scope;

  // Initialize the controller and a mock scope
  beforeEach(inject(function ($controller, $rootScope) {
    scope = $rootScope.$new();
    CorpusCtrl = $controller('CorpusCtrl', {
      $scope: scope
      // place here mocked dependencies
    });
  }));

  it('should attach a list of awesomeThings to the scope', function () {
    expect(CorpusCtrl.awesomeThings.length).toBe(3);
  });
});
