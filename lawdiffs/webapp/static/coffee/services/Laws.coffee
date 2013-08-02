angular.module(SERVICES_MODULE).factory 'Laws', ($http, $q, UrlBuilder) ->
    class Laws

        fetchAll: ->
            deferred = $q.defer()
            $http.get(UrlBuilder.apiUrl('/laws/or'))
                .success (response) ->
                    deferred.resolve response
            deferred.promise

        fetchLaw: (id, version) ->
            $http.get(UrlBuilder.apiUrl("/law/or/#{id}/#{version}"))
                    

    return new Laws()
