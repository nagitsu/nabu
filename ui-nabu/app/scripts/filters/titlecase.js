(function () {

'use strict';

/**
 * @ngdoc filter
 * @name nabuApp.filter:titlecase
 * @function
 * @description
 * # titlecase
 * Filter in the nabuApp. Example: "hi all." | titlecase -> "Hi All."
 */
angular.module('nabuApp')
  .filter('titlecase', function () {
    /*
        Credit: https://gist.github.com/i8ramin
                (https://gist.github.com/maruf-nc/5625869)
    */
    return function (input) {
        var words = input.split(' ');
        for (var i = 0; i < words.length; i++) {
          // lowercase everything to get rid of weird casing issues
          words[i] = words[i].toLowerCase();
          words[i] = words[i].charAt(0).toUpperCase() + words[i].slice(1);
        }
        return words.join(' ');
    };
  });
})(angular);
