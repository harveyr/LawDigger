angular.module(DIRECTIVE_MODULE).directive 'lawHeader', () ->
    directive =
        replace: true
        restrict: 'A'
        template: """
        <div class="law-title">
            <div>
                <h4>
                    {{code | uppercase}} {{subsection}}.
                    <span class="subheader">{{title}}</span>
                </h4>
            </div>
        </div>
        """
        link: (scope, elem, attrs) ->
            attrs.$observe 'title', (title) ->
                scope.title = title

            attrs.$observe 'subsection', (subsection) ->
                scope.subsection = subsection

            attrs.$observe 'code', (code) ->
                scope.code = code

