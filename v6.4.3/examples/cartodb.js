(window.webpackJsonp=window.webpackJsonp||[]).push([[11],{421:function(t,e,i){"use strict";i.r(e);var o=i(3),a=i(5),n=i(2),s=i(46),r=i(27),p=i(11),c=function(t){function e(e){t.call(this,{attributions:e.attributions,cacheSize:e.cacheSize,crossOrigin:e.crossOrigin,maxZoom:void 0!==e.maxZoom?e.maxZoom:18,minZoom:e.minZoom,projection:e.projection,wrapX:e.wrapX}),this.account_=e.account,this.mapId_=e.map||"",this.config_=e.config||{},this.templateCache_={},this.initializeMap_()}return t&&(e.__proto__=t),e.prototype=Object.create(t&&t.prototype),e.prototype.constructor=e,e.prototype.getConfig=function(){return this.config_},e.prototype.updateConfig=function(t){Object(p.a)(this.config_,t),this.initializeMap_()},e.prototype.setConfig=function(t){this.config_=t||{},this.initializeMap_()},e.prototype.initializeMap_=function(){var t=JSON.stringify(this.config_);if(this.templateCache_[t])this.applyTemplate_(this.templateCache_[t]);else{var e="https://"+this.account_+".carto.com/api/v1/map";this.mapId_&&(e+="/named/"+this.mapId_);var i=new XMLHttpRequest;i.addEventListener("load",this.handleInitResponse_.bind(this,t)),i.addEventListener("error",this.handleInitError_.bind(this)),i.open("POST",e),i.setRequestHeader("Content-type","application/json"),i.send(JSON.stringify(this.config_))}},e.prototype.handleInitResponse_=function(t,e){var i=e.target;if(!i.status||i.status>=200&&i.status<300){var o;try{o=JSON.parse(i.responseText)}catch(t){return void this.setState(s.a.ERROR)}this.applyTemplate_(o),this.templateCache_[t]=o,this.setState(s.a.READY)}else this.setState(s.a.ERROR)},e.prototype.handleInitError_=function(t){this.setState(s.a.ERROR)},e.prototype.applyTemplate_=function(t){var e="https://"+t.cdn_url.https+"/"+this.account_+"/api/v1/map/"+t.layergroupid+"/{z}/{x}/{y}.png";this.setUrl(e)},e}(r.a),h=i(9),u={layers:[{type:"cartodb",options:{cartocss_version:"2.1.1",cartocss:"#layer { polygon-fill: #F00; }",sql:"select * from european_countries_e where area > 0"}}]},l=new c({account:"documentation",config:u});new o.a({layers:[new a.a({source:new h.b}),new a.a({source:l})],target:"map",view:new n.a({center:[0,0],zoom:2})});document.getElementById("country-area").addEventListener("change",(function(){var t;t=this.value,u.layers[0].options.sql="select * from european_countries_e where area > "+t,l.setConfig(u)}))}},[[421,0]]]);
//# sourceMappingURL=cartodb.js.map