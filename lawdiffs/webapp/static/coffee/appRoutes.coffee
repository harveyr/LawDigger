angular.module('myLilApp').config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
    $routeProvider
        .when('/view', {
            redirectTo: '/view/ors'
        })
        .when('/view/:lawCode', {
            controller: 'ViewerCtrl'
            templateUrl: '/static/partials/home.html'
        })
        .when('/view/:lawCode/:param', {
            redirectTo: '/view/ors'
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
            redirectTo: '/view'
        })

    $locationProvider
        .html5Mode(true)
        .hashPrefix('!');
]
