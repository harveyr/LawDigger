angular.module(APP_NAME).config ['$routeProvider', '$locationProvider', ($routeProvider, $locationProvider) ->
    defaultCode = 'ors'

    appPrefix = APP_PREFIX
    templatePrefix = PARTIALS_PREFIX

    $routeProvider
        .when(appPrefix + '/view/:lawCode/:version/:subsection', {
            controller: 'LawViewerCtrl'
            templateUrl: templatePrefix + '/view_law.html'
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
        .when(appPrefix + '/toc/:lawCode/:version/:division', {
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
