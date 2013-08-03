angular.module(SERVICES_MODULE).factory 'Sorter', () ->
    class Sorter
        sortVersions: (versions) ->
            return versions.sort (a, b) ->
                return parseInt(b) - parseInt(a)

    new Sorter()
