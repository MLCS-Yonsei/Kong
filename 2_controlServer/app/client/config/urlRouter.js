function config($stateProvider, $urlRouterProvider, $ocLazyLoadProvider, $locationProvider) {
    $urlRouterProvider.otherwise("/");
    $locationProvider.html5Mode(true);
    $ocLazyLoadProvider.config({
        // Set to true if you want to see what and when is dynamically loaded
        debug: false
    });

    $stateProvider

        .state('main', {
            url: "/",
            data: { pageTitle: 'Example view' },
            views: {
                'contents' : {
                    templateUrl: "/app/client/views/main.html",
                }
            }
        })

}
mlcs.config(config)
    .run(function($rootScope, $state) {
        $rootScope.$state = $state;
    });
