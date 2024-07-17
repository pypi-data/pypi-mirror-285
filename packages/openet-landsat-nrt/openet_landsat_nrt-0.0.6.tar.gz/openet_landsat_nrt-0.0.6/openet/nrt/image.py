import ee
import openet.core

from openet.nrt import lst
from openet.nrt import tasumi


def landsat8(landsat_toa):

    # Server side objects
    path = ee.Number(landsat_toa.get('WRS_PATH'))
    row = ee.Number(landsat_toa.get('WRS_ROW'))
    date = ee.Date.parse('YYYY-MM-dd', landsat_toa.get('DATE_ACQUIRED'))
    # date = ee.Date(landsat_toa.get('system:time_start'))
    # date = date.update(hour=0, minute=0, second=0)

    # Hard coding to use Landsat 8 collection IDs for now
    # landsat_toa = ee.Image(f'LANDSAT/LC08/C02/T1_RT_TOA/{scene_id.upper()}')

    # # Get date, path, and row from the scene ID for now
    # path = int(scene_id[5:8])
    # row = int(scene_id[8:11])
    # date = ee.Date.parse('YYYYMMdd', scene_id[12:20])

    # # Can't process images outside CONUS using NLDAS meteorology
    # if path < 10 or path > 48:
    #     raise ValueError(f'Path must be in the range 10-48')
    # if row < 26 or row > 44:
    #     raise ValueError(f'Row must be in the range 26-44')
    # # if start < '2015-01-01'
    # #     raise ValueError(f'Start date cannot be before 2022-01-01')

    # Cloud mask the source image
    cloud_mask = openet.core.common.landsat_c2_sr_cloud_mask(landsat_toa)

    # Add a buffer around cloud
    cloud_mask = (
        cloud_mask.lt(1)
        .reduceNeighborhood(ee.Reducer.min(), ee.Kernel.circle(30, 'meters'))
        .reduceNeighborhood(ee.Reducer.max(), ee.Kernel.circle(900, 'meters'))
        .eq(0)
        .rename(['cloud_mask'])
    )
    landsat_toa = landsat_toa.updateMask(cloud_mask)

    # Hard coding NLDAS as the meteorology collection (for now)
    meteo_coll_id = 'NASA/NLDAS/FORA0125_H002'
    meteo_coll = ee.ImageCollection(meteo_coll_id)

    # Run Tasumi SR correction
    landsat_rt_sr = tasumi.surface_reflectance(landsat_toa, meteo_coll)

    # TODO: Set the dates or the range as input/function parameters
    # Setting the training date range dynamically to the 2 years prior to the image
    train_start = date.advance(-2, 'year')
    train_end = date.advance(-1, 'day')
    #train_start = '2020-01-01'
    #train_end = '2021-12-31'

    # Use all available months for training
    # Yun found no improvement to limiting the month range in initial testing
    startmonth = 1
    endmonth = 12
    # # The months could be set dynamically based on the target date
    # startmonth = date.advance(-1, 'month').get('month')
    # endmonth = date.advance(1, 'month').get('month')

    # Direct LST random forest
    landsat_lst = lst.randomforest_getparameter(
        landsat_toa,
        meteo_coll=meteo_coll,
        trainstart=train_start,
        trainend=train_end,
        trainparameter='ST_B10',
        path=path,
        row=row,
        startmonth=startmonth,
        endmonth=endmonth,
    )

    # TODO: This might be better structured using copyProperties()
    properties = {
        'CLOUD_COVER': landsat_toa.get('CLOUD_COVER'),
        'CLOUD_COVER_LAND': landsat_toa.get('CLOUD_COVER_LAND'),
        'COLLECTION_CATEGORY': landsat_toa.get('COLLECTION_CATEGORY'),
        'COLLECTION_NUMBER': landsat_toa.get('COLLECTION_NUMBER'),
        'IMAGE_QUALITY_OLI': landsat_toa.get('IMAGE_QUALITY_OLI'),
        'IMAGE_QUALITY_TIRS': landsat_toa.get('IMAGE_QUALITY_TIRS'),
        'LANDSAT_PRODUCT_ID': landsat_toa.get('LANDSAT_PRODUCT_ID'),
        'LANDSAT_SCENE_ID': landsat_toa.get('LANDSAT_SCENE_ID'),
        # Use the TOA image PROCESSING_LEVEL for both properties for now
        # Should the L2 processing level be hardcoded to "L2SP" or something else?
        'L1_PROCESSING_LEVEL': landsat_toa.get('PROCESSING_LEVEL'),
        'PROCESSING_LEVEL': landsat_toa.get('PROCESSING_LEVEL'),
        # 'PROCESSING_LEVEL': 'L2SP',
        'SENSOR_ID': landsat_toa.get('SENSOR_ID'),
        'SPACECRAFT_ID': landsat_toa.get('SPACECRAFT_ID'),
        'SUN_AZIMUTH': landsat_toa.get('SUN_AZIMUTH'),
        'SUN_ELEVATION': landsat_toa.get('SUN_ELEVATION'),
        'UTM_ZONE': landsat_toa.get('UTM_ZONE'),
        'WRS_PATH': landsat_toa.get('WRS_PATH'),
        'WRS_ROW': landsat_toa.get('WRS_ROW'),
        # 'WRS_TYPE': landsat_rt.get('WRS_TYPE'),
        'system:time_start': landsat_toa.get('system:time_start'),
        'system:index': landsat_toa.get('system:index'),
        # 'system:id': landsat_toa.get('system:id'),
    }

    # Scale (unscale?) the reflectance and LST to match a LANDSAT/LC08/C02/T1_L2 image
    # Setting output type to match T1_L2 image types
    output_img = (
        landsat_rt_sr.subtract(-0.2).divide(0.0000275).round().clamp(0, 65535).uint16()
        .addBands([landsat_lst.subtract(149.0).divide(0.00341802).round().clamp(0, 65535).uint16()])
        .addBands(landsat_toa.select(['QA_PIXEL', 'QA_RADSAT']))
        .set(properties)
    )

    return output_img
