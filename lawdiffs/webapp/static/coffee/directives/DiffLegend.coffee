angular.module(DIRECTIVE_MODULE).directive 'diffLegend', () ->
    directive =
        scope: 
            vOne: '='
            vTwo: '='
        replace: true
        template: """
        <div>
            <div class="diff-legend-header">
                <table>
                    <thead>
                        <tr>
                            <th>Legend</th>
                        </tr>
                    </thead>
                </table>
            </div>
            <div class="diff-container">
                <div ng-repeat="line in lines" inline-diff-line line="line"></div>
            </div>
        </div>
        """
        link: (scope) ->
            scope.lines = [
                "- (Text removed between #{scope.vOne} and #{scope.vTwo})"
                "+ (Text added between #{scope.vOne} and #{scope.vTwo})"
            ]
