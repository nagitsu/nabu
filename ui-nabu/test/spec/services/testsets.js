'use strict';

describe('Service: TestSets', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var TestSets;
  beforeEach(inject(function (_TestSets_) {
    TestSets = _TestSets_;
  }));

  it('should do something', function () {
    expect(!!TestSets).toBe(true);
  });

});
