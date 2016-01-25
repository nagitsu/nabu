'use strict';

describe('Service: JobsTesting', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var JobsTesting;
  beforeEach(inject(function (_JobsTesting_) {
    JobsTesting = _JobsTesting_;
  }));

  it('should do something', function () {
    expect(!!JobsTesting).toBe(true);
  });

});
