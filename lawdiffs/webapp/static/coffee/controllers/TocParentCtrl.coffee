angular.module(APP_NAME).controller 'TocParentCtrl', ($route, $scope, $rootScope, $http, $routeParams, UrlBuilder) ->
    $scope.m = {}

    if not $scope.tocData and not $routeParams.division
        url = UrlBuilder.api("/laws/#{$rootScope.currentLawCode}/toc")
        $http.get(url)
            .success (data) ->
                $scope.tocData = data
                if not $rootScope.currentVersion
                    $rootScope.currentVersion = data.versions[0]
                $scope.m.selectedVersion = $rootScope.currentVersion

    switch $rootScope.currentLawCode
        when 'ors'
            $scope.tocChildTemplate = UrlBuilder.template('toc_ors.html')
