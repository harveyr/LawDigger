app = angular.module(APP_NAME, [
    DIRECTIVE_MODULE,
    SERVICES_MODULE,
]).run ($route, $location, $rootScope, $routeParams) ->

    $rootScope.$on '$routeChangeSuccess', ->
        console.log 'routeChangeSuccess'
        if $routeParams.lawCode
            $rootScope.currentLawCode = $routeParams.lawCode


    _.mixin({
        in: (arr, value) ->
            arr.indexOf(value) != -1
    })
