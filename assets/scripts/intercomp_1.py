# step 1. preprocessing
# configuration
group_name = 'group_10'
base_dir = r"GEOGRAPHIC INFORMATION SYSTEMS/laboratory"
intercmp_dir = base_dir + '/output/intercomparison/'

ghs_input = base_dir + r"/data/GHS_POP_E2015_GLOBE_R2019A_4326_30ss_V1_0/GHS_POP_E2015_GLOBE_R2019A_4326_30ss_V1_0.tif"
ppp_input = base_dir + r"/data/ppp_2015_1km_Aggregated.tif"
mask = base_dir + r"/data/GIS_lab_areas.gpkg|layername=" + group_name

# input
group = QgsProject.instance().mapLayersByName(group_name)[0]

def clip2group(raster_in, raster_out, mask):
    res = processing.runAndLoadResults("gdal:cliprasterbymasklayer", 
        {'INPUT': raster_in,'MASK': mask, 'SOURCE_CRS':None,'TARGET_CRS':None,'NODATA':None,'ALPHA_BAND':False,'CROP_TO_CUTLINE': True,'KEEP_RESOLUTION':False,'SET_RESOLUTION':False,'X_RESOLUTION':None,'Y_RESOLUTION':None,'MULTITHREADING':False,'OPTIONS':'','DATA_TYPE':0,'EXTRA':'',
        'OUTPUT': raster_out
        })
    print('[DONE] clip raster layer by mask layer %s: %r' % (group_name, res))

# clip raster by mask layer
ghs_output = intercmp_dir + r"ghs.tif"
clip2group(ghs_input, ghs_output, mask)

ppp_output = intercmp_dir + r"worldpop.tif"
clip2group(ppp_input, ppp_output, mask)

# align worldpop to ghs
ghs_input = ghs_output
ghs_output = intercmp_dir + r"ghs_clip.tif"
ghs_item = QgsAlignRaster.Item(ghs_input, ghs_output)

ppp_input = ppp_output
ppp_output = intercmp_dir + r"worldpop_clip.tif"
ppp_item = QgsAlignRaster.Item(ppp_input, ppp_output)

alignClass = QgsAlignRaster()
alignClass.setRasters([ghs_item, ppp_item])
alignClass.setParametersFromRaster(ghs_input)
res = alignClass.run()
print('[DONE] align worldpop to ghs: ', res, alignClass.errorMessage())


# to integer
ghs_input = ghs_output
ghs_output = intercmp_dir + r"ghs_clip_int.tif"
res = processing.runAndLoadResults("gdal:translate", 
    {'INPUT': ghs_input,'TARGET_CRS':None,'NODATA':None,'COPY_SUBDATASETS':False,'OPTIONS':'','EXTRA':'','DATA_TYPE':2,
        'OUTPUT': ghs_output})
print('[DONE] translate ghs to integer: ', res)  
ppp_input = ppp_output
ppp_output = intercmp_dir + r"worldpop_clip_int.tif"
res = processing.runAndLoadResults("gdal:translate", 
    {'INPUT': ppp_input,'TARGET_CRS':None,'NODATA':None,'COPY_SUBDATASETS':False,'OPTIONS':'','EXTRA':'','DATA_TYPE':2,
        'OUTPUT': ppp_output})

print('[DONE] translate worldpop to integer: ', res) 

# adjust null for worldpop
ppp_input = ppp_output
ppp_output = intercmp_dir + r"worldpop_clip_int_setnull.tif"
processing.runAndLoadResults("qgis:rastercalculator", {'EXPRESSION':'(\"worldpop_clip_int@1\" < 0)*0+(\"worldpop_clip_int@1\" >= 0)*\"worldpop_clip_int@1\"','LAYERS':[ppp_input],'CELLSIZE':None,'EXTENT':None,'CRS':None,'OUTPUT':ppp_output})

ghs_input = ghs_output
ppp_input = ppp_output
ppp_output = intercmp_dir + r"worldpop_clip_int_setnull_replace.tif"

processing.runAndLoadResults("qgis:rastercalculator", {'EXPRESSION':'(\"ghs_clip_int@1\" < 0)*(-200) + (\"ghs_clip_int@1\" >=0)*\"worldpop_clip_int_setnull@1\"','LAYERS':[ppp_input],'CELLSIZE':None,'EXTENT':None,'CRS':None,'OUTPUT':ppp_output})

print('[DONE] adjust null for worldpop')

# set null
null_val = -200
ppp_input = ppp_output
ppp_output = intercmp_dir + r"worldpop_intercomp_final.tif"
res = processing.runAndLoadResults("grass7:r.null",
    {'map': ppp_input,'setnull':null_val,
        'null':None,'-f':False,'-i':False,'-n':False,'-c':False,'-r':False,
        'output':ppp_output,'GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})
        
ghs_input = ghs_output
ghs_output = intercmp_dir + r"ghs_intercomp_final.tif"
res = processing.runAndLoadResults("grass7:r.null",
    {'map': ghs_input,'setnull':null_val,
        'null':None,'-f':False,'-i':False,'-n':False,'-c':False,'-r':False,
        'output':ghs_output,'GRASS_REGION_PARAMETER':None,'GRASS_REGION_CELLSIZE_PARAMETER':0,'GRASS_RASTER_FORMAT_OPT':'','GRASS_RASTER_FORMAT_META':''})
print('[DONE] set null value ("%s") for ghs and worldpop' % null_val)
