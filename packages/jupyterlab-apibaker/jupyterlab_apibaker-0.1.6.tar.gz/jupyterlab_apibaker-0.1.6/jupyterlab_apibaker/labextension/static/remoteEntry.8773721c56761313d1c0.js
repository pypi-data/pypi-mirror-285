var _JUPYTERLAB;
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "webpack/container/entry/jupyterlab-apibaker":
/*!***********************!*\
  !*** container entry ***!
  \***********************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

var moduleMap = {
	"./index": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_emotion_memoize_dist_emotion-memoize_esm_js-node_modules_mui_material_Gr-1fa383"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_CssBaseline_CssBaselin-44bd1b"), __webpack_require__.e("vendors-node_modules_react-icons_fi_index_mjs-node_modules_react-icons_io5_index_mjs-node_mod-c9828a"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_8f22"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf"), __webpack_require__.e("lib_index_js")]).then(() => (() => ((__webpack_require__(/*! ./lib/index.js */ "./lib/index.js")))));
	},
	"./extension": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_emotion_memoize_dist_emotion-memoize_esm_js-node_modules_mui_material_Gr-1fa383"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_CssBaseline_CssBaselin-44bd1b"), __webpack_require__.e("vendors-node_modules_react-icons_fi_index_mjs-node_modules_react-icons_io5_index_mjs-node_mod-c9828a"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_8f22"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf"), __webpack_require__.e("lib_index_js")]).then(() => (() => ((__webpack_require__(/*! ./lib/index.js */ "./lib/index.js")))));
	},
	"./style": () => {
		return __webpack_require__.e("style_index_js").then(() => (() => ((__webpack_require__(/*! ./style/index.js */ "./style/index.js")))));
	}
};
var get = (module, getScope) => {
	__webpack_require__.R = getScope;
	getScope = (
		__webpack_require__.o(moduleMap, module)
			? moduleMap[module]()
			: Promise.resolve().then(() => {
				throw new Error('Module "' + module + '" does not exist in container.');
			})
	);
	__webpack_require__.R = undefined;
	return getScope;
};
var init = (shareScope, initScope) => {
	if (!__webpack_require__.S) return;
	var name = "default"
	var oldScope = __webpack_require__.S[name];
	if(oldScope && oldScope !== shareScope) throw new Error("Container initialization failed as it has already been initialized with a different share scope");
	__webpack_require__.S[name] = shareScope;
	return __webpack_require__.I(name, initScope);
};

