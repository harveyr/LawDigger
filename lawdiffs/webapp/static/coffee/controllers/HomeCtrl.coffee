angular.module('myLilApp').controller 'HomeCtrl', ($scope, $http, $rootScope, Laws) ->
    $scope.m = {}

    fetchAndApplyLaw = (lawId, version) ->
        Laws.fetchLaw(lawId, version).then (response) ->
            console.log 'data:', response.data
            $scope.currentLaw = response.data

    $scope.chooseLaw = (law) ->
        console.log 'law:', law
        $scope.currentLaw = law
        $scope.hideSearchList = true
        $scope.m.primaryYear = _.max law.versions
        fetchAndApplyLaw law.id, $scope.m.primaryYear

    $scope.lawFilterChange = ->
        $scope.hideSearchList = false

    $scope.choosePrimaryYear = (year) ->
        $scope.m.primaryYear = year


    Laws.fetchAll().then (data) ->
        $scope.laws = data

