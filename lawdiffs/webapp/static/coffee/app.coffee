app = angular.module(APP_NAME, [
    DIRECTIVE_MODULE,
    SERVICES_MODULE,
]).run ($route, $location, $rootScope) ->
    $rootScope.appName = "My Lil' App"

    # partials =
    #     '/': 'static/partials/home.html'
    #     '/view': 'static/partials/home.html'

    # $rootScope.$on '$routeChangeSuccess', ->
    #     path = $location.path
    #     $rootScope.partialUrl = partials[$location.path()]

    _.mixin({
        in: (arr, value) ->
            arr.indexOf(value) != -1
    })
