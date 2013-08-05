angular.module(APP_NAME).config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
    defaultCode = 'ors'

    appPrefix = APP_PREFIX
    templatePrefix = PARTIALS_PREFIX

    $routeProvider
        .when(appPrefix + '/view', {
            redirectTo: "/view/#{defaultCode}"
        })
        .when(appPrefix + '/view/:lawCode', {
            controller: 'ViewerCtrl'
            templateUrl: templatePrefix + '/home.html'
        })
        .when(appPrefix + '/view/:lawCode/:version', {
            redirectTo: "/view/#{defaultCode}"
        })
        .when(appPrefix + '/view/:lawCode/:version/:section', {
            controller: 'ViewerCtrl'
            templateUrl: templatePrefix + '/home.html'
        })
        .when(appPrefix + '/diff', {
            redirectTo: '/diff/ors'
        })
        .when(appPrefix + '/diff/:lawCode', {
            controller: 'DiffCtrl'
            templateUrl: templatePrefix + '/diff.html'
        })
        .when(appPrefix + '/diff/:lawCode/:subsection/:version1/:version2', {
            controller: 'DiffCtrl'
            templateUrl: templatePrefix + '/diff.html'
        })
        .when(appPrefix + '/toc/:lawCode', {
            controller: 'TocParentCtrl'
            templateUrl: templatePrefix + '/toc_base.html'
        })
        .otherwise({
            redirectTo: appPrefix + "/toc/#{defaultCode}"
        })

    $locationProvider
        .html5Mode(true)
        .hashPrefix('!');
]
