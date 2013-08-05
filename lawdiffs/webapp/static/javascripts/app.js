// Generated by CoffeeScript 1.6.3
(function() {
  var APP_NAME, APP_PREFIX, DIRECTIVE_MODULE, PARTIALS_PREFIX, SERVICES_MODULE, app;

  APP_NAME = 'lawDiggerApp';

  APP_PREFIX = '/app';

  PARTIALS_PREFIX = '/static/partials';

  DIRECTIVE_MODULE = "" + APP_NAME + ".directives";

  SERVICES_MODULE = "" + APP_NAME + ".directives";

  angular.module(DIRECTIVE_MODULE, []);

  angular.module(SERVICES_MODULE, []);

  angular.module(DIRECTIVE_MODULE).directive('diffLegend', function() {
    var directive;
    return directive = {
      scope: {
        vOne: '=',
        vTwo: '='
      },
      replace: true,
      template: "<div>\n    <div class=\"diff-legend-header\">\n        <table>\n            <thead>\n                <tr>\n                    <th>Legend</th>\n                </tr>\n            </thead>\n        </table>\n    </div>\n    <div class=\"diff-container\">\n        <div ng-repeat=\"line in lines\" inline-diff-line line=\"line\"></div>\n    </div>\n</div>",
      link: function(scope) {
        return scope.lines = ["- (Text removed between " + scope.vOne + " and " + scope.vTwo + ")", "+ (Text added between " + scope.vOne + " and " + scope.vTwo + ")"];
      }
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('inlineDiff', function() {
    var directive;
    return directive = {
      scope: {
        lines: '='
      },
      replace: true,
      template: "<div class=\"diff-container\">\n    <div ng-repeat=\"line in lines\" inline-diff-line line=\"line\" first=\"$first\"></div>\n</div>",
      link: function(scope) {}
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('inlineDiffLine', function() {
    var directive;
    return directive = {
      scope: {
        line: '=',
        first: '='
      },
      replace: true,
      template: "<table class=\"diff-line-table\">\n    <tr ng-class=\"diffClass\">\n        <td class=\"plus-minus\">{{plusMinus}}</td>\n        <td class=\"diff-text\"><pre>{{text}}</pre></td>\n    </tr>\n</table>",
      link: function(scope) {
        var diffClass, firstChar;
        firstChar = scope.line.charAt(0);
        diffClass = '';
        if (firstChar === '-') {
          diffClass = 'diff-subtraction';
          scope.plusMinus = '-';
          scope.text = scope.line.substring(1);
        } else if (firstChar === '+') {
          diffClass = 'diff-addition';
          scope.plusMinus = '+';
          scope.text = scope.line.substring(1);
        } else {
          scope.text = scope.line;
        }
        if (scope.first) {
          diffClass += ' first-line';
        }
        return scope.diffClass = diffClass;
      }
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('lawHeader', function() {
    var directive;
    return directive = {
      replace: true,
      restrict: 'A',
      template: "<div class=\"law-title\">\n    <div>\n        <h4>\n            {{code | uppercase}} {{subsection}}.\n            <span class=\"subheader\">{{title}}</span>\n        </h4>\n    </div>\n</div>",
      link: function(scope, elem, attrs) {
        attrs.$observe('title', function(title) {
          return scope.title = title;
        });
        attrs.$observe('subsection', function(subsection) {
          return scope.subsection = subsection;
        });
        return attrs.$observe('code', function(code) {
          return scope.code = code;
        });
      }
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('lawSearch', function($rootScope, Laws) {
    var directive;
    return directive = {
      replace: true,
      scope: true,
      template: "<div>\n    <form>\n        <div class=\"row collapse\">\n            <div class=\"small-2 columns\">\n                <span class=\"prefix\">\n                    Search {{lawCode}}\n                </span>\n            </div>\n            <div class=\"small-10 columns\">\n                <input type=\"text\"\n                    placeholder=\"Enter subsection, title, or both\"\n                    ng-change=\"inputChange()\"\n                    ng-model=\"m.lawInput\"\n                    autofocus>\n            </div>\n        </div>\n    </form>\n\n    <div class=\"row\" ng-show=\"m.lawInput && !hideSearchList\">\n        <div class=\"small-10 small-offset-2 columns panel\">\n            <p>\n                <strong>Best Matches</strong>\n            </p>\n            <div class=\"row\" ng-repeat=\"l in laws | filter:m.lawInput | limitTo: 10\">\n                <div class=\"small-12 columns\">\n                    <a ng-click=\"click(l.subsection); $event.stopPropagation()\">\n                        ORS {{l.subsection}} {{l.titles[m.selectedVersion]}}\n                    </a>\n                </div>\n            </div>\n        </div>\n    </div>\n</div>",
      link: function(scope) {
        scope.m = {};
        scope.lawCode = $rootScope.currentLawCode;
        scope.inputChange = function() {
          if (!scope.laws) {
            return scope.laws = Laws.fetchAll();
          }
        };
        return scope.click = function(section) {
          return scope.$emit('lawNavClick', section);
        };
      }
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('prevNextButton', function() {
    var directive;
    return directive = {
      replace: true,
      scope: true,
      template: "<div ng-class=\"parentClass\" ng-show=\"section\">\n    <a ng-click=\"click()\">\n        <span ng-show=\"isPrev\" ng-bind-html-unsafe=\"navChar\"></span>\n        {{section}}\n        <span ng-show=\"isNext\" ng-bind-html-unsafe=\"navChar\"></span>\n    </a>\n</div>",
      link: function(scope, elem, attrs) {
        attrs.$observe('prevNextButton', function(section) {
          return scope.section = section;
        });
        if (_.has(attrs, 'prev')) {
          scope.isPrev = true;
          scope.parentClass = 'prev';
          scope.navChar = '&laquo;';
        } else if (_.has(attrs, 'next')) {
          scope.isNext = true;
          scope.parentClass = 'next';
          scope.navChar = '&raquo;';
        } else {
          throw "Can't figure out prevNextButton type!";
        }
        return scope.click = function() {
          if (scope.isNext) {
            return scope.$emit('lawNavClick', scope.section);
          } else if (scope.isPrev) {
            return scope.$emit('lawNavClick', scope.section);
          }
        };
      }
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('topNavbar', function($location) {
    var directive;
    return directive = {
      replace: true,
      template: "<div class=\"navbar\">\n    <div class=\"navbar-inner\">\n        <a class=\"brand\" href=\"#\">{{appName}}</a>\n        <ul class=\"nav\">\n            <li ng-repeat=\"link in navLinks\"\n                ng-class=\"{active: currentPath == link.href}\">\n                    <a href=\"{{link.href}}\">{{link.title}}</a>\n            </li>\n        </ul>\n    </div>\n</div>",
      link: function(scope) {
        scope.navLinks = [
          {
            href: '/',
            title: 'Home'
          }
        ];
        return scope.$on("$routeChangeSuccess", function(e, current, previous) {
          return scope.currentPath = $location.path();
        });
      }
    };
  });

  angular.module(DIRECTIVE_MODULE).directive('userFeedback', function() {
    var directive;
    return directive = {
      replace: true,
      scope: true,
      template: "<div class=\"row\" ng-show=\"m.html\">\n    <div data-alert class=\"small-12 columns alert-box\">\n        {{m.html}}\n        <a href=\"#\" class=\"close\">&times;</a>\n    </div>\n</div>",
      link: function(scope) {
        var setFeedback;
        scope.m = {};
        scope.showUserFeedback = false;
        setFeedback = function(html, alertClass, iconClass) {
          scope.m.html = html;
          scope.m.alertClass = alertClass;
          return scope.m.iconClass = iconClass;
        };
        scope.$on('feedback', function(html, alertClass, iconClass) {
          return setFeedback(html, alertClass, iconClass);
        });
        scope.$on('successFeedback', function(e, html) {
          return setFeedback(html, 'alert-success', 'icon-thumbs-up');
        });
        scope.$on('errorFeedback', function(e, html) {
          return setFeedback(html, 'alert-error', 'icon-exclamation-sign');
        });
        scope.$on('warnFeedback', function(e, html) {
          console.log('here');
          return setFeedback(html, '', 'icon-info-sign');
        });
        return scope.$on('clearFeedback', function(e) {
          return setFeedback(null, '', '');
        });
      }
    };
  });

  angular.module(SERVICES_MODULE).factory('ExternalReferences', function() {
    var ExternalReferences;
    ExternalReferences = (function() {
      function ExternalReferences() {}

      ExternalReferences.prototype.orsVersionPaths = {
        2001: '/ors_archives/2001ORS'
      };

      ExternalReferences.prototype.sourceLink = function(lawCode, version, subsection) {
        var url;
        if (lawCode === 'ors') {
          return url = 'http://www.leg.state.or.us/ors/';
        }
      };

      return ExternalReferences;

    })();
    return new ExternalReferences;
  });

  angular.module(SERVICES_MODULE).factory('Laws', function($http, $q, UrlBuilder, Sorter) {
    var Laws;
    Laws = (function() {
      function Laws() {}

      Laws.prototype.fetchLaw = function(version, section) {
        return $http.get(UrlBuilder.apiUrl("/law/ors/" + version + "/" + section));
      };

      Laws.prototype.fetchVersions = function(lawCode, section) {
        var deferred;
        deferred = $q.defer();
        $http.get(UrlBuilder.apiUrl("/versions/" + lawCode + "/" + section)).success(function(data) {
          return deferred.resolve(Sorter.sortVersions(data.versions));
        });
        return deferred.promise;
      };

      Laws.prototype.fetchDivision = function(lawCode, division) {
        var deferred, url;
        deferred = $q.defer();
        url = UrlBuilder.api("/laws/" + lawCode + "/division/" + division);
        $http.get(url).success(function(data) {
          return deferred.resolve(data);
        });
        return deferred.promise;
      };

      Laws.prototype.nearestVersion = function(lawCode, section, version) {
        var deferred;
        deferred = $q.defer();
        this.fetchVersions(lawCode, section, version).then(function(versions) {
          var minDifference, nearestVersion;
          if (_["in"](versions, version)) {
            deferred.resolve(version);
            return;
          }
          nearestVersion = null;
          minDifference = 10000;
          _.each(versions, function(candidateVersion) {
            var diff;
            diff = Math.abs(version - candidateVersion);
            if (diff < minDifference) {
              nearestVersion = candidateVersion;
              return minDifference = diff;
            }
          });
          if (!nearestVersion) {
            throw "Failed to find nearest version: " + lawCode + ", " + section + ", " + version;
          }
          return deferred.resolve(nearestVersion);
        });
        return deferred.promise;
      };

      Laws.prototype.fetchDiff = function(lawCode, section, version1, version2) {
        return $http.get(UrlBuilder.apiUrl("/diff/" + lawCode + "/" + section + "/" + version1 + "/" + version2));
      };

      return Laws;

    })();
    return new Laws();
  });

  angular.module(SERVICES_MODULE).factory('Sorter', function() {
    var Sorter;
    Sorter = (function() {
      function Sorter() {}

      Sorter.prototype.sortVersions = function(versions) {
        return versions.sort(function(a, b) {
          return parseInt(b) - parseInt(a);
        });
      };

      return Sorter;

    })();
    return new Sorter();
  });

  angular.module(SERVICES_MODULE).factory('UrlBuilder', function($rootScope) {
    var UrlBuilder;
    UrlBuilder = (function() {
      function UrlBuilder() {}

      UrlBuilder.prototype.APP_PREFIX = APP_PREFIX;

      UrlBuilder.prototype.TEMPLATE_PREFIX = PARTIALS_PREFIX;

      UrlBuilder.prototype.API_PREFIX = '/api';

      UrlBuilder.prototype.api = function(url) {
        return this.API_PREFIX + url;
      };

      UrlBuilder.prototype.apiUrl = function(url) {
        return this.api(url);
      };

      UrlBuilder.prototype.app = function(url) {
        return this.APP_PREFIX + url;
      };

      UrlBuilder.prototype.appUrl = function(url) {
        return this.app(url);
      };

      UrlBuilder.prototype.template = function(url) {
        return this.TEMPLATE_PREFIX + ("/" + url);
      };

      UrlBuilder.prototype.viewPage = function(subsection, lawCode, version) {
        if (lawCode == null) {
          lawCode = null;
        }
        if (version == null) {
          version = null;
        }
        if (!lawCode) {
          if (!$rootScope.currentLawCode) {
            throw 'No code found in args or rootScope';
          }
          lawCode = $rootScope.currentLawCode;
        }
        if (!version) {
          if (!$rootScope.currentVersion) {
            throw 'No version in args or rootScope';
          }
          version = $rootScope.currentVersion;
        }
        return "/view/" + lawCode + "/" + version + "/" + subsection;
      };

      UrlBuilder.prototype.diffPage = function(lawCode, subsection, version1, version2) {
        return "/diff/" + lawCode + "/" + subsection + "/" + version1 + "/" + version2;
      };

      return UrlBuilder;

    })();
    return new UrlBuilder();
  });

  app = angular.module(APP_NAME, [DIRECTIVE_MODULE, SERVICES_MODULE]).run(function($route, $location, $rootScope, UrlBuilder) {
    $rootScope.appPrefix = UrlBuilder.APP_PREFIX;
    $rootScope.$on('$routeChangeSuccess', function(e, current, previous) {
      var params, path;
      path = $location.path();
      if (_.beginswith(path, '/view')) {
        $rootScope.currentNav = 'view';
      } else if (_.beginswith(path, '/diff')) {
        $rootScope.currentNav = 'diff';
      }
      params = current.params;
      if (_.has(params, 'lawCode')) {
        $rootScope.currentLawCode = params.lawCode;
      }
      if (_.has(params, 'version')) {
        return $rootScope.currentVersion = params.version;
      }
    });
    return _.mixin({
      "in": function(arr, value) {
        return arr.indexOf(value) !== -1;
      },
      beginswith: function(string_, substring_) {
        return string_.indexOf(substring_) === 0;
      }
    });
  });

  angular.module(APP_NAME).controller('DiffCtrl', function($route, $scope, $rootScope, $http, $routeParams, $location, Laws, UrlBuilder, Sorter) {
    var updateLegendDiffLines;
    $scope.m = {};
    console.log('$rootScope.currentLawCode:', $rootScope.currentLawCode);
    updateLegendDiffLines = function() {
      var version1, version2;
      version1 = $routeParams.version1;
      version2 = $routeParams.version2;
      return $scope.legendDiffLines = ["- Text removed between " + version1 + " and " + version2, "+ Text added between " + version1 + " and " + version2];
    };
    $scope.versionChange = function() {
      $scope.$broadcast('clearFeedback');
      if ($scope.m.version1 === $scope.m.version2) {
        $scope.$broadcast('warnFeedback', 'You must choose different versions to compare.');
        $scope.showUpdateButton = false;
        return;
      }
      return $scope.showUpdateButton = $scope.m.version1 !== $routeParams.version1 || $scope.m.version2 !== $routeParams.version2;
    };
    $scope.updatePath = function() {
      var path;
      path = UrlBuilder.diffPage($scope.lawCode, $scope.subsection, $scope.m.version1, $scope.m.version2);
      return $location.path(path);
    };
    if ($routeParams.version2) {
      $scope.lawCode = $routeParams.lawCode;
      $scope.subsection = $routeParams.subsection;
      $scope.m.version1 = $routeParams.version1;
      $scope.m.version2 = $routeParams.version2;
      $scope.currentVersion1 = $routeParams.version1;
      $scope.currentVersion2 = $routeParams.version2;
      Laws.fetchDiff($scope.lawCode, $scope.subsection, $scope.m.version1, $scope.m.version2).then(function(response) {
        $scope.diffText = response.data.diff;
        $scope.diffLines = response.data.lines;
        $scope.nextSubsection = response.data.next;
        $scope.prevSubsection = response.data.prev;
        $scope.version2Title = response.data.version2_title;
        $scope.availableVersions = Sorter.sortVersions(response.data.versions);
        return updateLegendDiffLines();
      });
      if ($rootScope.currentLawCode && $rootScope.currentSection) {
        Laws.fetchVersions($rootScope.currentLawCode, $rootScope.currentSection).then(function(versions) {
          return console.log('versions:', versions);
        });
      }
    }
    $scope.lawNavClick = function(section) {
      var url;
      if ($scope.currentVersion1 && $scope.currentVersion2) {
        url = UrlBuilder.diffPage($rootScope.currentLawCode, section, $scope.currentVersion1, $scope.currentVersion2);
        return $location.path(url);
      } else {
        return Laws.fetchVersions($rootScope.currentLawCode, section).then(function(versions) {
          url = UrlBuilder.diffPage($rootScope.currentLawCode, section, Math.min.apply(null, versions), Math.max.apply(null, versions));
          return $location.path(url);
        });
      }
    };
    return $scope.$on('lawNavClick', function(e, section) {
      return $scope.lawNavClick(section);
    });
  });

  angular.module(APP_NAME).controller('HomeCtrl', function($scope, $rootScope, $http, $routeParams, Laws) {
    return console.log('HomeCtrl');
  });

  angular.module(APP_NAME).controller('TocParentCtrl', function($route, $scope, $rootScope, $http, $routeParams, UrlBuilder) {
    var url;
    $scope.m = {};
    if (!$scope.tocData && !$routeParams.division) {
      url = UrlBuilder.api("/laws/" + $rootScope.currentLawCode + "/toc");
      $http.get(url).success(function(data) {
        $scope.tocData = data;
        if (!$rootScope.currentVersion) {
          $rootScope.currentVersion = data.versions[0];
        }
        return $scope.m.selectedVersion = $rootScope.currentVersion;
      });
    }
    switch ($rootScope.currentLawCode) {
      case 'ors':
        return $scope.tocChildTemplate = UrlBuilder.template('toc_ors.html');
    }
  });

  angular.module(APP_NAME).controller('ViewerCtrl', function($route, $scope, $rootScope, $http, $routeParams, $location, Laws, UrlBuilder) {
    var applyLaw, fetchAllLaws, fetchAndApplyLaw, fetchedLaws;
    console.log('ViewerCtrl');
    $scope.m = {};
    fetchedLaws = false;
    applyLaw = function(law) {
      $scope.lawText = law.text;
      $scope.lawTitle = law.title;
      $scope.lawVersions = law.versions.sort(function(a, b) {
        return parseInt(b) - parseInt(a);
      });
      $scope.prevSection = law.prev;
      return $scope.nextSection = law.next;
    };
    fetchAllLaws = function() {
      return Laws.fetchAll().then(function(laws) {
        return $scope.allLaws = laws;
      });
    };
    fetchAndApplyLaw = function(version, section) {
      return Laws.fetchLaw(version, section).then(function(response) {
        return applyLaw(response.data);
      });
    };
    $scope.chooseLaw = function(law) {
      $scope.currentLaw = law;
      $scope.hideSearchList = true;
      $scope.m.primaryYear = _.max(law.versions);
      return fetchAndApplyLaw(law.id, $scope.m.primaryYear);
    };
    $scope.lawFilterChange = function() {
      $scope.hideSearchList = false;
      if (!fetchedLaws) {
        fetchAllLaws();
        return fetchedLaws = true;
      }
    };
    $scope.diffMe = function() {
      var url;
      url = UrlBuilder.diffPage('ors', $scope.activeSection, $scope.availableVersions[$scope.availableVersions.length - 1], $scope.availableVersions[0]);
      return $location.path(url);
    };
    $scope.choosePrimaryYear = function(year) {
      return $scope.m.primaryYear = year;
    };
    $scope.selectedVersionChange = function(version) {
      return $location.path("/view/ors/" + version + "/" + $scope.activeSection);
    };
    if ($routeParams.section) {
      $rootScope.currentLawCode = $routeParams.lawCode;
      $rootScope.currentVersion = $scope.m.selectedVersion = $routeParams.version;
      $rootScope.currentSection = $routeParams.section;
      fetchAndApplyLaw($rootScope.currentVersion, $scope.currentSection);
    } else {
      $rootScope.currentVersion = $scope.m.selectedVersion = 2011;
      fetchAllLaws();
    }
    return $scope.$on('navClick', function(e, section) {
      var url;
      url = UrlBuilder.viewPage(section);
      return $location.path(url);
    });
  });

  angular.module(APP_NAME).config([
    '$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {
      var appPrefix, defaultCode, templatePrefix;
      defaultCode = 'ors';
      appPrefix = APP_PREFIX;
      templatePrefix = PARTIALS_PREFIX;
      $routeProvider.when(appPrefix + '/view/:lawCode/:version/:divison', {
        controller: 'DivisionViewerCtrl',
        templateUrl: templatePrefix + '/view_division.html'
      }).when(appPrefix + '/diff', {
        redirectTo: '/diff/ors'
      }).when(appPrefix + '/diff/:lawCode', {
        controller: 'DiffCtrl',
        templateUrl: templatePrefix + '/diff.html'
      }).when(appPrefix + '/diff/:lawCode/:subsection/:version1/:version2', {
        controller: 'DiffCtrl',
        templateUrl: templatePrefix + '/diff.html'
      }).when(appPrefix + '/toc/:lawCode', {
        controller: 'TocParentCtrl',
        templateUrl: templatePrefix + '/toc_base.html'
      }).when(appPrefix + '/toc/:lawCode/:version/:division', {
        controller: 'TocParentCtrl',
        templateUrl: templatePrefix + '/toc_base.html'
      }).otherwise({
        redirectTo: appPrefix + ("/toc/" + defaultCode)
      });
      return $locationProvider.html5Mode(true).hashPrefix('!');
    }
  ]);

  angular.module(APP_NAME).controller('DivisionViewerCtrl', function($route, $scope, $rootScope, $http, $routeParams, $location, UrlBuilder) {
    return $scope.m = {};
  });

  angular.module(APP_NAME).controller('OrsTocCtrl', function($route, $scope, $rootScope, $http, $routeParams, Laws, UrlBuilder) {
    var chapter, promise;
    $scope.chapterLinkBase = UrlBuilder.app("/toc/" + $rootScope.currentLawCode + "/" + $rootScope.currentVersion);
    if ($routeParams.division) {
      chapter = $routeParams.division;
      promise = Laws.fetchDivision($rootScope.currentLawCode, chapter);
      return promise.then(function(data) {
        $scope.currentChapter = data.chapter;
        return $scope.chapterStatutes = data.statutes;
      });
    }
  });

}).call(this);
