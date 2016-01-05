'use strict';

describe('Directive: chooseFileButton', function () {

  // load the directive's module
  beforeEach(module('nabuApp'));

  var element,
    scope;

  beforeEach(inject(function ($rootScope) {
    scope = $rootScope.$new();
  }));

  it('should make hidden element visible', inject(function ($compile) {
    element = angular.element('<choose-file-button></choose-file-button>');
    element = $compile(element)(scope);
    expect(element.text()).toBe('this is the chooseFileButton directive');
  }));
});
