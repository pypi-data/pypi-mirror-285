(this.webpackJsonpui_v2=this.webpackJsonpui_v2||[]).push([[34],{1363:function(e,n,t){},1364:function(e,n,t){},652:function(e,n,t){"use strict";t.r(n);var a=t(0),i=t.n(a),o=t(95),s=t(219),l=t(11),r=t(17),c=t(25),u=Object(c.d)(c.c.RUNS),d=t(14),m=t(385),f=t(282),v=t(848),h=t(2),b=t(7),g=t(740),j=t(741),p=t(63),O=t(377),_=t(5),C=t(208),x=t(1);var y=function(e){var n=e.isInfiniteLoading,t=e.tableRef,a=e.columns,o=e.tableRowHeight,s=e.onExportTableData,r=e.getLastRunsData,u=e.isLatest,d=e.data,m=e.onColumnsVisibilityChange,f=e.onTableDiffShow,v=e.onManageColumns,h=e.sameValueColumns,b=e.onRowHeightChange,g=e.hiddenColumns,j=e.columnsOrder,p=e.columnsWidths,y=e.hideSystemMetrics,R=e.updateColumnsWidths,w=e.selectedRows,S=e.onRowSelect,N=e.archiveRuns,L=e.deleteRuns,D=e.requestStatus,I=e.onToggleColumnsColorScales,E=e.columnsColorScales,k=e.metricsValueKey,M=e.onMetricsValueKeyChange,V=i.a.useRef(null);return i.a.useEffect((function(){return function(){var e;null===(e=V.current)||void 0===e||e.abort()}}),[]),Object(x.jsx)(l.a,{children:Object(x.jsxs)("div",{className:"Runs__RunList__runListBox",children:[Object(x.jsx)("div",{className:"RunsTable",children:Object(x.jsx)(O.a,{custom:!0,allowInfiniteLoading:!0,isInfiniteLoading:n,showRowClickBehaviour:!1,infiniteLoadHandler:function(e){var t;u||n||(V.current=r(e),null===(t=V.current)||void 0===t||t.call().catch())},showResizeContainerActionBar:!1,ref:t,data:d,sameValueColumns:h,columns:a,selectedRows:w,appName:c.b.RUNS,multiSelect:!0,topHeader:!0,metricsValueKey:k,rowHeight:o,hiddenColumns:g,hideSystemMetrics:y,columnsOrder:j,columnsWidths:p,onMetricsValueKeyChange:M,onManageColumns:v,onColumnsVisibilityChange:m,onTableDiffShow:f,onRowHeightChange:b,updateColumnsWidths:R,onExport:s,onRowSelect:S,archiveRuns:N,deleteRuns:L,illustrationConfig:{type:C.e[D],page:"runs"},onToggleColumnsColorScales:I,columnsColorScales:E})}),n&&Object(x.jsx)("div",{className:"Infinite_Loader",children:Object(x.jsx)(_.l,{})})]})})},R=t(714),w=t(737),S=t(791),N=t(84),L=t(105),D=t(169);t(793);function I(e){return Object(x.jsx)(l.a,{children:Object(x.jsxs)(w.a,{title:L.a.RUNS_EXPLORER,disabled:e.disabled,children:[Object(x.jsx)(S.a,Object(h.a)({},e)),Object(x.jsx)("div",{className:"MetricsBar__menu",children:Object(x.jsx)(l.a,{children:Object(x.jsx)(N.a,{title:"Menu",anchor:function(e){var n=e.onAnchorClick;return Object(x.jsx)(_.c,{withOnlyIcon:!0,color:"secondary",size:"small",onClick:n,children:Object(x.jsx)(_.f,{fontSize:16,name:"menu",className:"MetricsBar__item__bookmark__Icon"})})},component:Object(x.jsx)("div",{className:"MetricsBar__popover",children:Object(x.jsx)("a",{href:D.b.EXPLORERS.RUNS.MAIN,target:"_blank",rel:"noreferrer",children:Object(x.jsx)(R.a,{children:"Explorer Documentation"})})})})})})]})})}var E=i.a.memo(I),k=t(705),M=t(749),V=t(60);t(1363);var B=function(e){var n=e.selectFormData,t=e.isRunsDataLoading,a=e.searchValue,o=e.onSearchInputChange,s=e.isDisabled,c=i.a.useRef(null),m=i.a.useRef(null);i.a.useEffect((function(){return function(){var e;null===(e=c.current)||void 0===e||e.abort()}}),[]);var f=i.a.useCallback((function(){var e;if(!t){var n=null===m||void 0===m||null===(e=m.current)||void 0===e?void 0:e.getValue();o(null!==n&&void 0!==n?n:""),c.current=u.getRunsData(!0,!0,!0,null!==n&&void 0!==n?n:""),c.current.call((function(e){Object(V.a)({detail:e,model:u})})).catch(),Object(d.b)(r.a.runs.searchClick)}}),[t,o]);return Object(x.jsx)(l.a,{children:Object(x.jsxs)("div",{className:"Runs_Search_Bar",children:[Object(x.jsx)("form",{onSubmit:f,children:Object(x.jsx)(M.a,{refObject:m,onEnter:f,error:n.error,context:n.suggestions,value:a,disabled:s})}),Object(x.jsx)(k.a,{style:{margin:"0 1em"},orientation:"vertical",flexItem:!0}),Object(x.jsx)(_.c,{className:"Runs_Search_Bar__Button",color:"primary",onClick:t?function(e){var n;e.preventDefault(),t&&(null===(n=c.current)||void 0===n||n.abort(),u.abortRequest())}:f,variant:t?"outlined":"contained",startIcon:Object(x.jsx)(_.f,{name:t?"close":"search",fontSize:t?12:14}),children:t?"Cancel":"Search"})]})})};t(1364);var T=function(e){var n,t=i.a.useState(!1),a=Object(b.a)(t,2),o=a[0],s=a[1];return Object(x.jsx)("div",{className:"Runs__container",children:Object(x.jsxs)("section",{className:"Runs__section",children:[Object(x.jsxs)("div",{className:"Runs__section__appBarContainer Runs__fullHeight",children:[Object(x.jsx)(E,Object(h.a)(Object(h.a)({},e.liveUpdateConfig),{},{onLiveUpdateConfigChange:e.onLiveUpdateConfigChange,disabled:o})),Object(x.jsx)(B,{selectFormData:e.selectFormData,onSearchInputChange:e.onSelectRunQueryChange,searchValue:e.query,isRunsDataLoading:e.requestStatus===p.a.Pending,isDisabled:o}),Object(x.jsxs)("div",{className:"Runs__table__container",children:[Object(x.jsx)(j.a,{progress:e.requestProgress,pendingStatus:e.requestStatus===p.a.Pending,setIsProgressBarVisible:s}),Object(x.jsx)(y,{columnsOrder:e.columnsOrder,hiddenColumns:e.hiddenColumns,onColumnsVisibilityChange:e.onColumnsVisibilityChange,onTableDiffShow:e.onTableDiffShow,onManageColumns:e.onManageColumns,onRowHeightChange:e.onRowHeightChange,onMetricsValueKeyChange:e.onMetricsValueKeyChange,data:e.tableData,sameValueColumns:e.sameValueColumns,isInfiniteLoading:e.isInfiniteLoading,isLatest:e.isLatest,hideSystemMetrics:e.hideSystemMetrics,onExportTableData:e.onExportTableData,tableRowHeight:e.tableRowHeight,metricsValueKey:e.metricsValueKey,columns:e.tableColumns,runsList:e.tableData,requestStatus:e.requestStatus,tableRef:e.tableRef,getLastRunsData:e.getLastRunsData,columnsWidths:e.columnsWidths,updateColumnsWidths:e.updateColumnsWidths,selectedRows:e.selectedRows,onRowSelect:e.onRowSelect,archiveRuns:e.archiveRuns,deleteRuns:e.deleteRuns,onToggleColumnsColorScales:e.onToggleColumnsColorScales,columnsColorScales:e.columnsColorScales})]})]}),(null===(n=e.notifyData)||void 0===n?void 0:n.length)>0&&Object(x.jsx)(g.a,{handleClose:e.onNotificationDelete,data:e.notifyData})]})})};function P(){var e,n,t,a,h,b,g,j,p,O,_,C,y,R,w,S=i.a.useRef(null),N=Object(s.a)(u),L=Object(o.h)();return i.a.useEffect((function(){var e;S.current&&Object(m.a)({refElement:{tableRef:S},model:u}),(null===N||void 0===N||null===(e=N.data)||void 0===e?void 0:e.length)>0&&Object(v.a)(u)}),[null===N||void 0===N?void 0:N.data]),i.a.useEffect((function(){u.initialize(),d.a(r.a.runs.pageView);var e=L.listen((function(){(null===N||void 0===N?void 0:N.config)&&N.config.select!==Object(f.a)("search")&&L.location.pathname==="/".concat(c.b.RUNS)&&u.setDefaultAppConfigData()}));return function(){e(),u.destroy()}}),[]),Object(x.jsx)(l.a,{children:Object(x.jsx)(T,{tableData:null===N||void 0===N?void 0:N.tableData,tableColumns:null===N||void 0===N?void 0:N.tableColumns,requestStatus:null===N||void 0===N?void 0:N.requestStatus,requestProgress:null===N||void 0===N?void 0:N.requestProgress,isLatest:null===N||void 0===N||null===(e=N.config)||void 0===e?void 0:e.pagination.isLatest,onSelectRunQueryChange:u.onSelectRunQueryChange,onToggleColumnsColorScales:u.onToggleColumnsColorScales,tableRowHeight:null===N||void 0===N||null===(n=N.config)||void 0===n||null===(t=n.table)||void 0===t?void 0:t.rowHeight,metricsValueKey:null===N||void 0===N||null===(a=N.config)||void 0===a||null===(h=a.table)||void 0===h?void 0:h.metricsValueKey,sameValueColumns:null===N||void 0===N?void 0:N.sameValueColumns,tableRef:S,columnsOrder:null===N||void 0===N||null===(b=N.config)||void 0===b?void 0:b.table.columnsOrder,hiddenColumns:null===N||void 0===N||null===(g=N.config)||void 0===g?void 0:g.table.hiddenColumns,hideSystemMetrics:null===N||void 0===N||null===(j=N.config)||void 0===j||null===(p=j.table)||void 0===p?void 0:p.hideSystemMetrics,selectedRows:null===N||void 0===N?void 0:N.selectedRows,query:null===N||void 0===N||null===(O=N.config)||void 0===O||null===(_=O.select)||void 0===_?void 0:_.query,selectFormData:null===N||void 0===N?void 0:N.selectFormData,columnsWidths:null===N||void 0===N||null===(C=N.config)||void 0===C?void 0:C.table.columnsWidths,onExportTableData:u.onExportTableData,updateColumnsWidths:u.updateColumnsWidths,getLastRunsData:u.getLastRunsData,isInfiniteLoading:null===N||void 0===N?void 0:N.infiniteIsPending,onNotificationDelete:u.onNotificationDelete,notifyData:null===N||void 0===N?void 0:N.notifyData,columnsColorScales:null===N||void 0===N||null===(y=N.config)||void 0===y||null===(R=y.table)||void 0===R?void 0:R.columnsColorScales,onRowHeightChange:u.onRowHeightChange,onManageColumns:u.onColumnsOrderChange,onColumnsVisibilityChange:u.onColumnsVisibilityChange,onTableDiffShow:u.onTableDiffShow,liveUpdateConfig:null===N||void 0===N||null===(w=N.config)||void 0===w?void 0:w.liveUpdate,onLiveUpdateConfigChange:u.changeLiveUpdateConfig,onRowSelect:u.onRowSelect,archiveRuns:u.archiveRuns,deleteRuns:u.deleteRuns,onMetricsValueKeyChange:u.onMetricsValueKeyChange})})}n.default=Object(a.memo)(P)},731:function(e,n,t){"use strict";t.d(n,"a",(function(){return c}));var a,i=t(0),o=["title","titleId"];function s(){return(s=Object.assign?Object.assign.bind():function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var a in t)Object.prototype.hasOwnProperty.call(t,a)&&(e[a]=t[a])}return e}).apply(this,arguments)}function l(e,n){if(null==e)return{};var t,a,i=function(e,n){if(null==e)return{};var t,a,i={},o=Object.keys(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||(i[t]=e[t]);return i}(e,n);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(i[t]=e[t])}return i}function r(e,n){var t=e.title,r=e.titleId,c=l(e,o);return i.createElement("svg",s({xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 44 44",ref:n,"aria-labelledby":r},c),t?i.createElement("title",{id:r},t):null,a||(a=i.createElement("path",{fill:"#30954c",d:"M22,3A19,19,0,1,0,41,22,19,19,0,0,0,22,3Zm8.53259,14.69269-9.8518,11.61108a1.50007,1.50007,0,0,1-2.2876,0l-4.9259-5.8056a1.5,1.5,0,1,1,2.28753-1.94086L19.537,26.01489l8.70813-10.26312a1.5,1.5,0,1,1,2.28747,1.94092Z"})))}var c=i.forwardRef(r);t.p},732:function(e,n,t){"use strict";t.d(n,"a",(function(){return c}));var a,i=t(0),o=["title","titleId"];function s(){return(s=Object.assign?Object.assign.bind():function(e){for(var n=1;n<arguments.length;n++){var t=arguments[n];for(var a in t)Object.prototype.hasOwnProperty.call(t,a)&&(e[a]=t[a])}return e}).apply(this,arguments)}function l(e,n){if(null==e)return{};var t,a,i=function(e,n){if(null==e)return{};var t,a,i={},o=Object.keys(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||(i[t]=e[t]);return i}(e,n);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(i[t]=e[t])}return i}function r(e,n){var t=e.title,r=e.titleId,c=l(e,o);return i.createElement("svg",s({xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 44 44",ref:n,"aria-labelledby":r},c),t?i.createElement("title",{id:r},t):null,a||(a=i.createElement("path",{fill:"#cc231a",d:"M22,3A19,19,0,1,0,41,22,19,19,0,0,0,22,3Zm7.91309,24.794.1455.15332a1.50037,1.50037,0,0,1,.38477.48535,1.46959,1.46959,0,0,1,.1543.59863A1.49927,1.49927,0,0,1,29.6416,30.499a1.39236,1.39236,0,0,1-.61133.09864,1.48626,1.48626,0,0,1-.59961-.1543,1.551,1.551,0,0,1-.50976-.41309L22,24.11328l-5.94531,5.93555a1.49689,1.49689,0,0,1-.48584.38476,1.47552,1.47552,0,0,1-.59912.15528,1.33873,1.33873,0,0,1-.61084-.09864,1.505,1.505,0,0,1-.51953-.33886,1.474,1.474,0,0,1-.3379-.51856,1.49377,1.49377,0,0,1,.05616-1.21,1.55724,1.55724,0,0,1,.41211-.50976L19.605,22.27832l.28369-.28223-5.94678-5.94238a1.49988,1.49988,0,0,1,.41651-2.55225,1.441,1.441,0,0,1,.61133-.10009,1.4941,1.4941,0,0,1,.59912.15625,1.55409,1.55409,0,0,1,.51074.41211L22,19.88623l5.94434-5.94434a1.5084,1.5084,0,0,1,1.08593-.54052,1.43985,1.43985,0,0,1,.61133.10009,1.50239,1.50239,0,0,1,.80176,2.06641,1.57937,1.57937,0,0,1-.41309.51074l-5.91894,5.917Z"})))}var c=i.forwardRef(r);t.p},737:function(e,n,t){"use strict";var a=t(4),i=(t(0),t(18)),o=t.n(i),s=t(5),l=t(11),r=(t(738),t(1));n.a=function(e){var n,t;return Object(r.jsx)(l.a,{children:Object(r.jsxs)("div",{className:o()("AppBar",Object(a.a)({},null!==(n=null===e||void 0===e?void 0:e.className)&&void 0!==n?n:"",e.className)),children:[Object(r.jsx)(s.n,{component:"h3",weight:600,size:14,tint:100,className:"AppBar__title",children:e.title}),e.children&&Object(r.jsx)("div",{className:o()("AppBar__content",Object(a.a)({"AppBar__content--disabled":e.disabled},null!==(t=null===e||void 0===e?void 0:e.className)&&void 0!==t?t:"",e.className)),children:e.children})]})})}},738:function(e,n,t){},740:function(e,n,t){"use strict";t.d(n,"a",(function(){return d}));t(0);var a=t(72),i=t(1594),o=t(1597),s=t(713),l=t(731),r=t(732),c=t(11),u=(t(751),t(1));function d(e){var n=e.data,t=void 0===n?[]:n,d=e.handleClose;return Object(u.jsx)(c.a,{children:a.a.isEmpty(t)?null:Object(u.jsx)("div",{children:Object(u.jsx)(o.a,{open:!0,autoHideDuration:3e3,anchorOrigin:{vertical:"top",horizontal:"right"},children:Object(u.jsx)("div",{className:"NotificationContainer",children:t.map((function(e){var n=e.id,t=e.severity,a=e.messages;return Object(u.jsx)(s.a,{mt:.5,children:Object(u.jsx)(i.a,{onClose:function(){return d(+n)},variant:"outlined",severity:t,iconMapping:{success:Object(u.jsx)(l.a,{}),error:Object(u.jsx)(r.a,{})},style:{height:"auto"},children:Object(u.jsxs)("div",{className:"NotificationContainer__contentBox",children:[Object(u.jsx)("p",{className:"NotificationContainer__contentBox__severity",children:t}),a.map((function(e,n){return e?Object(u.jsx)("p",{className:"NotificationContainer__contentBox__message",children:e},n):null}))]})})},n)}))})})})})}},741:function(e,n,t){"use strict";var a=t(7),i=t(0),o=t.n(i),s=t(18),l=t.n(s),r=t(5),c=(t(742),t(1));function u(e){var n=e.progress,t=void 0===n?{}:n,i=e.processing,s=void 0!==i&&i,u=e.pendingStatus,d=void 0!==u&&u,m=e.setIsProgressBarVisible,f=t.checked,v=void 0===f?0:f,h=t.trackedRuns,b=void 0===h?0:h,g=t.matched,j=void 0===g?0:g,p=t.percent,O=void 0===p?0:p,_=o.a.useState(!1),C=Object(a.a)(_,2),x=C[0],y=C[1],R=o.a.useRef(0);o.a.useEffect((function(){if(s||d)y(!0),null===m||void 0===m||m(!0);else{R.current&&window.clearTimeout(R.current),R.current=window.setTimeout((function(){y(!1)}),2e3)}return function(){R.current&&window.clearTimeout(R.current),null===m||void 0===m||m(!1)}}),[s,d,m]);var w=o.a.useMemo((function(){return d?O+"%":"unset"}),[d,O]),S=o.a.useMemo((function(){return!(s||d)}),[d,s]),N=o.a.useMemo((function(){return d?"Searching over runs...":"Processing..."}),[d]);return x?Object(c.jsx)("div",{className:l()("ProgressBar",{fadeOutProgress:S}),children:Object(c.jsxs)("div",{className:"ProgressBar__container",children:[Object(c.jsx)(r.n,{className:"ProgressBar__container__title",size:16,weight:500,component:"p",children:N}),Object(c.jsx)("div",{className:"ProgressBar__container__bar",children:Object(c.jsx)("span",{style:{width:w}})}),0!==b&&Object(c.jsxs)("div",{className:"ProgressBar__container__info",children:[Object(c.jsxs)(r.n,{size:14,weight:500,children:[v," of ",b," checked"]}),Object(c.jsxs)(r.n,{className:"ProgressBar__container__info__matched",size:14,weight:600,color:"success",children:[j," matched run(s)"]})]})]})}):null}n.a=o.a.memo(u)},742:function(e,n,t){},743:function(e,n,t){},749:function(e,n,t){"use strict";var a=t(2),i=t(7),o=t(0),s=t.n(o),l=t(18),r=t.n(l),c=t(72),u=t(372),d=t(5),m=t(170),f=t(169),v=t(9),h=t(98),b=t(374);function g(e,n){return null===e||void 0===e?void 0:e.languages.registerCompletionItemProvider("python",function(e,n){return{triggerCharacters:["."],provideCompletionItems:function(t,a){var i=t.getValueInRange({startLineNumber:a.lineNumber,startColumn:1,endLineNumber:a.lineNumber,endColumn:a.column}).replace("\t","").split(" "),o=c.a.last(i);if(j.forEach((function(e){o.includes(e)&&(o=c.a.last(o.split(e)))})),!Object.keys(n).some((function(e){return o.startsWith(e)})))return null;var s,l=Object(h.a)(n,n).map((function(e){var n=-1!==e.indexOf(".__example_type__")||"."===e[e.length-1]?e.indexOf(".__example_type__"):e.length;return e.slice(0,n)})),r="."===o.charAt(o.length-1),u=!1,d=[],m=Object(v.a)(l);try{for(m.s();!(s=m.n()).done;){var f=s.value;if(""===f.split(o)[0]||r&&""===f.split(o.slice(0,o.length-2))[0]){u=!0;break}}}catch(N){m.e(N)}finally{m.f()}var g=n,_=o;r&&u&&(g=Object(b.a)(n,_.substring(0,_.length-1)));var C=t.getWordUntilPosition(a),x={startLineNumber:a.lineNumber,endLineNumber:a.lineNumber,startColumn:C.startColumn,endColumn:C.endColumn};for(var y in g)if(g.hasOwnProperty(y)&&!y.startsWith("__")){var R=h.b.test(y)?y:'["'.concat(y,'"]'),w=p(Object(b.a)(n,_+R)),S={label:R,kind:O(e,w.hasExampleType?w.type:g[y],r),insertText:R,detail:w.type,range:x};S.kind!==e.languages.CompletionItemKind.Function&&S.kind!==e.languages.CompletionItemKind.Method||(S.insertText+="("),d.push(S)}return{suggestions:u?d:[]}}}}(e,n))}var j=["(","="];function p(e){var n=null===e||void 0===e?void 0:e.hasOwnProperty("__example_type__"),t="";if(n)switch(e.__example_type__.slice(7,e.__example_type__.length-1)){case"'str'":t="str";break;case"'int'":t="int";break;case"'bool'":t="bool";break;case"'list'":t="list";break;case"'float'":t="float";break;case"'bytes'":t="bytes";break;default:t="unknown"}else switch(typeof e){case"object":t="dict";break;case"string":t="str";break;case"boolean":t="bool";break;case"number":t="int"}return{type:t,hasExampleType:n}}function O(e,n){var t=arguments.length>2&&void 0!==arguments[2]&&arguments[2];switch((typeof n).toLowerCase()){case"object":return e.languages.CompletionItemKind.Class;case"function":return t?e.languages.CompletionItemKind.Method:e.languages.CompletionItemKind.Function;default:return t?e.languages.CompletionItemKind.Property:e.languages.CompletionItemKind.Variable}}t(743);var _=t(1);function C(e){var n=e.context,t=e.advanced,o=e.className,l=e.editorProps,v=void 0===l?{}:l,h=e.value,b=void 0===h?"":h,j=e.refObject,p=e.error,O=e.disabled,C=void 0!==O&&O,x=e.forceRemoveError,y=void 0!==x&&x,R=e.onEnter,w=e.onChange,S=s.a.useState(!1),N=Object(i.a)(S,2),L=N[0],D=N[1],I=s.a.useState(0),E=Object(i.a)(I,2),k=E[0],M=E[1],V=s.a.useState(!1),B=Object(i.a)(V,2),T=B[0],P=B[1],A=s.a.useState(!1),K=Object(i.a)(A,2),W=K[0],z=K[1],U=s.a.useState(b),H=Object(i.a)(U,2),q=H[0],F=H[1],Q=s.a.useState(""),Z=Object(i.a)(Q,2),J=Z[0],X=Z[1],G=Object(u.c)(),Y=s.a.useRef();s.a.useEffect((function(){se(),W&&(G.editor.defineTheme($.theme.name,$.theme.config),G.editor.setTheme($.theme.name));var e=c.a.debounce((function(){M(window.innerWidth)}),500);window.addEventListener("resize",e),ne();var t=g(G,n);return function(){null===t||void 0===t||t.dispose(),window.removeEventListener("resize",e)}}),[G,n,W]),s.a.useEffect((function(){setTimeout((function(){se(),te()}),100)}),[k]),s.a.useEffect((function(){te(),y&&!p&&(X(""),ae())}),[p,G,y]),s.a.useEffect((function(){var e;T&&(null===(e=Y.current)||void 0===e||e.focus())}),[T,W]),s.a.useEffect((function(){b!==q&&F(b)}),[b]),s.a.useEffect((function(){setTimeout((function(){se()}),100)}),[k]);var $=s.a.useMemo((function(){return Object(m.a)(t)}),[t]),ee=s.a.useCallback((function(){P(!0)}),[]),ne=s.a.useCallback((function(){P(!1)}),[]);function te(){var e;G&&p&&(X(null===p||void 0===p?void 0:p.message),G.editor.setModelMarkers(G.editor.getModels()[0],"marker",[{startLineNumber:null===p||void 0===p?void 0:p.detail.line,startColumn:null===p||void 0===p?void 0:p.detail.offset,endLineNumber:null===p||void 0===p?void 0:p.detail.line,endColumn:(null===p||void 0===p||null===(e=p.detail)||void 0===e?void 0:e.end_offset)||(null===p||void 0===p?void 0:p.detail.offset),message:null===p||void 0===p?void 0:p.message,severity:G.MarkerSeverity.Error}]))}function ae(){(null===G||void 0===G?void 0:G.editor)&&G.editor.setModelMarkers(G.editor.getModels()[0],"marker",[])}function ie(e){if(e.selection){var n=e.selection,t=n.startColumn,a=n.endColumn;D(t!==a)}}var oe=s.a.useCallback((function(e,n){if(C)Y.current.setValue(q);else if(ae(),X(""),"string"===typeof e){var t=e.replace(/[\n\r]/g,"");if(n.changes[0].text.startsWith("[")&&"."===t[n.changes[0].rangeOffset-1]&&(t=t.slice(0,n.changes[0].rangeOffset-1)+t.slice(n.changes[0].rangeOffset,t.length)),w&&w(t,n),"\n"===n.changes[0].text)return t=L?q.replace(/[\n\r]/g,""):t,Y.current.setValue(t),R&&R(),void F(t);F(t)}}),[L,w,R,C]);function se(){W&&(G.editor.defineTheme($.theme.name,$.theme.config),G.editor.setTheme($.theme.name))}return Object(_.jsxs)("section",{className:r()("AutocompleteInput ".concat(o||""),{AutocompleteInput__disabled:C}),children:[Object(_.jsxs)("div",{onClick:ee,className:r()("AutocompleteInput__container",{AutocompleteInput__container__focused:T,AutocompleteInput__container__advanced:t,AutocompleteInput__container__error:J}),children:[Object(_.jsx)(u.a,Object(a.a)({language:"python",height:$.height,value:q,onChange:oe,onMount:function(e){z(!0),Y.current=e,j&&(j.current=Y.current),Y.current.onDidFocusEditorWidget(ee),Y.current.onDidBlurEditorWidget(ne),Y.current.onDidChangeCursorSelection(ie)},loading:Object(_.jsx)("span",{}),options:$.options},v),"".concat(k)),W&&(T||q?null:Object(_.jsxs)("div",{className:"AutocompleteInput__container__placeholder",children:["Filter runs, e.g. run.learning_rate ",">"," 0.0001 and run.batch_size == 32"]}))]}),J&&Object(_.jsxs)("div",{className:"AutocompleteInput__errorBar",children:[Object(_.jsx)("div",{children:Object(_.jsxs)(d.n,{color:"error",className:"AutocompleteInput__errorBar__message",component:"p",size:16,children:[Object(_.jsx)(d.n,{size:16,color:"error",weight:700,children:"Error:"}),J]})}),Object(_.jsxs)("div",{className:"AutocompleteInput__errorBar__hint",children:[Object(_.jsx)(d.f,{name:"info-circle-outline",box:!0}),Object(_.jsxs)(d.n,{children:["Aim Query Language is pythonic and fairly easy to get used to. If you are having issues, please refer to the"," ",Object(_.jsx)("a",{href:f.b.AIM_QL,target:"_blank",rel:"noreferrer",children:"docs"})," ","for detailed usage guide and more examples."]})]})]})]})}C.displayName="AutocompleteInput";var x=s.a.memo(C);n.a=x},751:function(e,n,t){},791:function(e,n,t){"use strict";var a=t(0),i=t.n(a),o=t(5),s=t(11),l=(t(792),t(1));function r(e){return Object(l.jsx)(s.a,{children:Object(l.jsxs)("div",{className:"LiveUpdateSettings",children:[Object(l.jsx)(o.n,{className:"LiveUpdateSettings__Text",size:14,children:"Live Update:"}),Object(l.jsx)(o.m,{checked:Boolean(e.enabled),onChange:function(){e.onLiveUpdateConfigChange({enabled:!e.enabled})},size:"small",color:"primary"})]})})}n.a=i.a.memo(r)},792:function(e,n,t){},793:function(e,n,t){},848:function(e,n,t){"use strict";t.d(n,"a",(function(){return s}));var a=t(2),i=t(6),o=t(390);function s(e){var n=e.getState(),t=Object(o.a)(null===n||void 0===n?void 0:n.tableColumns),s=Object(i.a)(n.config.table.hiddenColumns);0===s.length&&t.length>0&&n.config.table.hideSystemMetrics&&(s=t,e.updateModelData(Object(a.a)(Object(a.a)({},n.config),{},{table:Object(a.a)(Object(a.a)({},n.config.table),{},{hiddenColumns:s})})))}}}]);
//# sourceMappingURL=runs.js.map?version=0d8816ff6904d31bcd75