(function () {

'use strict';

/**
 * @ngdoc service
 * @name nabuApp.VerifyDelete
 * @description
 * # VerifyDelete
 * Service in the nabuApp.
 * Credit to: http://www.angularauthority.com/2015/04/28/creating-a-material-design-modal-service/
 */
angular.module('nabuApp')
  .service('VerifyDelete', function ($mdDialog) {
    return function(msg, objType) {
        var deleteType = objType || 'Object';
        var confirm = $mdDialog.confirm()
            .title('Please confirm the action')
            .content(msg)
            .ariaLabel('Delete ' + deleteType)
            .ok('Confirm')
            .cancel('Cancel');
        return $mdDialog.show(confirm);
    };
  });
})(angular);
