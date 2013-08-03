angular.module(SERVICES_MODULE).factory 'UrlBuilder', ($rootScope) ->
    class UrlBuilder
        API_PREFIX: '/api'

        apiUrl: (url) ->
            return @API_PREFIX + url

        viewPage: (subsection, lawCode = null, version = null) ->
            if not lawCode
                if not $rootScope.currentLawCode
                    throw 'No code found in args or rootScope'
                lawCode = $rootScope.currentLawCode

            if not version
                if not $rootScope.currentVersion
                    throw 'No version in args or rootScope'
                version = $rootScope.currentVersion
            "/view/#{lawCode}/#{version}/#{subsection}"

        diffPage: (lawCode, subsection, version1, version2) ->
            "/diff/#{lawCode}/#{subsection}/#{version1}/#{version2}"

    new UrlBuilder()
