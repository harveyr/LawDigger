angular.module('myLilApp').config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
    $routeProvider
        .when('/', {
            controller: 'ViewerCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .when('/view', {
            controller: 'ViewerCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .when('/view/:lawCode', {
            redirectTo: '/'
        })
        .when('/view/:lawCode/:param', {
            redirectTo: '/'
        })
        .when('/view/:lawCode/:version/:section', {
            controller: 'ViewerCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .when('/diff/:lawCode/:subsection/:version1/:version2', {
            controller: 'DiffCtrl'
            templateUrl: '/static/partials/diff.html'
        })
        .otherwise({
            redirectTo: '/'    
        })

    $locationProvider
        .html5Mode(true)
        .hashPrefix('!');
]
