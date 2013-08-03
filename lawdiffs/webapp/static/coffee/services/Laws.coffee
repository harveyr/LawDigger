angular.module(SERVICES_MODULE).factory 'Laws', ($http, $q, UrlBuilder, Sorter) ->
    class Laws

        fetchAll: ->
            $http.get(UrlBuilder.apiUrl('/laws/ors'))

        fetchLaw: (version, section) ->
            $http.get(UrlBuilder.apiUrl("/law/ors/#{version}/#{section}"))

        fetchVersions: (lawCode, section) ->
            deferred = $q.defer()
            $http.get(UrlBuilder.apiUrl("/versions/#{lawCode}/#{section}"))
                .success (data) ->
                    deferred.resolve Sorter.sortVersions data.versions
            deferred.promise

        nearestVersion: (lawCode, section, version) ->
            deferred = $q.defer()
            @fetchVersions(lawCode, section, version).then (versions) ->
                if _.in versions, version
                    deferred.resolve version
                    return

                nearestVersion = null
                minDifference = 10000
                _.each versions, (candidateVersion) ->
                    diff = Math.abs(version - candidateVersion)
                    if  diff < minDifference
                        nearestVersion = candidateVersion
                        minDifference = diff
                if not nearestVersion
                    throw "Failed to find nearest version: #{lawCode}, #{section}, #{version}"
                deferred.resolve nearestVersion

            deferred.promise

        fetchDiff: (lawCode, section, version1, version2) ->
            $http.get UrlBuilder.apiUrl("/diff/#{lawCode}/#{section}/#{version1}/#{version2}")                    


    return new Laws()
