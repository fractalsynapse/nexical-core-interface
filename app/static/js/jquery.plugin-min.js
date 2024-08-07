/*! Simple JavaScript Inheritance
 * By John Resig http://ejohn.org/
 * MIT Licensed.
 */
!(function () {
  'use strict';
  var a = !1;
  (window.JQClass = function () {}),
    (JQClass.classes = {}),
    (JQClass.extend = function b(c) {
      function d() {
        !a && this._init && this._init.apply(this, arguments);
      }
      var e = this.prototype;
      a = !0;
      var f = new this();
      a = !1;
      for (var g in c)
        if ('function' == typeof c[g] && 'function' == typeof e[g])
          f[g] = (function (a, b) {
            return function () {
              var c = this._super;
              this._super = function (b) {
                return e[a].apply(this, b || []);
              };
              var d = b.apply(this, arguments);
              return (this._super = c), d;
            };
          })(g, c[g]);
        else if (
          'object' == typeof c[g] &&
          'object' == typeof e[g] &&
          'defaultOptions' === g
        ) {
          var h,
            i = e[g],
            j = c[g],
            k = {};
          for (h in i) k[h] = i[h];
          for (h in j) k[h] = j[h];
          f[g] = k;
        } else f[g] = c[g];
      return (
        (d.prototype = f), (d.prototype.constructor = d), (d.extend = b), d
      );
    });
})() /*! Abstract base class for collection plugins v1.0.2.
	Written by Keith Wood (wood.keith{at}optusnet.com.au) December 2013.
	Licensed under the MIT license (http://keith-wood.name/licence.html). */,
  (function ($) {
    'use strict';
    function camelCase(a) {
      return a.replace(/-([a-z])/g, function (a, b) {
        return b.toUpperCase();
      });
    }
    (JQClass.classes.JQPlugin = JQClass.extend({
      name: 'plugin',
      defaultOptions: {},
      regionalOptions: {},
      deepMerge: !0,
      _getMarker: function () {
        return 'is-' + this.name;
      },
      _init: function () {
        $.extend(
          this.defaultOptions,
          (this.regionalOptions && this.regionalOptions['']) || {},
        );
        var a = camelCase(this.name);
        ($[a] = this),
          ($.fn[a] = function (b) {
            var c = Array.prototype.slice.call(arguments, 1),
              d = this,
              e = this;
            return (
              this.each(function () {
                if ('string' == typeof b) {
                  if ('_' === b[0] || !$[a][b]) throw 'Unknown method: ' + b;
                  var f = $[a][b].apply($[a], [this].concat(c));
                  if (f !== d && void 0 !== f) return (e = f), !1;
                } else $[a]._attach(this, b);
              }),
              e
            );
          });
      },
      setDefaults: function (a) {
        $.extend(this.defaultOptions, a || {});
      },
      _attach: function (a, b) {
        if (((a = $(a)), !a.hasClass(this._getMarker()))) {
          a.addClass(this._getMarker()),
            (b = $.extend(
              this.deepMerge,
              {},
              this.defaultOptions,
              this._getMetadata(a),
              b || {},
            ));
          var c = $.extend(
            { name: this.name, elem: a, options: b },
            this._instSettings(a, b),
          );
          a.data(this.name, c), this._postAttach(a, c), this.option(a, b);
        }
      },
      _instSettings: function (a, b) {
        return {};
      },
      _postAttach: function (a, b) {},
      _getMetadata: function (elem) {
        try {
          var data = elem.data(this.name.toLowerCase()) || '';
          (data = data
            .replace(/(\\?)'/g, function (a, b) {
              return b ? "'" : '"';
            })
            .replace(/([a-zA-Z0-9]+):/g, function (a, b, c) {
              var d = data.substring(0, c).match(/"/g);
              return d && d.length % 2 !== 0 ? b + ':' : '"' + b + '":';
            })
            .replace(/\\:/g, ':')),
            (data = $.parseJSON('{' + data + '}'));
          for (var key in data)
            if (data.hasOwnProperty(key)) {
              var value = data[key];
              'string' == typeof value &&
                value.match(/^new Date\(([-0-9,\s]*)\)$/) &&
                (data[key] = eval(value));
            }
          return data;
        } catch (a) {
          return {};
        }
      },
      _getInst: function (a) {
        return $(a).data(this.name) || {};
      },
      option: function (a, b, c) {
        a = $(a);
        var d = a.data(this.name),
          e = b || {};
        return !b || ('string' == typeof b && 'undefined' == typeof c)
          ? ((e = (d || {}).options), e && b ? e[b] : e)
          : void (
              a.hasClass(this._getMarker()) &&
              ('string' == typeof b && ((e = {}), (e[b] = c)),
              this._optionsChanged(a, d, e),
              $.extend(d.options, e))
            );
      },
      _optionsChanged: function (a, b, c) {},
      destroy: function (a) {
        (a = $(a)),
          a.hasClass(this._getMarker()) &&
            (this._preDestroy(a, this._getInst(a)),
            a.removeData(this.name).removeClass(this._getMarker()));
      },
      _preDestroy: function (a, b) {},
    })),
      ($.JQPlugin = {
        createPlugin: function (a, b) {
          'object' == typeof a && ((b = a), (a = 'JQPlugin')),
            (a = camelCase(a));
          var c = camelCase(b.name);
          (JQClass.classes[c] = JQClass.classes[a].extend(b)),
            new JQClass.classes[c]();
        },
      });
  })(jQuery);
