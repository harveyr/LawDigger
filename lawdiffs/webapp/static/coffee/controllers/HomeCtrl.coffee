angular.module('myLilApp').controller 'HomeCtrl', ($scope, $http, $rootScope, Laws) ->
    $scope.m = {}

    Laws.fetch().then (data) ->
        $scope.laws = data

    $scope.chooseLaw = (law) ->
        console.log 'law:', law
        $scope.currentLaw = law
        $scope.hideSearchList = true
        $scope.m.primaryYear = _.max law.versions

    $scope.lawFilterChange = ->
        $scope.hideSearchList = false

    $scope.choosePrimaryYear = (year) ->
        $scope.m.primaryYear = year
