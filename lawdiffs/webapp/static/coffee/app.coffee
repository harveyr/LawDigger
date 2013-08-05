app = angular.module(APP_NAME, [
    DIRECTIVE_MODULE,
    SERVICES_MODULE,
]).run ($route, $location, $rootScope, UrlBuilder) ->

    $rootScope.appPrefix = UrlBuilder.APP_PREFIX

    $rootScope.$on '$routeChangeSuccess', (e, current, previous) ->
        path = $location.path()

        if _.beginswith path, '/view'
            $rootScope.currentNav = 'view'
        else if _.beginswith path, '/diff'
            $rootScope.currentNav = 'diff'

        params = current.params
        if _.has params, 'lawCode'
            $rootScope.currentLawCode = params.lawCode


    _.mixin({
        in: (arr, value) ->
            arr.indexOf(value) != -1

        beginswith: (string_, substring_) ->
            string_.indexOf(substring_) == 0
    })

