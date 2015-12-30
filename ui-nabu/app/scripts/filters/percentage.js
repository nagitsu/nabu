(function () {

'use strict';

/**
 * @ngdoc filter
 * @name nabuApp.filter:percentage
 * @function
 * @description
 * # percentage
 * Filter in the nabuApp. Example: 0.8532 | percentage -> "85%"
 */
angular.module('nabuApp')
  .filter('percentage', function ($filter) {
    /*
        Credit: https://gist.github.com/jeffjohnson9046
                (https://gist.github.com/jeffjohnson9046/9470800)
    */
    return function (input, decimals) {
        // This filter makes the assumption that the input will be in decimal form (i.e. 17% is 0.17).
        if (!decimals) {
            decimals = 0;
        }
        return $filter('number')(input * 100, decimals) + '%';
    };
  });
})(angular);
