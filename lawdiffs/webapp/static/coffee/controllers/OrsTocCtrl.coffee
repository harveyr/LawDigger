angular.module(APP_NAME).controller 'OrsTocCtrl', ($route, $scope, $rootScope, $http, $routeParams, Laws, UrlBuilder) ->

    lawCode = $rootScope.currentLawCode
    version = $rootScope.currentVersion

    $scope.chapterLinkBase = UrlBuilder.app "/toc/#{lawCode}/#{version}"

    $scope.statuteLinkBase = UrlBuilder.app "/view/#{lawCode}/#{version}"

    if $routeParams.division
        chapter = $routeParams.division
        promise = Laws.fetchDivision $rootScope.currentLawCode, chapter
        promise.then (data) ->
            $scope.currentChapter = data.chapter
            $scope.chapterStatutes = data.statutes

