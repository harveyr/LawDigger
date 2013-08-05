angular.module(APP_NAME).controller 'TocParentCtrl', ($route, $scope, $rootScope, $http, UrlBuilder) ->
    $scope.m = {}

    $http.get(UrlBuilder.api("/laws/#{$rootScope.currentLawCode}/toc"))
        .success (data) ->
            $scope.tocData = data
            $scope.m.selectedVersion = data.versions[0]

    switch $rootScope.currentLawCode
        when 'ors'
            $scope.tocChildTemplate = UrlBuilder.template('toc_ors.html')
