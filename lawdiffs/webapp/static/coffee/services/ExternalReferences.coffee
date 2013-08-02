angular.module(SERVICES_MODULE).factory 'ExternalReferences', () ->
    class ExternalReferences
        
        orsVersionPaths:
            2001: '/ors_archives/2001ORS'

        sourceLink: (lawCode, version, subsection) ->
            if lawCode == 'ors'
                url = 'http://www.leg.state.or.us/ors/'


    new ExternalReferences
