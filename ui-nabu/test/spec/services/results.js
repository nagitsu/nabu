'use strict';

describe('Service: Results', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var Results;
  beforeEach(inject(function (_Results_) {
    Results = _Results_;
  }));

  it('should do something', function () {
    expect(!!Results).toBe(true);
  });

});
