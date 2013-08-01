angular.module('myLilApp').config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
    $routeProvider
        .when('/', {
            controller: 'HomeCtrl'
            templateUrl: 'static/partials/home.html',
        })
        .otherwise({
            redirectTo: '/'    
        })

    $locationProvider
        .html5Mode(true)
        .hashPrefix('!');
]
