angular.module(SERVICES_MODULE).factory 'Laws', ($http, $q, UrlBuilder) ->
    class Laws

        fetchAll: ->
            $http.get(UrlBuilder.apiUrl('/laws/or'))

        fetchLaw: (id, version) ->
            $http.get(UrlBuilder.apiUrl("/law/or/#{id}/#{version}"))
                    

    return new Laws()
