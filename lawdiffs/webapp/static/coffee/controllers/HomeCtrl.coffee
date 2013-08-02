angular.module('myLilApp').controller 'HomeCtrl', ($scope, $http, $rootScope, Laws) ->
    $scope.laws = Laws.fetch()
