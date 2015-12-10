'use strict';

describe('Service: VerifyDelete', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var VerifyDelete;
  beforeEach(inject(function (_VerifyDelete_) {
    VerifyDelete = _VerifyDelete_;
  }));

  it('should do something', function () {
    expect(!!VerifyDelete).toBe(true);
  });

});
