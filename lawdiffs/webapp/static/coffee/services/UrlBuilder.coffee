angular.module(SERVICES_MODULE).factory 'UrlBuilder', () ->
    class UrlBuilder
        API_PREFIX: '/api'

        apiUrl: (url) ->
            return @API_PREFIX + url

        diffPage: (lawCode, subsection, version1, version2) ->
            "/diff/#{lawCode}/#{subsection}/#{version1}/#{version2}"

    new UrlBuilder()
