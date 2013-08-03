angular.module(DIRECTIVE_MODULE).directive 'inlineDiff', () ->
    directive =
        scope:
            lines: '='
        replace: true
        template: """
        <div class="diff-container">
            <div ng-repeat="line in lines" inline-diff-line line="line" first="$first"></div>
        </div>
        """
        link: (scope) ->
            # pass
