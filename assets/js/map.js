/* Configuration */
var geoserver_url = 'http://192.168.56.101:8082/geoserver';
var area_group_url = geoserver_url+'/Lab_GIS/ows?service=WFS&' +
'version=2.0.0&request=GetFeature&typeName=Lab_GIS:area_group_10&' +
'outputFormat=text/javascript&srsname=EPSG:3857&'
/* preprocessed GHS-POP and WorldPop for intercomparison */
var ghs_intercomp_final_info = new ol.source.ImageWMS({
    url: geoserver_url+'/Lab_GIS/wms',
    params: {'LAYERS': 'Lab_GIS:ghs_intercomp_final'}
});
var worldpop_intercomp_final_info = new ol.source.ImageWMS({
    url: geoserver_url+'/Lab_GIS/wms',
    params: {'LAYERS': 'Lab_GIS:worldpop_intercomp_final'}
});
/* map of differences (GHS-POP - WorldPop) */
var intercomp_diff_info = new ol.source.ImageWMS({
    url: geoserver_url+'/Lab_GIS/wms',
    params: {'LAYERS': 'Lab_GIS:intercomp_diff'}
});

/* Basemaps */
var osm = new ol.layer.Tile({
    title: 'OpenStreetMap',
    type: 'base',
    visible: true,
    source: new ol.source.OSM()
});
var stamenWatercolor = new ol.layer.Tile({
    title: 'Stamen Watercolor',
    type: 'base',
    visible: false,
    source: new ol.source.Stamen({
        layer: 'watercolor'
    })
});
var stamenToner = new ol.layer.Tile({
    title: 'Stamen Toner',
    type: 'base',
    visible: false,
    source: new ol.source.Stamen({
        layer: 'toner'
    })
});

/* Layers */
// area group
var vectorSource = new ol.source.Vector({
	loader: function(extent, resolution, projection){
		var url = area_group_url +
			'&format_options=callback:loadFeatures';
		$.ajax({
			url: url,
			dataType: 'jsonp'
		});
	}
});
var geojsonFormat = new ol.format.GeoJSON();

function loadFeatures(response) {
	vectorSource.addFeatures(geojsonFormat.readFeatures(response));
}

var area_group = new ol.layer.Vector({
	title: 'Area of Group 10',
    source: vectorSource,
    style: new ol.style.Style({
		stroke: new ol.style.Stroke({
			color: 'white',
			width: 1
        }),
        fill: new ol.style.Fill({
            color: 'green'
        })
	}),
	opacity: 0.7
});

// preprocessed GHS-POP and WorldPop for intercomparison
var ghs_intercomp_final = new ol.layer.Image({
    title: "Preprocessed GHS-POP",
    source: ghs_intercomp_final_info,
    opacity: 0.7
});
var world_intercomp_final = new ol.layer.Image({
    title: "Preprocessed WorldPop",
    source: worldpop_intercomp_final_info,
    opacity: 0.7
});
// map of differences (GHS-POP - WorldPop)
var intercomp_diff = new ol.layer.Image({
    title: "Map of differences",
    source: intercomp_diff_info,
    opacity: 0.7
});

/* Create the map */
/*************** map in homepage  *******************/
var map = new ol.Map({
    target: document.getElementById('map'),
    layers: [
        new ol.layer.Group({
            title: 'Base Maps',
            layers: [
                stamenWatercolor,
                stamenToner,
                osm
            ]
        }),
        new ol.layer.Group({
            title: 'Overlay Layers',
            layers: [
                area_group
            ]
        })
    ],
    view: new ol.View({
        center:[0, 0],
        zoom: 2
    }),
    controls: ol.control.defaults().extend([
        new ol.control.ScaleLine(),
        new ol.control.FullScreen(),
        new ol.control.OverviewMap({
            layers:[
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                })
            ]
        }),
        new ol.control.MousePosition({
            coordinateFormat: ol.coordinate.createStringXY(4),
            projection: 'EPSG:4326'
        })
    ])
});

