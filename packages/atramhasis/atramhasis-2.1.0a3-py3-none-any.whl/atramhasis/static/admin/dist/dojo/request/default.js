//>>built
define("dojo/request/default",["exports","require","../has"],function(b,c,d){var a=d("config-requestProvider");a||(a="./xhr");b.getPlatformDefaultId=function(){return"./xhr"};b.load=function(e,h,f,k){c(["platform"==e?"./xhr":a],function(g){f(g)})}});
//# sourceMappingURL=default.js.map