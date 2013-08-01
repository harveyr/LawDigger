angular.module(DIRECTIVE_MODULE).directive 'userFeedback', () ->
    directive =
        template: """
            <div class="row-fluid" ng-show="fbModel.html">
                <div class="span12 alert {{fbModel.alertClass}}">
                    <span class="{{fbModel.iconClass}}" ng-show="fbModel.iconClass"></span>
                    <span ng-bind-html-unsafe="fbModel.html"></span>
                </div>
            </div>
        """
        link: (scope) ->
            scope.fbModel = {}
            setFeedback = (html, alertClass, iconClass) ->
                scope.fbModel.html = html
                scope.fbModel.alertClass = alertClass
                scope.fbModel.iconClass = iconClass

            scope.$on 'feedback', (html, alertClass, iconClass) ->
                setFeedback html, alertClass, iconClass

            scope.$on 'successFeedback', (e, html) ->
                setFeedback html, 'alert-success', 'icon-thumbs-up'

            scope.$on 'errorFeedback', (e, html) ->
                setFeedback html, 'alert-error', 'icon-exclamation-sign'

            scope.$on 'warnFeedback', (e, html) ->
                setFeedback html, '', 'icon-info-sign'

            scope.$on 'clearFeedback', (e) ->
                setFeedback null, '', ''
