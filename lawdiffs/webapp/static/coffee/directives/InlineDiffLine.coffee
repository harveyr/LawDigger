angular.module(DIRECTIVE_MODULE).directive 'inlineDiffLine', () ->
    directive =
        scope:
            line: '='
            first: '='
        template: """
        <div class="diff-line-inline" ng-class="diffClass">
            {{line}}
        </div>
        """
        link: (scope) ->
            firstChar = scope.line.charAt(0)
            diffClass = ''
            if firstChar == '-'
                diffClass = 'diff-subtraction'
            else if firstChar == '+'
                diffClass = 'diff-addition'

            if scope.first
                diffClass += ' first-line'
            scope.diffClass = diffClass
            console.log 'scope.diffClass:', scope.diffClass

