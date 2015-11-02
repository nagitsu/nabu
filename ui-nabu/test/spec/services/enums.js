'use strict';

describe('Service: Enums', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var Enums;
  beforeEach(inject(function (_Enums_) {
    Enums = _Enums_;
  }));

  it('should do something', function () {
    expect(!!Enums).toBe(true);
  });

});
