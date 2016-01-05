(function () {

'use strict';

/**
 * @ngdoc directive
 * @name nabuApp.directive:chooseFileButton
 * @description
 * # Credit to: https://github.com/faustomorales
 * # Code from: https://github.com/angular/material/issues/2151#issuecomment-127065949
 */
angular.module('nabuApp')
  .directive('chooseFileButton', function () {
    return {
      link: function (scope, element, attrs) {
        var button = element.find('button');
        var input = element.find('input');
        input.css({display:'none'});
        button.bind('click', function() {
          input[0].click();
        });
        var onChangeHandler = scope.$eval(attrs.chooseFileButton);
        element.bind('change', onChangeHandler);
      }
    };
  });
})(angular);
