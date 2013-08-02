angular.module('myLilApp').controller 'DiffCtrl', ($route, $scope, $rootScope, $http, $routeParams, $location, Laws) ->
    console.log 'DiffCtrl'
    $scope.m = {}

    # fetchLaws = ->
    #     Laws.fetchAll().then (response) ->
    #         laws = _.sortBy response.data, (law) ->
    #             law.subsection
    #         $scope.laws = laws

    # fetchAndApplyLaw = (version, section) ->
    #     Laws.fetchLaw(version, section).then (response) ->
    #         $scope.activeText = response.data.text
    #         $scope.activeTitle = response.data.title
    #         $scope.availableVersions = response.data.versions.sort (a, b) ->
    #             return parseInt(b) - parseInt(a)

    # $scope.chooseLaw = (law) ->
    #     console.log 'law:', law
    #     $scope.currentLaw = law
    #     $scope.hideSearchList = true
    #     $scope.m.primaryYear = _.max law.versions
    #     fetchAndApplyLaw law.id, $scope.m.primaryYear

    # $scope.lawFilterChange = ->
    #     $scope.hideSearchList = false

    # $scope.choosePrimaryYear = (year) ->
    #     $scope.m.primaryYear = year

    # # fetchLaws()

    # $scope.selectedVersionChange = (version) ->
    #     $location.path("/view/ors/#{version}/#{$scope.activeSection}")

    if $routeParams.version2
        $scope.lawCode = $routeParams.lawCode
        $scope.subsection = $routeParams.subsection
        $scope.version1 = $routeParams.version1
        $scope.version2 = $routeParams.version2
        Laws.fetchDiff($scope.lawCode, $scope.subsection, $scope.version1, $scope.version2)
            .then (response) ->
                $scope.diffText = response.data.diff
                $scope.diffLines = response.data.lines
    else
        fetchLaws()

