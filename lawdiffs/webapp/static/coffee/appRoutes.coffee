angular.module('myLilApp').config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
    $routeProvider
        .when('/', {
            controller: 'HomeCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .when('/view', {
            controller: 'ViewerCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .when('/view/:lawCode', {
            controller: 'ViewerCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .otherwise({
            redirectTo: '/'    
        })

    $locationProvider
        .html5Mode(true)
        .hashPrefix('!');
]
