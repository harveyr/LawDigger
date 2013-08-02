angular.module(SERVICES_MODULE).factory 'Laws', ($http, $q, UrlBuilder) ->
    class Laws

        fetch: ->
            deferred = $q.defer()
            $http.get(UrlBuilder.apiUrl('/laws/or'))
                .success (response) ->
                    deferred.resolve response
            deferred.promise

    return new Laws()