// This exports getters to disallow modifications
__webpack_require__.d(exports, {
	get: () => (get),
	init: () => (init)
});

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			loaded: false,
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = __webpack_module_cache__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/ensure chunk */
/******/ 	(() => {
/******/ 		__webpack_require__.f = {};
/******/ 		// This file contains only the entry chunk.
/******/ 		// The chunk loading function for additional chunks
/******/ 		__webpack_require__.e = (chunkId) => {
/******/ 			return Promise.all(Object.keys(__webpack_require__.f).reduce((promises, key) => {
/******/ 				__webpack_require__.f[key](chunkId, promises);
/******/ 				return promises;
/******/ 			}, []));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/get javascript chunk filename */
/******/ 	(() => {
/******/ 		// This function allow to reference async chunks
/******/ 		__webpack_require__.u = (chunkId) => {
/******/ 			// return url for filenames based on template
/******/ 			return "" + chunkId + "." + {"vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js":"c1445e272277323f6004","vendors-node_modules_emotion_memoize_dist_emotion-memoize_esm_js-node_modules_mui_material_Gr-1fa383":"0d0870e2808cfd719462","vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_CssBaseline_CssBaselin-44bd1b":"eed05036156eebf11d9c","vendors-node_modules_react-icons_fi_index_mjs-node_modules_react-icons_io5_index_mjs-node_mod-c9828a":"d5011b4e3b5fc512051f","webpack_sharing_consume_default_react":"1d55025c44aefdcbe67b","webpack_sharing_consume_default_emotion_react_emotion_react-_8f22":"92b1b28023e270324aad","webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf":"537bca32b5cfd0666e0c","lib_index_js":"487dd87c45cd3b3d57a2","style_index_js":"e5f34050e1c4587d76c9","vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-cbc221":"d03c9a37a9305ebb280a","vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js":"f25a9453da041e1ef923","node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_memoize_dist_emotion-m-27ec560":"3b7604fb59931d82692e","vendors-node_modules_emotion_styled_dist_emotion-styled_browser_esm_js":"d3a75f95bb93c24e7e33","webpack_sharing_consume_default_emotion_react_emotion_react-_1cec":"74e6146b505a81100778","node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_memoize_dist_emotion-m-27ec561":"d5d89d9030ce79194df2","vendors-node_modules_mui_material_Alert_Alert_js-node_modules_mui_material_AlertTitle_AlertTi-81ffdc":"06d8e6587d929afb5df0","vendors-node_modules_mui_lab_index_js":"9eadb988b475494e7944","vendors-node_modules_mui_material_index_js":"5885a81e696beede8629","vendors-node_modules_lodash_isempty_index_js":"d77d9257b572110e045d","node_modules_lodash_isundefined_index_js":"3f5f1360dcf2f17862be"}[chunkId] + ".js";
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/load script */
/******/ 	(() => {
/******/ 		var inProgress = {};
/******/ 		var dataWebpackPrefix = "jupyterlab-apibaker:";
/******/ 		// loadScript function to load a script via script tag
/******/ 		__webpack_require__.l = (url, done, key, chunkId) => {
/******/ 			if(inProgress[url]) { inProgress[url].push(done); return; }
/******/ 			var script, needAttach;
/******/ 			if(key !== undefined) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				for(var i = 0; i < scripts.length; i++) {
/******/ 					var s = scripts[i];
/******/ 					if(s.getAttribute("src") == url || s.getAttribute("data-webpack") == dataWebpackPrefix + key) { script = s; break; }
/******/ 				}
/******/ 			}
/******/ 			if(!script) {
/******/ 				needAttach = true;
/******/ 				script = document.createElement('script');
/******/ 		
/******/ 				script.charset = 'utf-8';
/******/ 				script.timeout = 120;
/******/ 				if (__webpack_require__.nc) {
/******/ 					script.setAttribute("nonce", __webpack_require__.nc);
/******/ 				}
/******/ 				script.setAttribute("data-webpack", dataWebpackPrefix + key);
/******/ 		
/******/ 				script.src = url;
/******/ 			}
/******/ 			inProgress[url] = [done];
/******/ 			var onScriptComplete = (prev, event) => {
/******/ 				// avoid mem leaks in IE.
/******/ 				script.onerror = script.onload = null;
/******/ 				clearTimeout(timeout);
/******/ 				var doneFns = inProgress[url];
/******/ 				delete inProgress[url];
/******/ 				script.parentNode && script.parentNode.removeChild(script);
/******/ 				doneFns && doneFns.forEach((fn) => (fn(event)));
/******/ 				if(prev) return prev(event);
/******/ 			}
/******/ 			var timeout = setTimeout(onScriptComplete.bind(null, undefined, { type: 'timeout', target: script }), 120000);
/******/ 			script.onerror = onScriptComplete.bind(null, script.onerror);
/******/ 			script.onload = onScriptComplete.bind(null, script.onload);
/******/ 			needAttach && document.head.appendChild(script);
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/node module decorator */
/******/ 	(() => {
/******/ 		__webpack_require__.nmd = (module) => {
/******/ 			module.paths = [];
/******/ 			if (!module.children) module.children = [];
/******/ 			return module;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/sharing */
/******/ 	(() => {
/******/ 		__webpack_require__.S = {};
/******/ 		var initPromises = {};
/******/ 		var initTokens = {};
/******/ 		__webpack_require__.I = (name, initScope) => {
/******/ 			if(!initScope) initScope = [];
/******/ 			// handling circular init calls
/******/ 			var initToken = initTokens[name];
/******/ 			if(!initToken) initToken = initTokens[name] = {};
/******/ 			if(initScope.indexOf(initToken) >= 0) return;
/******/ 			initScope.push(initToken);
/******/ 			// only runs once
/******/ 			if(initPromises[name]) return initPromises[name];
/******/ 			// creates a new share scope if needed
/******/ 			if(!__webpack_require__.o(__webpack_require__.S, name)) __webpack_require__.S[name] = {};
/******/ 			// runs all init snippets from all modules reachable
/******/ 			var scope = __webpack_require__.S[name];
/******/ 			var warn = (msg) => {
/******/ 				if (typeof console !== "undefined" && console.warn) console.warn(msg);
/******/ 			};
/******/ 			var uniqueName = "jupyterlab-apibaker";
/******/ 			var register = (name, version, factory, eager) => {
/******/ 				var versions = scope[name] = scope[name] || {};
/******/ 				var activeVersion = versions[version];
/******/ 				if(!activeVersion || (!activeVersion.loaded && (!eager != !activeVersion.eager ? eager : uniqueName > activeVersion.from))) versions[version] = { get: factory, from: uniqueName, eager: !!eager };
/******/ 			};
/******/ 			var initExternal = (id) => {
/******/ 				var handleError = (err) => (warn("Initialization of sharing external failed: " + err));
/******/ 				try {
/******/ 					var module = __webpack_require__(id);
/******/ 					if(!module) return;
/******/ 					var initFn = (module) => (module && module.init && module.init(__webpack_require__.S[name], initScope))
/******/ 					if(module.then) return promises.push(module.then(initFn, handleError));
/******/ 					var initResult = initFn(module);
/******/ 					if(initResult && initResult.then) return promises.push(initResult['catch'](handleError));
/******/ 				} catch(err) { handleError(err); }
/******/ 			}
/******/ 			var promises = [];
/******/ 			switch(name) {
/******/ 				case "default": {
/******/ 					register("@emotion/react", "11.11.4", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-cbc221"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_memoize_dist_emotion-m-27ec560")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/react/dist/emotion-react.browser.esm.js */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))));
/******/ 					register("@emotion/styled", "11.11.5", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-cbc221"), __webpack_require__.e("vendors-node_modules_emotion_styled_dist_emotion-styled_browser_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_8f22"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_1cec"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_memoize_dist_emotion-m-27ec561")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/styled/dist/emotion-styled.browser.esm.js */ "./node_modules/@emotion/styled/dist/emotion-styled.browser.esm.js"))))));
/******/ 					register("@mui/lab", "5.0.0-alpha.172", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_mui_material_Alert_Alert_js-node_modules_mui_material_AlertTitle_AlertTi-81ffdc"), __webpack_require__.e("vendors-node_modules_emotion_memoize_dist_emotion-memoize_esm_js-node_modules_mui_material_Gr-1fa383"), __webpack_require__.e("vendors-node_modules_mui_lab_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_8f22"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@mui/lab/index.js */ "./node_modules/@mui/lab/index.js"))))));
/******/ 					register("@mui/material", "5.16.4", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_mui_material_Alert_Alert_js-node_modules_mui_material_AlertTitle_AlertTi-81ffdc"), __webpack_require__.e("vendors-node_modules_emotion_memoize_dist_emotion-memoize_esm_js-node_modules_mui_material_Gr-1fa383"), __webpack_require__.e("vendors-node_modules_mui_material_index_js"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_CssBaseline_CssBaselin-44bd1b"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_8f22"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@mui/material/index.js */ "./node_modules/@mui/material/index.js"))))));
/******/ 					register("jupyterlab-apibaker", "0.1.6", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_emotion_memoize_dist_emotion-memoize_esm_js-node_modules_mui_material_Gr-1fa383"), __webpack_require__.e("vendors-node_modules_mui_material_Box_Box_js-node_modules_mui_material_CssBaseline_CssBaselin-44bd1b"), __webpack_require__.e("vendors-node_modules_react-icons_fi_index_mjs-node_modules_react-icons_io5_index_mjs-node_mod-c9828a"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_8f22"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf"), __webpack_require__.e("lib_index_js")]).then(() => (() => (__webpack_require__(/*! ./lib/index.js */ "./lib/index.js"))))));
/******/ 					register("lodash.isempty", "4.4.0", () => (__webpack_require__.e("vendors-node_modules_lodash_isempty_index_js").then(() => (() => (__webpack_require__(/*! ./node_modules/lodash.isempty/index.js */ "./node_modules/lodash.isempty/index.js"))))));
/******/ 					register("lodash.isundefined", "3.0.1", () => (__webpack_require__.e("node_modules_lodash_isundefined_index_js").then(() => (() => (__webpack_require__(/*! ./node_modules/lodash.isundefined/index.js */ "./node_modules/lodash.isundefined/index.js"))))));
/******/ 				}
/******/ 				break;
/******/ 			}
/******/ 			if(!promises.length) return initPromises[name] = 1;
/******/ 			return initPromises[name] = Promise.all(promises).then(() => (initPromises[name] = 1));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript)
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) {
/******/ 					var i = scripts.length - 1;
/******/ 					while (i > -1 && (!scriptUrl || !/^http(s?):/.test(scriptUrl))) scriptUrl = scripts[i--].src;
/******/ 				}
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/consumes */
/******/ 	(() => {
/******/ 		var parseVersion = (str) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			var p=p=>{return p.split(".").map((p=>{return+p==p?+p:p}))},n=/^([^-+]+)?(?:-([^+]+))?(?:\+(.+))?$/.exec(str),r=n[1]?p(n[1]):[];return n[2]&&(r.length++,r.push.apply(r,p(n[2]))),n[3]&&(r.push([]),r.push.apply(r,p(n[3]))),r;
/******/ 		}
/******/ 		var versionLt = (a, b) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			a=parseVersion(a),b=parseVersion(b);for(var r=0;;){if(r>=a.length)return r<b.length&&"u"!=(typeof b[r])[0];var e=a[r],n=(typeof e)[0];if(r>=b.length)return"u"==n;var t=b[r],f=(typeof t)[0];if(n!=f)return"o"==n&&"n"==f||("s"==f||"u"==n);if("o"!=n&&"u"!=n&&e!=t)return e<t;r++}
/******/ 		}
/******/ 		var rangeToString = (range) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			var r=range[0],n="";if(1===range.length)return"*";if(r+.5){n+=0==r?">=":-1==r?"<":1==r?"^":2==r?"~":r>0?"=":"!=";for(var e=1,a=1;a<range.length;a++){e--,n+="u"==(typeof(t=range[a]))[0]?"-":(e>0?".":"")+(e=2,t)}return n}var g=[];for(a=1;a<range.length;a++){var t=range[a];g.push(0===t?"not("+o()+")":1===t?"("+o()+" || "+o()+")":2===t?g.pop()+" "+g.pop():rangeToString(t))}return o();function o(){return g.pop().replace(/^\((.+)\)$/,"$1")}
/******/ 		}
/******/ 		var satisfy = (range, version) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			if(0 in range){version=parseVersion(version);var e=range[0],r=e<0;r&&(e=-e-1);for(var n=0,i=1,a=!0;;i++,n++){var f,s,g=i<range.length?(typeof range[i])[0]:"";if(n>=version.length||"o"==(s=(typeof(f=version[n]))[0]))return!a||("u"==g?i>e&&!r:""==g!=r);if("u"==s){if(!a||"u"!=g)return!1}else if(a)if(g==s)if(i<=e){if(f!=range[i])return!1}else{if(r?f>range[i]:f<range[i])return!1;f!=range[i]&&(a=!1)}else if("s"!=g&&"n"!=g){if(r||i<=e)return!1;a=!1,i--}else{if(i<=e||s<g!=r)return!1;a=!1}else"s"!=g&&"n"!=g&&(a=!1,i--)}}var t=[],o=t.pop.bind(t);for(n=1;n<range.length;n++){var u=range[n];t.push(1==u?o()|o():2==u?o()&o():u?satisfy(u,version):!o())}return!!o();
/******/ 		}
/******/ 		var ensureExistence = (scopeName, key) => {
/******/ 			var scope = __webpack_require__.S[scopeName];
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) throw new Error("Shared module " + key + " doesn't exist in shared scope " + scopeName);
/******/ 			return scope;
/******/ 		};
/******/ 		var findVersion = (scope, key) => {
/******/ 			var versions = scope[key];
/******/ 			var key = Object.keys(versions).reduce((a, b) => {
/******/ 				return !a || versionLt(a, b) ? b : a;
/******/ 			}, 0);
/******/ 			return key && versions[key]
/******/ 		};
/******/ 		var findSingletonVersionKey = (scope, key) => {
/******/ 			var versions = scope[key];
/******/ 			return Object.keys(versions).reduce((a, b) => {
/******/ 				return !a || (!versions[a].loaded && versionLt(a, b)) ? b : a;
/******/ 			}, 0);
/******/ 		};
/******/ 		var getInvalidSingletonVersionMessage = (scope, key, version, requiredVersion) => {
/******/ 			return "Unsatisfied version " + version + " from " + (version && scope[key][version].from) + " of shared singleton module " + key + " (required " + rangeToString(requiredVersion) + ")"
/******/ 		};
/******/ 		var getSingleton = (scope, scopeName, key, requiredVersion) => {
/******/ 			var version = findSingletonVersionKey(scope, key);
/******/ 			return get(scope[key][version]);
/******/ 		};
/******/ 		var getSingletonVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			var version = findSingletonVersionKey(scope, key);
/******/ 			if (!satisfy(requiredVersion, version)) warn(getInvalidSingletonVersionMessage(scope, key, version, requiredVersion));
/******/ 			return get(scope[key][version]);
/******/ 		};
/******/ 		var getStrictSingletonVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			var version = findSingletonVersionKey(scope, key);
/******/ 			if (!satisfy(requiredVersion, version)) throw new Error(getInvalidSingletonVersionMessage(scope, key, version, requiredVersion));
/******/ 			return get(scope[key][version]);
/******/ 		};
/******/ 		var findValidVersion = (scope, key, requiredVersion) => {
/******/ 			var versions = scope[key];
/******/ 			var key = Object.keys(versions).reduce((a, b) => {
/******/ 				if (!satisfy(requiredVersion, b)) return a;
/******/ 				return !a || versionLt(a, b) ? b : a;
/******/ 			}, 0);
/******/ 			return key && versions[key]
/******/ 		};
/******/ 		var getInvalidVersionMessage = (scope, scopeName, key, requiredVersion) => {
/******/ 			var versions = scope[key];
/******/ 			return "No satisfying version (" + rangeToString(requiredVersion) + ") of shared module " + key + " found in shared scope " + scopeName + ".\n" +
/******/ 				"Available versions: " + Object.keys(versions).map((key) => {
/******/ 				return key + " from " + versions[key].from;
/******/ 			}).join(", ");
/******/ 		};
/******/ 		var getValidVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			var entry = findValidVersion(scope, key, requiredVersion);
/******/ 			if(entry) return get(entry);
/******/ 			throw new Error(getInvalidVersionMessage(scope, scopeName, key, requiredVersion));
/******/ 		};
/******/ 		var warn = (msg) => {
/******/ 			if (typeof console !== "undefined" && console.warn) console.warn(msg);
/******/ 		};
/******/ 		var warnInvalidVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			warn(getInvalidVersionMessage(scope, scopeName, key, requiredVersion));
/******/ 		};
/******/ 		var get = (entry) => {
/******/ 			entry.loaded = 1;
/******/ 			return entry.get()
/******/ 		};
/******/ 		var init = (fn) => (function(scopeName, a, b, c) {
/******/ 			var promise = __webpack_require__.I(scopeName);
/******/ 			if (promise && promise.then) return promise.then(fn.bind(fn, scopeName, __webpack_require__.S[scopeName], a, b, c));
/******/ 			return fn(scopeName, __webpack_require__.S[scopeName], a, b, c);
/******/ 		});
/******/ 		
/******/ 		var load = /*#__PURE__*/ init((scopeName, scope, key) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return get(findVersion(scope, key));
/******/ 		});
/******/ 		var loadFallback = /*#__PURE__*/ init((scopeName, scope, key, fallback) => {
/******/ 			return scope && __webpack_require__.o(scope, key) ? get(findVersion(scope, key)) : fallback();
/******/ 		});
/******/ 		var loadVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return get(findValidVersion(scope, key, version) || warnInvalidVersion(scope, scopeName, key, version) || findVersion(scope, key));
/******/ 		});
/******/ 		var loadSingleton = /*#__PURE__*/ init((scopeName, scope, key) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getSingleton(scope, scopeName, key);
/******/ 		});
/******/ 		var loadSingletonVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadStrictVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getValidVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadStrictSingletonVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getStrictSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return get(findValidVersion(scope, key, version) || warnInvalidVersion(scope, scopeName, key, version) || findVersion(scope, key));
/******/ 		});
/******/ 		var loadSingletonFallback = /*#__PURE__*/ init((scopeName, scope, key, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return getSingleton(scope, scopeName, key);
/******/ 		});
/******/ 		var loadSingletonVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return getSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadStrictVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			var entry = scope && __webpack_require__.o(scope, key) && findValidVersion(scope, key, version);
/******/ 			return entry ? get(entry) : fallback();
/******/ 		});
/******/ 		var loadStrictSingletonVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return getStrictSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var installedModules = {};
/******/ 		var moduleToHandlerMapping = {
/******/ 			"webpack/sharing/consume/default/react": () => (loadSingletonVersionCheck("default", "react", [1,17,0,1])),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?8f22": () => (loadFallback("default", "@emotion/react", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-cbc221"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?9405": () => (loadStrictVersionCheckFallback("default", "@emotion/react", [1,11,4,1], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-cbc221"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/styled/@emotion/styled": () => (loadStrictVersionCheckFallback("default", "@emotion/styled", [1,11,3,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-cbc221"), __webpack_require__.e("vendors-node_modules_emotion_styled_dist_emotion-styled_browser_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-_1cec")]).then(() => (() => (__webpack_require__(/*! @emotion/styled */ "./node_modules/@emotion/styled/dist/emotion-styled.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/react-dom": () => (loadSingletonVersionCheck("default", "react-dom", [1,17,0,1])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/settingregistry": () => (loadSingletonVersionCheck("default", "@jupyterlab/settingregistry", [1,3,6,7])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/launcher": () => (loadSingletonVersionCheck("default", "@jupyterlab/launcher", [1,3,6,7])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/mainmenu": () => (loadSingletonVersionCheck("default", "@jupyterlab/mainmenu", [1,3,6,7])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/coreutils": () => (loadSingletonVersionCheck("default", "@jupyterlab/coreutils", [1,5,6,7])),
/******/ 			"webpack/sharing/consume/default/@lumino/disposable": () => (loadSingletonVersionCheck("default", "@lumino/disposable", [1,1,10,0])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/apputils": () => (loadSingletonVersionCheck("default", "@jupyterlab/apputils", [1,3,6,7])),
/******/ 			"webpack/sharing/consume/default/@lumino/widgets": () => (loadSingletonVersionCheck("default", "@lumino/widgets", [1,1,37,2])),
/******/ 			"webpack/sharing/consume/default/@mui/material/@mui/material": () => (loadStrictVersionCheckFallback("default", "@mui/material", [1,5,16,4], () => (Promise.all([__webpack_require__.e("vendors-node_modules_mui_material_Alert_Alert_js-node_modules_mui_material_AlertTitle_AlertTi-81ffdc"), __webpack_require__.e("vendors-node_modules_mui_material_index_js")]).then(() => (() => (__webpack_require__(/*! @mui/material */ "./node_modules/@mui/material/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mui/lab/@mui/lab": () => (loadStrictVersionCheckFallback("default", "@mui/lab", [1,5,0,0,,"alpha",172], () => (Promise.all([__webpack_require__.e("vendors-node_modules_mui_material_Alert_Alert_js-node_modules_mui_material_AlertTitle_AlertTi-81ffdc"), __webpack_require__.e("vendors-node_modules_mui_lab_index_js")]).then(() => (() => (__webpack_require__(/*! @mui/lab */ "./node_modules/@mui/lab/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/services": () => (loadSingletonVersionCheck("default", "@jupyterlab/services", [1,6,6,7])),
/******/ 			"webpack/sharing/consume/default/lodash.isempty/lodash.isempty": () => (loadStrictVersionCheckFallback("default", "lodash.isempty", [1,4,4,0], () => (__webpack_require__.e("vendors-node_modules_lodash_isempty_index_js").then(() => (() => (__webpack_require__(/*! lodash.isempty */ "./node_modules/lodash.isempty/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/lodash.isundefined/lodash.isundefined": () => (loadStrictVersionCheckFallback("default", "lodash.isundefined", [1,3,0,1], () => (__webpack_require__.e("node_modules_lodash_isundefined_index_js").then(() => (() => (__webpack_require__(/*! lodash.isundefined */ "./node_modules/lodash.isundefined/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?1cec": () => (loadStrictVersionCheckFallback("default", "@emotion/react", [1,11,0,0,,"rc",0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js-node_modules_react-is_index_js"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js")))))))
/******/ 		};
/******/ 		// no consumes in initial chunks
/******/ 		var chunkMapping = {
/******/ 			"webpack_sharing_consume_default_react": [
/******/ 				"webpack/sharing/consume/default/react"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react-_8f22": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?8f22"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-5f41bf": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?9405",
/******/ 				"webpack/sharing/consume/default/@emotion/styled/@emotion/styled",
/******/ 				"webpack/sharing/consume/default/react-dom"
/******/ 			],
/******/ 			"lib_index_js": [
/******/ 				"webpack/sharing/consume/default/@jupyterlab/settingregistry",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/launcher",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/mainmenu",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/coreutils",
/******/ 				"webpack/sharing/consume/default/@lumino/disposable",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/apputils",
/******/ 				"webpack/sharing/consume/default/@lumino/widgets",
/******/ 				"webpack/sharing/consume/default/@mui/material/@mui/material",
/******/ 				"webpack/sharing/consume/default/@mui/lab/@mui/lab",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/services",
/******/ 				"webpack/sharing/consume/default/lodash.isempty/lodash.isempty",
/******/ 				"webpack/sharing/consume/default/lodash.isundefined/lodash.isundefined"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react-_1cec": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?1cec"
/******/ 			]
/******/ 		};
/******/ 		var startedInstallModules = {};
/******/ 		__webpack_require__.f.consumes = (chunkId, promises) => {
/******/ 			if(__webpack_require__.o(chunkMapping, chunkId)) {
/******/ 				chunkMapping[chunkId].forEach((id) => {
/******/ 					if(__webpack_require__.o(installedModules, id)) return promises.push(installedModules[id]);
/******/ 					if(!startedInstallModules[id]) {
/******/ 					var onFactory = (factory) => {
/******/ 						installedModules[id] = 0;
/******/ 						__webpack_require__.m[id] = (module) => {
/******/ 							delete __webpack_require__.c[id];
/******/ 							module.exports = factory();
/******/ 						}
/******/ 					};
/******/ 					startedInstallModules[id] = true;
/******/ 					var onError = (error) => {
/******/ 						delete installedModules[id];
/******/ 						__webpack_require__.m[id] = (module) => {
/******/ 							delete __webpack_require__.c[id];
/******/ 							throw error;
/******/ 						}
/******/ 					};
/******/ 					try {
/******/ 						var promise = moduleToHandlerMapping[id]();
/******/ 						if(promise.then) {
/******/ 							promises.push(installedModules[id] = promise.then(onFactory)['catch'](onError));
/******/ 						} else onFactory(promise);
/******/ 					} catch(e) { onError(e); }
/******/ 					}
/******/ 				});
/******/ 			}
/******/ 		}
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"jupyterlab-apibaker": 0
/******/ 		};
/******/ 		
/******/ 		__webpack_require__.f.j = (chunkId, promises) => {
/******/ 				// JSONP chunk loading for javascript
/******/ 				var installedChunkData = __webpack_require__.o(installedChunks, chunkId) ? installedChunks[chunkId] : undefined;
/******/ 				if(installedChunkData !== 0) { // 0 means "already installed".
/******/ 		
/******/ 					// a Promise means "currently loading".
/******/ 					if(installedChunkData) {
/******/ 						promises.push(installedChunkData[2]);
/******/ 					} else {
/******/ 						if(!/^webpack_sharing_consume_default_(emotion_react_emotion_react\-(_1cec|_8f22|webpack_sharing_consume_default_e\-5f41bf)|react)$/.test(chunkId)) {
/******/ 							// setup Promise in chunk cache
/******/ 							var promise = new Promise((resolve, reject) => (installedChunkData = installedChunks[chunkId] = [resolve, reject]));
/******/ 							promises.push(installedChunkData[2] = promise);
/******/ 		
/******/ 							// start chunk loading
/******/ 							var url = __webpack_require__.p + __webpack_require__.u(chunkId);
/******/ 							// create error before stack unwound to get useful stacktrace later
/******/ 							var error = new Error();
/******/ 							var loadingEnded = (event) => {
/******/ 								if(__webpack_require__.o(installedChunks, chunkId)) {
/******/ 									installedChunkData = installedChunks[chunkId];
/******/ 									if(installedChunkData !== 0) installedChunks[chunkId] = undefined;
/******/ 									if(installedChunkData) {
/******/ 										var errorType = event && (event.type === 'load' ? 'missing' : event.type);
/******/ 										var realSrc = event && event.target && event.target.src;
/******/ 										error.message = 'Loading chunk ' + chunkId + ' failed.\n(' + errorType + ': ' + realSrc + ')';
/******/ 										error.name = 'ChunkLoadError';
/******/ 										error.type = errorType;
/******/ 										error.request = realSrc;
/******/ 										installedChunkData[1](error);
/******/ 									}
/******/ 								}
/******/ 							};
/******/ 							__webpack_require__.l(url, loadingEnded, "chunk-" + chunkId, chunkId);
/******/ 						} else installedChunks[chunkId] = 0;
/******/ 					}
/******/ 				}
/******/ 		};
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		// no on chunks loaded
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 		
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkjupyterlab_apibaker"] = self["webpackChunkjupyterlab_apibaker"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/nonce */
/******/ 	(() => {
/******/ 		__webpack_require__.nc = undefined;
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// module cache are used so entry inlining is disabled
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	var __webpack_exports__ = __webpack_require__("webpack/container/entry/jupyterlab-apibaker");
/******/ 	(_JUPYTERLAB = typeof _JUPYTERLAB === "undefined" ? {} : _JUPYTERLAB)["jupyterlab-apibaker"] = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=remoteEntry.8773721c56761313d1c0.js.map