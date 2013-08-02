angular.module(DIRECTIVE_MODULE).directive 'inlineDiff', () ->
    directive =
        replace: true
        scope:
            lines: '='
        template: """
        <div class="row diff-container">
            <div ng-repeat="line in lines" inline-diff-line line="line"></div>
        </div>
        """
        link: (scope) ->
            # pass

