angular.module('myLilApp').controller 'HomeCtrl', ($scope, $http, $rootScope, Laws) ->
    Laws.fetch().then (data) ->
        $scope.laws = data
        console.log '$scope.laws:', $scope.laws
