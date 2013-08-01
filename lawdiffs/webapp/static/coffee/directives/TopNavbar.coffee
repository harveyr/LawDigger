angular.module(DIRECTIVE_MODULE).directive 'topNavbar', ($location) ->
    directive =
        replace: true
        template: """
            <div class="navbar">
                <div class="navbar-inner">
                    <a class="brand" href="#">{{appName}}</a>
                    <ul class="nav">
                        <li ng-repeat="link in navLinks"
                            ng-class="{active: currentPath == link.href}">
                                <a href="{{link.href}}">{{link.title}}</a>
                        </li>
                    </ul>
                </div>
            </div>
        """
        link: (scope) ->
            scope.navLinks = [
                {
                    href: '/'
                    title: 'Home'
                }
            ]

            # http://docs.angularjs.org/api/ng.$route
            scope.$on "$routeChangeSuccess", (e, current, previous) ->
                scope.currentPath = $location.path()



