angular.module(SERVICES_MODULE).factory 'UrlBuilder', () ->
    class UrlBuilder
        API_PREFIX: '/api'

        apiUrl: (url) ->
            return @API_PREFIX + url

    new UrlBuilder()
