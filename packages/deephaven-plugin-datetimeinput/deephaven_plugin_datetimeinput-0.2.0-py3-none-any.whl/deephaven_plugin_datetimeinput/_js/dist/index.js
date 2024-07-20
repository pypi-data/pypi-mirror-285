"use strict";
const plugin = require("@deephaven/plugin");
const icons = require("@deephaven/icons");
const require$$1 = require("react");
const jsapiBootstrap = require("@deephaven/jsapi-bootstrap");
const Log = require("@deephaven/log");
const components = require("@deephaven/components");
var jsxRuntimeExports = {};
var jsxRuntime = {
  get exports() {
    return jsxRuntimeExports;
  },
  set exports(v) {
    jsxRuntimeExports = v;
  }
};
var reactJsxRuntime_production_min = {};
/*
object-assign
(c) Sindre Sorhus
@license MIT
*/
var getOwnPropertySymbols = Object.getOwnPropertySymbols;
var hasOwnProperty = Object.prototype.hasOwnProperty;
var propIsEnumerable = Object.prototype.propertyIsEnumerable;
function toObject(val) {
  if (val === null || val === void 0) {
    throw new TypeError("Object.assign cannot be called with null or undefined");
  }
  return Object(val);
}
function shouldUseNative() {
  try {
    if (!Object.assign) {
      return false;
    }
    var test1 = new String("abc");
    test1[5] = "de";
    if (Object.getOwnPropertyNames(test1)[0] === "5") {
      return false;
    }
    var test2 = {};
    for (var i = 0; i < 10; i++) {
      test2["_" + String.fromCharCode(i)] = i;
    }
    var order2 = Object.getOwnPropertyNames(test2).map(function(n2) {
      return test2[n2];
    });
    if (order2.join("") !== "0123456789") {
      return false;
    }
    var test3 = {};
    "abcdefghijklmnopqrst".split("").forEach(function(letter) {
      test3[letter] = letter;
    });
    if (Object.keys(Object.assign({}, test3)).join("") !== "abcdefghijklmnopqrst") {
      return false;
    }
    return true;
  } catch (err) {
    return false;
  }
}
shouldUseNative() ? Object.assign : function(target, source) {
  var from;
  var to = toObject(target);
  var symbols;
  for (var s = 1; s < arguments.length; s++) {
    from = Object(arguments[s]);
    for (var key in from) {
      if (hasOwnProperty.call(from, key)) {
        to[key] = from[key];
      }
    }
    if (getOwnPropertySymbols) {
      symbols = getOwnPropertySymbols(from);
      for (var i = 0; i < symbols.length; i++) {
        if (propIsEnumerable.call(from, symbols[i])) {
          to[symbols[i]] = from[symbols[i]];
        }
      }
    }
  }
  return to;
};
/** @license React v17.0.2
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var f = require$$1, g = 60103;
reactJsxRuntime_production_min.Fragment = 60107;
if ("function" === typeof Symbol && Symbol.for) {
  var h = Symbol.for;
  g = h("react.element");
  reactJsxRuntime_production_min.Fragment = h("react.fragment");
}
var m = f.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, n = Object.prototype.hasOwnProperty, p = { key: true, ref: true, __self: true, __source: true };
function q(c, a, k) {
  var b, d = {}, e = null, l = null;
  void 0 !== k && (e = "" + k);
  void 0 !== a.key && (e = "" + a.key);
  void 0 !== a.ref && (l = a.ref);
  for (b in a)
    n.call(a, b) && !p.hasOwnProperty(b) && (d[b] = a[b]);
  if (c && c.defaultProps)
    for (b in a = c.defaultProps, a)
      void 0 === d[b] && (d[b] = a[b]);
  return { $$typeof: g, type: c, key: e, ref: l, props: d, _owner: m.current };
}
reactJsxRuntime_production_min.jsx = q;
reactJsxRuntime_production_min.jsxs = q;
(function(module2) {
  {
    module2.exports = reactJsxRuntime_production_min;
  }
})(jsxRuntime);
const log = Log.module(
  "@deephaven/js-plugin-datetimeinput/DeephavenPluginDateTimeInput"
);
function DeephavenPluginDateTimeInput(props) {
  const { fetch } = props;
  const [date, setDate] = require$$1.useState("2024-05-01 12:00:00.000000000");
  const [widget, setWidget] = require$$1.useState(null);
  const dh = jsapiBootstrap.useApi();
  require$$1.useEffect(() => {
    async function init() {
      const newWidget = await fetch();
      setWidget(newWidget);
      const newDate = newWidget.getDataAsString();
      setDate(newDate);
      newWidget.addEventListener(
        dh.Widget.EVENT_MESSAGE,
        ({ detail }) => {
          const newDate2 = detail.getDataAsString();
          setDate(newDate2);
        }
      );
    }
    init();
  }, [dh, fetch]);
  const handleChange = require$$1.useCallback(
    (newDate) => {
      log.info("handleChange", newDate, widget);
      if (newDate == null) {
        return;
      }
      const { timeZone } = Intl.DateTimeFormat().resolvedOptions();
      const dateLiteral = `${newDate.replace(" ", "T")} ${timeZone}`;
      widget == null ? void 0 : widget.sendMessage(dateLiteral);
    },
    [widget]
  );
  return /* @__PURE__ */ jsxRuntimeExports.jsx(components.DateTimeInput, { onChange: handleChange, defaultValue: date });
}
const DeephavenPluginDateTimeInputPlugin = {
  // The name of the plugin
  name: "@deephaven/js-plugin-datetimeinput",
  // The type of plugin - this will generally be WIDGET_PLUGIN
  type: plugin.PluginType.WIDGET_PLUGIN,
  // The supported types for the plugin. This should match the value returned by `name`
  // in DeephavenPluginDateTimeInputType in deephaven_plugin_datetimeinput_type.py
  supportedTypes: "DeephavenPluginDateTimeInput",
  // The component to render for the plugin
  component: DeephavenPluginDateTimeInput,
  // The icon to display for the plugin
  icon: icons.vsGraph
};
module.exports = DeephavenPluginDateTimeInputPlugin;
