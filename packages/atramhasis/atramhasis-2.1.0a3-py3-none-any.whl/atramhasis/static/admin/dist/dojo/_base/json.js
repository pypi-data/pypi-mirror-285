//>>built
define("dojo/_base/json",["./kernel","../json"],function(a,d){a.fromJson=function(c){return eval("("+c+")")};a._escapeString=d.stringify;a.toJsonIndentStr="\t";a.toJson=function(c,f){return d.stringify(c,function(g,b){if(b){var e=b.__json__||b.json;if("function"==typeof e)return e.call(b)}return b},f&&a.toJsonIndentStr)};return a});
//# sourceMappingURL=json.js.map