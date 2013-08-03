angular.module('myLilApp').controller 'ViewerCtrl', ($route, $scope, $rootScope, $http, $routeParams, $location, Laws, UrlBuilder) ->
    console.log 'ViewerCtrl'
    $scope.m = {}
    fetchedLaws = false

    applyLaw = (law) ->
        $scope.activeText = law.text
        $scope.activeTitle = law.title
        $scope.availableVersions = law.versions.sort (a, b) ->
            return parseInt(b) - parseInt(a)
        $scope.previousSection = law.prev
        $scope.nextSection = law.next

    fetchAllLaws = ->
        Laws.fetchAll().then (response) ->
            laws = _.sortBy response.data, (law) ->
                law.subsection
            $scope.allLaws = laws

    fetchAndApplyLaw = (version, section) ->
        Laws.fetchLaw(version, section).then (response) ->
            applyLaw response.data

    $scope.chooseLaw = (law) ->
        $scope.currentLaw = law
        $scope.hideSearchList = true
        $scope.m.primaryYear = _.max law.versions
        fetchAndApplyLaw law.id, $scope.m.primaryYear

    $scope.lawFilterChange = ->
        $scope.hideSearchList = false
        if not fetchedLaws
            fetchAllLaws()
            fetchedLaws = true

    $scope.diffMe = ->
        url = UrlBuilder.diffPage 'ors', $scope.activeSection,
            $scope.availableVersions[$scope.availableVersions.length - 1],
            $scope.availableVersions[0]
        $location.path(url)

    $scope.choosePrimaryYear = (year) ->
        $scope.m.primaryYear = year

    # fetchAllLaws()

    $scope.selectedVersionChange = (version) ->
        $location.path("/view/ors/#{version}/#{$scope.activeSection}")

    # Handle route
    if $routeParams.section
        $scope.activeVersion = $routeParams.version
        $scope.m.selectedVersion = $routeParams.version
        $scope.activeSection = $routeParams.section
        fetchAndApplyLaw $scope.activeVersion, $scope.activeSection
    else
        $scope.m.selectedVersion = 2011
        fetchAllLaws()

    $scope.$on 'navClick', (e, section) ->
        promise = Laws.nearestVersion $routeParams.lawCode,
            section, $routeParams.version
        promise.then (version) ->
            url = UrlBuilder.viewPage $routeParams.lawCode, version, section
            $location.path(url)
