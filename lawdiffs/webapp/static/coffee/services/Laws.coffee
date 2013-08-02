angular.module(SERVICES_MODULE).factory 'Laws', ($http, UrlBuilder) ->
    class Laws

        fetch: ->
            $http.get(UrlBuilder.apiUrl('/laws/or'))

    return new Laws()
