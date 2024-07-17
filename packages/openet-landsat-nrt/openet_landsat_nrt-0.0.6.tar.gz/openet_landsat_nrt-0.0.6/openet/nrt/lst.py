import math
import pprint

import ee


def randomforest_getparameter(
        #rt_img,
        toa_img,
        meteo_coll,
        trainstart,
        trainend,
        trainparameter,
        path,
        row,
        startmonth=1,
        endmonth=12,
):
    """"""

    #toa_img = landsat_rt_preprocess(rt_img)

    date = ee.Date(toa_img.get('system:time_start'))

    bands = [
        'emissivity_band13', 'lon', 'lat',
        'B10', 'B2', 'B6', 'ndvi', 'doy', 'landcover', 'elevation',
    ]
    # Note, these are hard coded to the NLDAS band names
    meteo_bands = [
        'specific_humidity', 'shortwave_radiation', 'longwave_radiation',
        'temperature', 'wind_v', 'wind_u'
    ]
    bands = bands + meteo_bands

    image_agg = prepare_randomforest(
        meteo_coll.select(meteo_bands), trainstart, trainend, path, row,
        startmonth, endmonth
    )
    samples = image_agg.map(buildsample).flatten()
    rf = (
        ee.Classifier.smileRandomForest(100, 5, 20)
        .setOutputMode('REGRESSION')
        .train(samples, trainparameter, bands)
    )

    dem = ee.Image('USGS/SRTMGL1_003')
    aster_ged = (
        ee.Image('NASA/ASTER_GED/AG100_003')
        .select(['emissivity_band13'])
        # .select(['emissivity_band13', 'emissivity_band14'])
    )
    nlcd = (
        ee.ImageCollection('USGS/NLCD_RELEASES/2019_REL/NLCD')
        .filter(ee.Filter.eq('system:index', '2019')).first().select('landcover')
        .remap([0, 11, 21, 22, 23, 24, 31, 41, 42, 43, 52, 71, 81, 82, 90, 95],
               [0, 1, 2, 2, 2, 2, 3, 4, 4, 4, 5, 7, 7, 8, 9, 9])
    )

    # TODO: Figure out how to get fastGaussianBlur support
    #   Trying bilinear resampling in the mean time
    meteo_img = (
        ee.Image(meteo_coll.filterDate(date.advance(-1, 'hour'), date).first())
        .select(meteo_bands)
        # .resample('bilinear')
        # .fastGaussianBlur(3000)
    )

    image_topredict = toa_img.addBands([
        meteo_img,
        dem.rename('elevation'),
        nlcd.rename('landcover'),
        aster_ged,
        toa_img.normalizedDifference(['B5', 'B4']).rename('ndvi'),
        ee.Image.constant(date.getRelative('day', 'year').add(1)).rename('doy'),
        # ee.Image.constant(date.get('day')).rename('doy'),
        toa_img.select(['B4']).multiply(0).add(ee.Image.pixelLonLat()).select(['longitude'], ['lon']),
        toa_img.select(['B4']).multiply(0).add(ee.Image.pixelLonLat()).select(['latitude'], ['lat']),
    ])

    return (
        ee.Image(image_topredict.classify(rf, trainparameter))
        .rename(trainparameter)
        .setDefaultProjection(toa_img.select(['B5']).projection())
        .set({'system:time_start': toa_img.get('system:time_start')})
    )


def prepare_randomforest(
        meteo_coll,
        trainstart,
        trainend,
        path,
        row,
        startmonth,
        endmonth,
):
    """"""

    l8_coll_totrain_toa = (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_RT_TOA')
        # ee.ImageCollection('LANDSAT/LC08/C02/T1_RT')
        .filterMetadata('CLOUD_COVER', 'less_than', 50)
        .filterMetadata('CLOUD_COVER', 'greater_than', -0.5)
        .filterDate(trainstart, trainend)
        .filterMetadata('WRS_PATH', 'equals', path)
        .filterMetadata('WRS_ROW', 'equals', row)
        .filter(ee.Filter.calendarRange(startmonth, endmonth, 'month'))
        .select(['B2', 'B4', 'B5', 'B6', 'B10'])
        # .map(landsat_rt_preprocess)
    )

    l8_coll_totrain_l2 = (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterMetadata('CLOUD_COVER', 'less_than', 50)
        .filterMetadata('CLOUD_COVER', 'greater_than', -0.5)
        .filterDate(trainstart, trainend)
        .filterMetadata('WRS_PATH', 'equals', path)
        .filterMetadata('WRS_ROW', 'equals', row)
        .filter(ee.Filter.calendarRange(startmonth, endmonth, 'month'))
        .map(landsat_l2_preprocess)
    )

    meteo_filter = ee.Filter.maxDifference(
        1000 * 60 * 60 * 4, "system:time_start", None, "system:time_start", None
    )
    meteo_prev_filter = ee.Filter.And(
        meteo_filter,
        ee.Filter.greaterThan("system:time_start", None, "system:time_start", None)
    )
    image_agg = ee.ImageCollection(
        ee.Join.saveBest('landsat_l2', 'landsat_totrain')
        .apply(
            l8_coll_totrain_toa, l8_coll_totrain_l2,
            ee.Filter.equals("system:time_start", None, "system:time_start", None)
        )
    )
    image_agg = ee.ImageCollection(
        ee.Join.saveBest('meteo_prev_match', 'meteo_prev_metric')
        .apply(image_agg, meteo_coll, meteo_prev_filter)
    )

    return ee.ImageCollection(image_agg)


