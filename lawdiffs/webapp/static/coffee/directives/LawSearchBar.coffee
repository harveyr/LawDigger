angular.module(DIRECTIVE_MODULE).directive 'lawSearch', ($rootScope, Laws) ->
    directive =
        replace: true
        scope: true
        template: """
        <div>
            <form>
                <div class="row collapse">
                    <div class="small-2 columns">
                        <span class="prefix">
                            Search {{lawCode}}
                        </span>
                    </div>
                    <div class="small-10 columns">
                        <input type="text"
                            placeholder="Enter subsection, title, or both"
                            ng-change="inputChange()"
                            ng-model="m.lawInput"
                            autofocus>
                    </div>
                </div>
            </form>

            <div class="row" ng-show="m.lawInput && !hideSearchList">
                <div class="small-10 small-offset-2 columns panel">
                    <p>
                        <strong>Best Matches</strong>
                    </p>
                    <div class="row" ng-repeat="l in laws | filter:m.lawInput | limitTo: 10">
                        <div class="small-12 columns">
                            <a ng-click="click(l.subsection); $event.stopPropagation()">
                                ORS {{l.subsection}} {{l.titles[m.selectedVersion]}}
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        link: (scope) ->
            scope.m = {}
            scope.lawCode = $rootScope.currentLawCode

            scope.inputChange = ->
                if not scope.laws
                    scope.laws = Laws.fetchAll()

            scope.click = (section) ->
                scope.$emit 'lawNavClick', section

