angular.module(SERVICES_MODULE).factory 'Laws', ($http, $q, UrlBuilder) ->
    class Laws

        fetchAll: ->
            $http.get(UrlBuilder.apiUrl('/laws/ors'))

        fetchLaw: (version, section) ->
            $http.get(UrlBuilder.apiUrl("/law/ors/#{version}/#{section}"))

        fetchDiff: (lawCode, section, version1, version2) ->
            $http.get UrlBuilder.apiUrl("/diff/#{lawCode}/#{section}/#{version1}/#{version2}")                    


    return new Laws()
