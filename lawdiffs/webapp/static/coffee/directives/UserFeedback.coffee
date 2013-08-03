angular.module(DIRECTIVE_MODULE).directive 'userFeedback', () ->
    directive =
        replace: true
        scope: true
        template: """
        <div class="row" ng-show="m.html">
            <div data-alert class="small-12 columns alert-box">
                {{m.html}}
                <a href="#" class="close">&times;</a>
            </div>
        </div>
        """
        link: (scope) ->
            scope.m = {}
            scope.showUserFeedback = false

            setFeedback = (html, alertClass, iconClass) ->
                scope.m.html = html
                scope.m.alertClass = alertClass
                scope.m.iconClass = iconClass

            scope.$on 'feedback', (html, alertClass, iconClass) ->
                setFeedback html, alertClass, iconClass

            scope.$on 'successFeedback', (e, html) ->
                setFeedback html, 'alert-success', 'icon-thumbs-up'

            scope.$on 'errorFeedback', (e, html) ->
                setFeedback html, 'alert-error', 'icon-exclamation-sign'

            scope.$on 'warnFeedback', (e, html) ->
                console.log 'here'
                setFeedback html, '', 'icon-info-sign'

            scope.$on 'clearFeedback', (e) ->
                setFeedback null, '', ''
