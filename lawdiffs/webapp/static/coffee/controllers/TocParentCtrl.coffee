angular.module(APP_NAME).controller 'TocParentCtrl', ($route, $scope, $rootScope, $http, $routeParams, UrlBuilder) ->
    $scope.m = {}

    if not $scope.tocData and not $routeParams.division
        url = UrlBuilder.api("/laws/#{$rootScope.currentLawCode}/toc")
        $http.get(url).then (response) ->
            $scope.tocData = response.data

    switch $rootScope.currentLawCode
        when 'ors'
            $scope.tocChildTemplate = UrlBuilder.template('toc_ors.html')
