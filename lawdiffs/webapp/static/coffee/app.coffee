app = angular.module(APP_NAME, [
    DIRECTIVE_MODULE,
    SERVICES_MODULE,
]).run ($rootScope) ->
    $rootScope.appName = "My Lil' App"
