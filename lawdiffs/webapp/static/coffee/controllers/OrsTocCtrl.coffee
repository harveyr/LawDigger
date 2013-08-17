angular.module(APP_NAME).controller 'OrsTocCtrl', ($route, $scope, $rootScope, $http, $routeParams, Laws, UrlBuilder) ->
    lawCode = $rootScope.currentLawCode
    version = $rootScope.currentVersion
    $scope.chapterLinkBase = UrlBuilder.app "/toc/#{lawCode}/#{version}"
    $scope.statuteLinkBase = UrlBuilder.app "/view/#{lawCode}/#{version}"

    simpleNumPat = /\d+/

    if $routeParams.division
        chapter = $routeParams.division
        promise = Laws.fetchDivision $rootScope.currentLawCode, chapter
        promise.then (data) ->
            $scope.currentChapter = data.chapter
            $scope.chapterStatutes = data.statutes

    getChapterVolume = (chapterStr) ->
        chapterNum = simpleNumPat.exec(chapterStr)
        if not chapterNum
            throw "No number found for chapter #{chapterStr}"
        chapterNum = chapterNum[0]
        volume = _.find $scope.tocData.volumes, (volume) ->
            return chapterNum >= volume.chapters[0] and chapterNum <= volume.chapters[1]
        volume

    $scope.searchInputChange = (searchInput) ->
        subsectionPat = /\d+\.\d+/
        subs = subsectionPat.exec searchInput
        if subs
            subs = subs[0]
            $scope.interpretedSearch = "ORS #{subs}"
            parts = subs.split('.')
            $scope.searchChapter = parts[0]
            $scope.searchSubsection = parts[1]
            $scope.searchVolume = getChapterVolume($scope.searchChapter)

        else
            $scope.interpretedSearch = "Type some more ..."


    $scope.$watch 'tocData', ->
        _.each $scope.tocData.volumes, (val, key, list) ->
            $scope.tocData.volumes[key]['volume'] = key


