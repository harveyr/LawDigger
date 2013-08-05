angular.module('myLilApp').controller 'DiffCtrl', ($route, $scope, $rootScope, $http, $routeParams, $location, Laws, UrlBuilder, Sorter) ->
    $scope.m = {}

    console.log '$rootScope.currentLawCode:', $rootScope.currentLawCode

    updateLegendDiffLines = ->
        version1 = $routeParams.version1
        version2 = $routeParams.version2
        $scope.legendDiffLines = [
            "- Text removed between #{version1} and #{version2}" 
            "+ Text added between #{version1} and #{version2}" 
        ]

    $scope.versionChange = ->
        $scope.$broadcast 'clearFeedback'
        if $scope.m.version1 == $scope.m.version2
            $scope.$broadcast 'warnFeedback',
                'You must choose different versions to compare.'
            $scope.showUpdateButton = false
            return

        $scope.showUpdateButton = (
            $scope.m.version1 != $routeParams.version1 or
            $scope.m.version2 != $routeParams.version2
        )
                
    $scope.updatePath = ->
        path = UrlBuilder.diffPage $scope.lawCode,
            $scope.subsection,
            $scope.m.version1,
            $scope.m.version2
        $location.path(path)

    # Handle route
    if $routeParams.version2
        $scope.lawCode = $routeParams.lawCode
        $scope.subsection = $routeParams.subsection
        $scope.m.version1 = $routeParams.version1
        $scope.m.version2 = $routeParams.version2
        $scope.currentVersion1 = $routeParams.version1
        $scope.currentVersion2 = $routeParams.version2

        Laws.fetchDiff($scope.lawCode,
            $scope.subsection,
            $scope.m.version1,
            $scope.m.version2)
                .then (response) ->
                    $scope.diffText = response.data.diff
                    $scope.diffLines = response.data.lines
                    $scope.nextSubsection = response.data.next
                    $scope.prevSubsection = response.data.prev
                    $scope.version2Title = response.data.version2_title
                    $scope.availableVersions = Sorter.sortVersions response.data.versions

                    updateLegendDiffLines()
        if $rootScope.currentLawCode and $rootScope.currentSection
            Laws.fetchVersions($rootScope.currentLawCode, $rootScope.currentSection).then (versions) ->
                console.log 'versions:', versions
        # else
        #     promise = Laws.fetchAll().then (laws) ->
        #         console.log 'laws:', laws

        # url = UrlBuilder.diffPage $rootScope.currentLawCode,
        #     $rootScope.currentSection,
        #     $rootScope.currentVersion

    $scope.lawNavClick = (section) ->
        if $scope.currentVersion1 and $scope.currentVersion2
            url = UrlBuilder.diffPage $rootScope.currentLawCode,
                section,
                $scope.currentVersion1
                $scope.currentVersion2
            $location.path(url)
        else
            Laws.fetchVersions($rootScope.currentLawCode, section)
                .then (versions) ->
                    url = UrlBuilder.diffPage $rootScope.currentLawCode,
                        section,
                        Math.min.apply(null, versions),
                        Math.max.apply(null, versions)
                    $location.path(url)


    $scope.$on 'lawNavClick', (e, section) ->
        $scope.lawNavClick(section)

