group_layer = QgsProject.instance().mapLayersByName('group_10')
group10_layer = group_layer[0]
group10_layer.name()
tiles = {}
for feature in group10_layer.getFeatures():
    tiles[feature['tileID']] = {
        'x_1': feature['x_1'],
        'y_1': feature['y_1'],
        'x_2': feature['x_2'],
        'y_2': feature['y_2'],
        'id': feature.id(),
    }
cor_fac_index = 7 # figure out from attribute table, may change
caps = group10_layer.dataProvider().capabilities()


outputDir = r'/path/to/output/dir'

# get target map
wpop_layer = QgsProject.instance().mapLayersByName('worldpop_intercomp_final')[0]
ghs_layer = QgsProject.instance().mapLayersByName('ghs_intercomp_final')[0]

# path of gda translate
gda_translate = r'/Applications/QGIS3.14.app/Contents/MacOS/bin/gdal_translate'

import os
for tid, info in tiles.items():
    # clip
    tiles_rasters = []
    for lyr in [wpop_layer, ghs_layer]:
        outputFile = str(lyr.name()) + '_tile' + str(tid) +".tif"
        cmd = '{} -projwin {} {} {} {}  -of GTiff "{}" "{}"'.format(gda_translate, info['x_1'], info['y_1'], info['x_2'], info['y_2'], lyr.source(), outputDir + outputFile)
        print('[EXECUTE]'+cmd)
        ret = os.system(cmd)
        print("[DONE] clip " + outputFile + ' ret=' + str(ret>>8))
        qgis.utils.iface.addRasterLayer(str(outputDir + "/" + outputFile), outputFile)
        tiles_rasters.append(outputDir + outputFile)
        
    # calculate covariance matrix
    output = processing.run('grass7:r.covar', { '-r' : True, 'GRASS_REGION_CELLSIZE_PARAMETER' : 0, 'GRASS_REGION_PARAMETER' : None, 'html' : '{}corr_matrix_tile_{}.html'.format(outputDir, tid), 'map' : tiles_rasters })
    if output.get('html'):
        print('[DONE] the correlation matrix has written to ', output['html'])
    else:
        print('[FAIL] calcalate correlation matrix: ', output)
        break
    # add correlation values to group tiles vector layer
    with open(output['html']) as f:
        f.readline()
        tmp = f.readline().strip().split(' ')[-1].strip()
        print('[DISPLAY] the correlation factor:', tmp)
        if tmp and tmp != 'nan':
            attrs = {cor_fac_index: float(tmp)}
            if caps & QgsVectorDataProvider.ChangeAttributeValues:
                group10_layer.dataProvider().changeAttributeValues({info['id']:attrs})
    

print('[DONE] clip')