var layerSwitcher = new ol.control.LayerSwitcher({});
map.addControl(layerSwitcher);

/* Popup */
var elementPopup = document.getElementById('popup');

var popup = new ol.Overlay({
	element: elementPopup
});
map.addOverlay(popup);

map.on('click', function(event){
	var feature = map.forEachFeatureAtPixel(event.pixel, function(feature, layer){
		return feature;
    });
    //console.log(feature)

	if(feature != null) {
		var pixel = event.pixel;
		var coord = map.getCoordinateFromPixel(pixel);
		popup.setPosition(coord);
		$(elementPopup).attr('title', 'Group 10 Tiles');
		$(elementPopup).attr('data-content', '<b>TileID: </b>'+feature.get('tileID') +
            '</br><b>Location:</b>(' + feature.get('x_1') + ', ' + feature.get('y_1') +
            '), (' + feature.get('x_2') + ', ' + feature.get('y_2') +')');
		$(elementPopup).popover({'placement': 'top', 'html': true});
		$(elementPopup).popover('show');
	}
});

map.on('pointermove', function(event){
	if(event.dragging) {
		$(elementPopup).popover('dispose');
		return;
	}
	var pixel = map.getEventPixel(event.originalEvent);
	var hit = map.hasFeatureAtPixel(pixel);
	map.getTarget().style.cursor = hit ? 'pointer' : '';
})

/*************** map in intercomparision  *******************/
var map_intc = new ol.Map({
    target: document.getElementById('map1'),
    layers: [
        new ol.layer.Group({
            title: 'Base Maps',
            layers: [
                stamenWatercolor,
                stamenToner,
                osm
            ]
        }),
        new ol.layer.Group({
            title: 'Overlay Layers',
            layers: [
                area_group,
                ghs_intercomp_final,
                world_intercomp_final,
                intercomp_diff
            ]
        })
    ],
    view: new ol.View({
        center:[26, 64],
        zoom: 2
    }),
    controls: ol.control.defaults().extend([
        new ol.control.ScaleLine(),
        new ol.control.FullScreen(),
        new ol.control.OverviewMap({
            layers:[
                new ol.layer.Tile({
                    source: new ol.source.OSM()
                })
            ]
        }),
        new ol.control.MousePosition({
            coordinateFormat: ol.coordinate.createStringXY(4),
            projection: 'EPSG:4326'
        })
    ])
});

var layerSwitcher1 = new ol.control.LayerSwitcher({});
map_intc.addControl(layerSwitcher1);

/* Popup */
var elementPopup1 = document.getElementById('popup1');

var popup1 = new ol.Overlay({
	element: elementPopup1
});
map_intc.addOverlay(popup1);

map_intc.on('click', function(event){
	var feature = map_intc.forEachFeatureAtPixel(event.pixel, function(feature, layer){
		return feature;
    });
    //console.log(feature)

	if(feature != null) {
		var pixel = event.pixel;
		var coord = map_intc.getCoordinateFromPixel(pixel);
		popup1.setPosition(coord);
		$(elementPopup1).attr('title', 'Group 10 Tiles');
		$(elementPopup1).attr('data-content', '<b>TileID: </b>'+feature.get('tileID') +
            '</br><b>Correlation Dactor:</b>' + feature.get('correlation_factor'));
        //console.log(elementPopup1)
		$(elementPopup1).popover({'placement': 'top', 'html': true});
		$(elementPopup1).popover('show');
	}
});

map_intc.on('pointermove', function(event){
	if(event.dragging) {
		$(elementPopup1).popover('dispose');
		return;
	}
	var pixel = map_intc.getEventPixel(event.originalEvent);
	var hit = map_intc.hasFeatureAtPixel(pixel);
	map_intc.getTarget().style.cursor = hit ? 'pointer' : '';
})
