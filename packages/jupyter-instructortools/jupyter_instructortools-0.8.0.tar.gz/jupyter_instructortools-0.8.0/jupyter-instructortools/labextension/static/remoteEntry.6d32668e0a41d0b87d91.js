var _JUPYTERLAB;(()=>{"use strict";var e,r,t,o,n,a,i,u,l,s,f,d,p,c,h,v,g,m={340:(e,r,t)=>{var o={"./index":()=>t.e(509).then((()=>()=>t(509))),"./extension":()=>t.e(509).then((()=>()=>t(509))),"./style":()=>t.e(728).then((()=>()=>t(728)))},n=(e,r)=>(t.R=r,r=t.o(o,e)?o[e]():Promise.resolve().then((()=>{throw new Error('Module "'+e+'" does not exist in container.')})),t.R=void 0,r),a=(e,r)=>{if(t.S){var o="default",n=t.S[o];if(n&&n!==e)throw new Error("Container initialization failed as it has already been initialized with a different share scope");return t.S[o]=e,t.I(o,r)}};t.d(r,{get:()=>n,init:()=>a})}},y={};function b(e){var r=y[e];if(void 0!==r)return r.exports;var t=y[e]={id:e,exports:{}};return m[e](t,t.exports,b),t.exports}b.m=m,b.c=y,b.n=e=>{var r=e&&e.__esModule?()=>e.default:()=>e;return b.d(r,{a:r}),r},b.d=(e,r)=>{for(var t in r)b.o(r,t)&&!b.o(e,t)&&Object.defineProperty(e,t,{enumerable:!0,get:r[t]})},b.f={},b.e=e=>Promise.all(Object.keys(b.f).reduce(((r,t)=>(b.f[t](e,r),r)),[])),b.u=e=>e+"."+{509:"2c605a792a8760908c87",728:"05a0208492ab713ca9d1"}[e]+".js?v="+{509:"2c605a792a8760908c87",728:"05a0208492ab713ca9d1"}[e],b.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(e){if("object"==typeof window)return window}}(),b.o=(e,r)=>Object.prototype.hasOwnProperty.call(e,r),e={},r="jupyter-instructortools:",b.l=(t,o,n,a)=>{if(e[t])e[t].push(o);else{var i,u;if(void 0!==n)for(var l=document.getElementsByTagName("script"),s=0;s<l.length;s++){var f=l[s];if(f.getAttribute("src")==t||f.getAttribute("data-webpack")==r+n){i=f;break}}i||(u=!0,(i=document.createElement("script")).charset="utf-8",i.timeout=120,b.nc&&i.setAttribute("nonce",b.nc),i.setAttribute("data-webpack",r+n),i.src=t),e[t]=[o];var d=(r,o)=>{i.onerror=i.onload=null,clearTimeout(p);var n=e[t];if(delete e[t],i.parentNode&&i.parentNode.removeChild(i),n&&n.forEach((e=>e(o))),r)return r(o)},p=setTimeout(d.bind(null,void 0,{type:"timeout",target:i}),12e4);i.onerror=d.bind(null,i.onerror),i.onload=d.bind(null,i.onload),u&&document.head.appendChild(i)}},b.r=e=>{"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},(()=>{b.S={};var e={},r={};b.I=(t,o)=>{o||(o=[]);var n=r[t];if(n||(n=r[t]={}),!(o.indexOf(n)>=0)){if(o.push(n),e[t])return e[t];b.o(b.S,t)||(b.S[t]={});var a=b.S[t],i="jupyter-instructortools",u=[];return"default"===t&&((e,r,t,o)=>{var n=a[e]=a[e]||{},u=n[r];(!u||!u.loaded&&(1!=!u.eager?o:i>u.from))&&(n[r]={get:()=>b.e(509).then((()=>()=>b(509))),from:i,eager:!1})})("jupyter-instructortools","0.8.0"),e[t]=u.length?Promise.all(u).then((()=>e[t]=1)):1}}})(),(()=>{var e;b.g.importScripts&&(e=b.g.location+"");var r=b.g.document;if(!e&&r&&(r.currentScript&&(e=r.currentScript.src),!e)){var t=r.getElementsByTagName("script");if(t.length)for(var o=t.length-1;o>-1&&(!e||!/^http(s?):/.test(e));)e=t[o--].src}if(!e)throw new Error("Automatic publicPath is not supported in this browser");e=e.replace(/#.*$/,"").replace(/\?.*$/,"").replace(/\/[^\/]+$/,"/"),b.p=e})(),t=e=>{var r=e=>e.split(".").map((e=>+e==e?+e:e)),t=/^([^-+]+)?(?:-([^+]+))?(?:\+(.+))?$/.exec(e),o=t[1]?r(t[1]):[];return t[2]&&(o.length++,o.push.apply(o,r(t[2]))),t[3]&&(o.push([]),o.push.apply(o,r(t[3]))),o},o=(e,r)=>{e=t(e),r=t(r);for(var o=0;;){if(o>=e.length)return o<r.length&&"u"!=(typeof r[o])[0];var n=e[o],a=(typeof n)[0];if(o>=r.length)return"u"==a;var i=r[o],u=(typeof i)[0];if(a!=u)return"o"==a&&"n"==u||"s"==u||"u"==a;if("o"!=a&&"u"!=a&&n!=i)return n<i;o++}},n=e=>{var r=e[0],t="";if(1===e.length)return"*";if(r+.5){t+=0==r?">=":-1==r?"<":1==r?"^":2==r?"~":r>0?"=":"!=";for(var o=1,a=1;a<e.length;a++)o--,t+="u"==(typeof(u=e[a]))[0]?"-":(o>0?".":"")+(o=2,u);return t}var i=[];for(a=1;a<e.length;a++){var u=e[a];i.push(0===u?"not("+l()+")":1===u?"("+l()+" || "+l()+")":2===u?i.pop()+" "+i.pop():n(u))}return l();function l(){return i.pop().replace(/^\((.+)\)$/,"$1")}},a=(e,r)=>{if(0 in e){r=t(r);var o=e[0],n=o<0;n&&(o=-o-1);for(var i=0,u=1,l=!0;;u++,i++){var s,f,d=u<e.length?(typeof e[u])[0]:"";if(i>=r.length||"o"==(f=(typeof(s=r[i]))[0]))return!l||("u"==d?u>o&&!n:""==d!=n);if("u"==f){if(!l||"u"!=d)return!1}else if(l)if(d==f)if(u<=o){if(s!=e[u])return!1}else{if(n?s>e[u]:s<e[u])return!1;s!=e[u]&&(l=!1)}else if("s"!=d&&"n"!=d){if(n||u<=o)return!1;l=!1,u--}else{if(u<=o||f<d!=n)return!1;l=!1}else"s"!=d&&"n"!=d&&(l=!1,u--)}}var p=[],c=p.pop.bind(p);for(i=1;i<e.length;i++){var h=e[i];p.push(1==h?c()|c():2==h?c()&c():h?a(h,r):!c())}return!!c()},i=(e,r)=>{var t=b.S[e];if(!t||!b.o(t,r))throw new Error("Shared module "+r+" doesn't exist in shared scope "+e);return t},u=(e,r)=>{var t=e[r];return Object.keys(t).reduce(((e,r)=>!e||!t[e].loaded&&o(e,r)?r:e),0)},l=(e,r,t,o)=>"Unsatisfied version "+t+" from "+(t&&e[r][t].from)+" of shared singleton module "+r+" (required "+n(o)+")",s=(e,r,t,o)=>{var n=u(e,t);return a(o,n)||f(l(e,t,n,o)),d(e[t][n])},f=e=>{"undefined"!=typeof console&&console.warn&&console.warn(e)},d=e=>(e.loaded=1,e.get()),p=(e=>function(r,t,o,n){var a=b.I(r);return a&&a.then?a.then(e.bind(e,r,b.S[r],t,o,n)):e(r,b.S[r],t,o)})(((e,r,t,o)=>(i(e,t),s(r,0,t,o)))),c={},h={110:()=>p("default","@jupyterlab/apputils",[1,4,3,3]),179:()=>p("default","@jupyterlab/mainmenu",[1,4,2,3]),858:()=>p("default","@jupyterlab/ui-components",[1,4,2,3]),902:()=>p("default","@jupyterlab/notebook",[1,4,2,3])},v={509:[110,179,858,902]},g={},b.f.consumes=(e,r)=>{b.o(v,e)&&v[e].forEach((e=>{if(b.o(c,e))return r.push(c[e]);if(!g[e]){var t=r=>{c[e]=0,b.m[e]=t=>{delete b.c[e],t.exports=r()}};g[e]=!0;var o=r=>{delete c[e],b.m[e]=t=>{throw delete b.c[e],r}};try{var n=h[e]();n.then?r.push(c[e]=n.then(t).catch(o)):t(n)}catch(e){o(e)}}}))},(()=>{var e={811:0};b.f.j=(r,t)=>{var o=b.o(e,r)?e[r]:void 0;if(0!==o)if(o)t.push(o[2]);else{var n=new Promise(((t,n)=>o=e[r]=[t,n]));t.push(o[2]=n);var a=b.p+b.u(r),i=new Error;b.l(a,(t=>{if(b.o(e,r)&&(0!==(o=e[r])&&(e[r]=void 0),o)){var n=t&&("load"===t.type?"missing":t.type),a=t&&t.target&&t.target.src;i.message="Loading chunk "+r+" failed.\n("+n+": "+a+")",i.name="ChunkLoadError",i.type=n,i.request=a,o[1](i)}}),"chunk-"+r,r)}};var r=(r,t)=>{var o,n,[a,i,u]=t,l=0;if(a.some((r=>0!==e[r]))){for(o in i)b.o(i,o)&&(b.m[o]=i[o]);u&&u(b)}for(r&&r(t);l<a.length;l++)n=a[l],b.o(e,n)&&e[n]&&e[n][0](),e[n]=0},t=self.webpackChunkjupyter_instructortools=self.webpackChunkjupyter_instructortools||[];t.forEach(r.bind(null,0)),t.push=r.bind(null,t.push.bind(t))})(),b.nc=void 0;var w=b(340);(_JUPYTERLAB=void 0===_JUPYTERLAB?{}:_JUPYTERLAB)["jupyter-instructortools"]=w})();