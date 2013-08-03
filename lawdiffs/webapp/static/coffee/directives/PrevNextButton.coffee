angular.module(DIRECTIVE_MODULE).directive 'prevNextButton', () ->
    directive =
        replace: true
        scope: true
        template: """
        <div ng-class="parentClass">
            <a ng-click="click()">
                <span ng-show="isPrev" ng-bind-html-unsafe="navChar"></span>
                {{section}}
                <span ng-show="isNext" ng-bind-html-unsafe="navChar"></span>
            </a>
        </div>
        """
        link: (scope, elem, attrs) ->
            attrs.$observe 'prevNextButton', (section) ->
                scope.section = section

            if _.has attrs, 'prev'
                scope.isPrev = true
                scope.parentClass = 'prev'
                scope.navChar = '&laquo;'
            else if _.has attrs, 'next'
                scope.isNext = true
                scope.parentClass = 'next'
                scope.navChar = '&raquo;'
            else
                throw "Can't figure out prevNextButton type!"

            scope.click = ->
                if scope.isNext
                    scope.$emit 'nextNavClick'
                else if scope.isPrev
                    scope.$emit 'prevNavClick'
