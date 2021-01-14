# step 2. processing
# configuration
group_name = 'group_10'
base_dir = r"/Users/elexu/读书/米兰理工（GIS-CS）/GEOGRAPHIC INFORMATION SYSTEMS/laboratory"
intercmp_dir = base_dir + '/output/intercomparison/'

ghs_input = intercmp_dir + r"ghs_intercomp_final.tif"
ppp_input = intercmp_dir + r"worldpop_intercomp_final.tif"
mask = base_dir + r"/data/GIS_lab_areas.gpkg|layername=" + group_name
tiles_output = intercmp_dir + r"clip/"

covar_factor = 'covar_factor' # field name in group vector, covariance value of the tile

# input
group = QgsProject.instance().mapLayersByName(group_name)[0]

# compute difference
diff_output = intercmp_dir + r"intercomp_diff.tif"

processing.runAndLoadResults("qgis:rastercalculator", 
    {'EXPRESSION':'\"ghs_intercomp_final@1\" - \"worldpop_intercomp_final@1\"',
        'LAYERS':[ghs_input],'CELLSIZE':None,'EXTENT':None,'CRS':None,
        'OUTPUT':diff_output})

# basic statistics
stat_output = intercmp_dir + r"intercomp_diff_stats.txt"
processing.run("grass7:r.univar", 
    {'map':[diff_output],'zones':None,'percentile':'','separator':'pipe','-e':False,
        'output': stat_output,'GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0})

# cavariance matrix
covar_output = intercmp_dir + r"covariance_matrix.html"
processing.run('grass7:r.covar',
    {'-r' : True, 'GRASS_REGION_CELLSIZE_PARAMETER' : 0, 'GRASS_REGION_PARAMETER' : None,
        'html' : covar_output, 'map' : [ghs_input, ppp_input] })

## for each tiles
group_layer = QgsProject.instance().mapLayersByName(group_name)[0]
tiles = {}
for feature in group_layer.getFeatures():
    tiles[feature['tileID']] = {
        'x_1': feature['x_1'],
        'y_1': feature['y_1'],
        'x_2': feature['x_2'],
        'y_2': feature['y_2'],
        'id': feature.id(),
    }
dp = group_layer.dataProvider()
if covar_factor not in group_layer.fields().names():
    # create a new field
    dp.addAttributes([QgsField(covar_factor,QVariant.Double)])
    group_layer.updateFields()

cor_fac_idx = group_layer.fields().indexFromName(covar_factor)
print("index for field '%s' is %d" % (covar_factor, cor_fac_idx))
if cor_fac_idx == -1:
    exit(-1)
    
caps = dp.capabilities()

import os
for tid, info in tiles.items():
    # clip
    tiles_rasters = []
    for key, lyr in [("worldpop", ppp_input), ("ghs", ghs_input)]:
        tile_output = tiles_output + key + '_tile_' + str(tid) +".tif"
        processing.run("gdal:cliprasterbyextent",
                       {'INPUT': lyr,
                        'PROJWIN':'{},{},{},{}'.format(info['x_1'], info['x_2'], info['y_2'], info['y_1']),
                        'NODATA':None,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'','OUTPUT':tile_output})
        tiles_rasters.append(tile_output)
        print("[DONE] clip " + tile_output)
        
    # calculate covariance matrix
    res = processing.run('grass7:r.covar',
    {'-r' : True, 'GRASS_REGION_CELLSIZE_PARAMETER' : 0, 'GRASS_REGION_PARAMETER' : None,
        'html' : '{}corr_matrix_tile_{}.html'.format(tiles_output, tid), 'map' : tiles_rasters })
    if res.get('html'):
        print('[DONE] the correlation matrix has written to ', res['html'])
    else:
        print('[FAIL] calcalate correlation matrix: ', res)
        break
        
    # add correlation values to group tiles vector layer
    with open(res['html']) as f:
        f.readline()
        tmp = f.readline().strip().split(' ')[-1].strip()
        print('[DISPLAY] the correlation factor:', tmp)
        if tmp and tmp != 'nan':
            attrs = {cor_fac_idx: float(tmp)}
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                group_layer.dataProvider().changeAttributeValues({info['id']:attrs})
    

print('[DONE] clip')