def buildsample(img):
    """"""
    date = ee.Date(img.get('system:time_start'))
    dem = ee.Image('USGS/SRTMGL1_003')
    aster_ged = (
        ee.Image('NASA/ASTER_GED/AG100_003')
        .select(['emissivity_band13'])
        # .select(['emissivity_band13', 'emissivity_band14'])
    )
    nlcd = (
        ee.ImageCollection('USGS/NLCD_RELEASES/2019_REL/NLCD')
        .filter(ee.Filter.eq('system:index', '2019')).first().select('landcover')
        .remap([0, 11, 21, 22, 23, 24, 31, 41, 42, 43, 52, 71, 81, 82, 90, 95],
               [0, 1, 2, 2, 2, 2, 3, 4, 4, 4, 5, 7, 7, 8, 9, 9])
        .rename('landcover')
    )

    b10 = img.select('B10')
    b10_class = (
        nlcd.multiply(0)
        .where(b10.lte(250), 10)
        .where(b10.lte(280).And(b10.gt(250)), 20)
        .where(b10.lte(290).And(b10.gt(280)), 30)
        .where(b10.lte(300).And(b10.gt(290)), 40)
        .where(b10.lte(310).And(b10.gt(300)), 50)
        .where(b10.lte(320).And(b10.gt(310)), 60)
        .where(b10.lte(330).And(b10.gt(320)), 70)
        .where(b10.lte(340).And(b10.gt(330)), 80)
        .where((b10.gt(340)), 90)
        .rename('b10_class')
    )

    # TODO: Figure out how to get fastGaussianBlur support
    #   Trying bilinear resampling in the mean time
    # TODO: Check if day band should actually be doy
    image_all = img.addBands([
        ee.Image(img.get('landsat_l2')),  # ST_B10
        ee.Image(img.get('meteo_prev_match')),
        # ee.Image(img.get('meteo_prev_match')).resample('bilinear'),
        # ee.Image(img.get('meteo_prev_match')).fastGaussianBlur(3000),
        dem,
        nlcd,
        b10_class,
        aster_ged,
        img.normalizedDifference(['B5', 'B4']).rename('ndvi'),
        ee.Image.constant(date.getRelative('day', 'year').add(1)).rename('doy'),
        # ee.Image.constant(date.get('day')).rename('doy'),
        img.select(['B4']).multiply(0).add(ee.Image.pixelLonLat()).select(['longitude'], ['lon']),
        img.select(['B4']).multiply(0).add(ee.Image.pixelLonLat()).select(['latitude'], ['lat']),
    ])

    samples = image_all.stratifiedSample(
        numPoints=1000,
        classBand='b10_class',
        region=img.geometry(),
        scale=30,
        dropNulls=True,
        # factor=5e-5,
    )
    return samples


def landsat_l2_preprocess(img):
    """Apply scale factors and offsets to convert to reflectance and temperature (Kelvin)"""

    # For training, only the LST band is needed from the level 2 images
    return (
        ee.Image(img)
        .select(['ST_B10']).multiply(0.00341802).add(149.0)
        .set({'system:time_start': img.get('system:time_start')})
    )


# # CGM - Simplified L2 function that only processes the thermal band
# def landsat_l2_preprocess(img):
#     """Scale factors and convert thermal DN value to TOA temperature (Kelvin)"""
#
#     opticalBands = img.select('SR_B.').multiply(0.0000275).add(-0.2)
#     thermalBands = img.select('ST_B10').multiply(0.00341802).add(149.0).rename('ST_B10')
#
#     return (
#         ee.Image(img)
#         .addBands(opticalBands, overwrite=True)
#         .addBands(thermalBands, overwrite=True)
#         # .set({'system:time_start': img.get('system:time_start')})
#     )


# # CGM - This function isn't needed if TOA image is used as input
# #   and SUN_ELEVATION correction is applied (it wasn't in the original code)
# def landsat_rt_preprocess(img):
#     """Scale factors and convert thermal DN value to TOA temperature (Kelvin)"""
#     # CGM - The sun elevation normalization is needed to match the TOA collection
#     #   but seems to make the lST worse, leaving off for now to match original approach
#     opticalBands = img.select('B.').multiply(0.00002).add(-0.1)\
#         .divide(ee.Number(img.get('SUN_ELEVATION')).multiply(math.pi / 180).sin())
#     thermalBands = img.select('B10').multiply(0.0003342).add(0.1)
#     thermalBands = thermalBands.expression(
#         'k2 / (log(k1 / rc + 1))', {'k2': 1321.0789, 'k1': 774.8853, 'rc': thermalBands}
#     ).rename('B10')
#
#     return (
#         ee.Image(img)
#         .addBands(opticalBands, overwrite=True)
#         .addBands(thermalBands, overwrite=True)
#         # .set({'system:time_start': img.get('system:time_start')})
#     )



