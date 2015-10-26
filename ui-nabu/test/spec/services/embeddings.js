'use strict';

describe('Service: Embeddings', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var Embeddings;
  beforeEach(inject(function (_Embeddings_) {
    Embeddings = _Embeddings_;
  }));

  it('should do something', function () {
    expect(!!Embeddings).toBe(true);
  });

});
