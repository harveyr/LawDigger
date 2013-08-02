angular.module('myLilApp').controller 'HomeCtrl', ($scope, $http, $rootScope, Laws) ->
    $scope.m = {}

    Laws.fetch().then (data) ->
        $scope.laws = data
        console.log '$scope.laws:', $scope.laws


    $scope.chooseLaw = (id) ->
        $scope.currentLawId = id
        $scope.hideSearchList = true

