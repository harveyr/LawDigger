app = angular.module(APP_NAME, [
    DIRECTIVE_MODULE,
    SERVICES_MODULE,
]).run ($route, $location, $rootScope) ->
    # $rootScope.$on '$routeChangeSuccess', ->
    #     path = $location.path
    #     $rootScope.partialUrl = partials[$location.path()]

    console.log 'here'

    _.mixin({
        in: (arr, value) ->
            arr.indexOf(value) != -1
    })
