angular.module(DIRECTIVE_MODULE).directive 'inlineDiffLine', () ->
    directive =
        scope:
            line: '='
            first: '='
        replace: true
        template: """
        <table class="diff-line-table">
            <tr ng-class="diffClass">
                <td class="plus-minus">{{plusMinus}}</td>
                <td class="diff-text"><pre>{{text}}</pre></td>
            </tr>
        </table>
        """
        link: (scope) ->
            firstChar = scope.line.charAt(0)
            diffClass = ''
            if firstChar == '-'
                diffClass = 'diff-subtraction'
                scope.plusMinus = '-'
                scope.text = scope.line.substring(1)
            else if firstChar == '+'
                diffClass = 'diff-addition'
                scope.plusMinus = '+'
                scope.text = scope.line.substring(1)
            else
                scope.text = scope.line

            if scope.first
                diffClass += ' first-line'
            scope.diffClass = diffClass

