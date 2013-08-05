angular.module(APP_NAME).controller 'OrsTocCtrl', ($route, $scope, $rootScope, $http, $routeParams, Laws, UrlBuilder) ->

    $scope.chapterLinkBase = UrlBuilder.app("/toc/#{$rootScope.currentLawCode}/#{$rootScope.currentVersion}")

    if $routeParams.division
        chapter = $routeParams.division
        promise = Laws.fetchDivision $rootScope.currentLawCode, chapter
        promise.then (data) ->
            $scope.currentChapter = data.chapter
            $scope.chapterStatutes = data.statutes

