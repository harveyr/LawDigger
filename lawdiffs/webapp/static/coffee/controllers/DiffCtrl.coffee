angular.module('myLilApp').controller 'DiffCtrl', ($route, $scope, $rootScope, $http, $routeParams, $location, Laws, UrlBuilder, Sorter) ->
    $scope.m = {}

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
    else
        fetchLaws()

    $scope.$on 'navClick', (e, section) ->
        url = UrlBuilder.diffPage $scope.lawCode,
            section,
            $scope.currentVersion1
            $scope.currentVersion2
        $location.path(url)
