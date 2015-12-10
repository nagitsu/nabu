'use strict';

describe('Service: JobsTraining', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var JobsTraining;
  beforeEach(inject(function (_JobsTraining_) {
    JobsTraining = _JobsTraining_;
  }));

  it('should do something', function () {
    expect(!!JobsTraining).toBe(true);
  });

});
