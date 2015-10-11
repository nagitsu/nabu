'use strict';

describe('Service: Corpus', function () {

  // load the service's module
  beforeEach(module('nabuApp'));

  // instantiate service
  var Corpus;
  beforeEach(inject(function (_Corpus_) {
    Corpus = _Corpus_;
  }));

  it('should do something', function () {
    expect(!!Corpus).toBe(true);
  });

});
