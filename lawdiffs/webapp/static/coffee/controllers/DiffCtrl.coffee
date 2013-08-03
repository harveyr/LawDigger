angular.module('myLilApp').controller 'DiffCtrl', ($route, $scope, $rootScope, $http, $routeParams, $location, Laws, UrlBuilder) ->
    console.log 'DiffCtrl'
    $scope.m = {}

    if $routeParams.version2
        $scope.lawCode = $routeParams.lawCode
        $scope.subsection = $routeParams.subsection
        $scope.m.version1 = $routeParams.version1
        $scope.m.version2 = $routeParams.version2
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
                    $scope.availableVersions = response.data.versions
                    console.log '$scope.version2Title:', $scope.version2Title
    else
        fetchLaws()

