angular.module(DIRECTIVE_MODULE).directive 'inlineDiffLine', () ->
    directive =
        scope:
            line: '='
        template: """
        <div class="small-12 columns" ng-class="diffClass">
            {{line}}
        </div>
        """
        link: (scope) ->
            firstChar = scope.line.charAt(0)
            if firstChar == '-'
                scope.diffClass = 'diff-subtraction'
            else if firstChar == '+'
                scope.diffClass = 'diff-addition'

