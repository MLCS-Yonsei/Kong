var mlcs = angular.module('mlcs', [
    'ui.router',                    // Routing
    'oc.lazyLoad',                  // ocLazyLoad
    'ui.bootstrap',                 // Ui Bootstrap
]);

mlcs.filter('str2date', function(){
    return function(input) {
        return input.slice(0,4)+'년 '+input.slice(4,6)+'월 '+input.slice(6,8)+'일 '+input.slice(8,10)+':'+input.slice(10,12)+':'+input.slice(12,14);
    }
});
