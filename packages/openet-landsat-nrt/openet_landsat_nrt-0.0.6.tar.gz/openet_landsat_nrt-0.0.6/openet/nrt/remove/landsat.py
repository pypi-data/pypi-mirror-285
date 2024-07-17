import ee


def get_landsat_rt(start, end, path, row, cloud_cover_max=50):
    """Get Landsat 8 real time raw data image collection"""

    landsat8_rt_coll = (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_RT')
        .filterDate(start, end)
        .filterMetadata('WRS_PATH', 'equals', path)
        .filterMetadata('WRS_ROW', 'equals', row)
        .filterMetadata('CLOUD_COVER', 'less_than', cloud_cover_max)
        .filterMetadata('CLOUD_COVER_LAND', 'greater_than', -0.5)
        # CGM - Check if the DATA_TYPE filtering is needed also
        # .filterMetadata('DATA_TYPE', 'equals', 'L1TP')
    ).map(landsat_rt_preprocess)

    return landsat8_rt_coll


def get_landsat_toa(start, end, path, row, cloud_cover_max=50):
    """Get Landsat 8 real time toa data for SR atmospheric correction,
    which is used in NDVI calculation for emissivity
    """

    landsat8_rt_toa = (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA_RT')
        .filterDate(start, end)
        .filterMetadata('WRS_PATH', 'equals', path)
        .filterMetadata('WRS_ROW', 'equals', row)
        .filterMetadata('CLOUD_COVER', 'less_than', cloud_cover_max)
        .filterMetadata('CLOUD_COVER_LAND', 'greater_than', -0.5)
        # CGM - Check if the DATA_TYPE filtering is needed also
        # .filterMetadata('DATA_TYPE', 'equals', 'L1TP')
    )

    return landsat8_rt_toa


def get_landsat_l2(start, end, path, row, startmonth=1, endmonth=12, cloud_cover_max=50):
    """Get Landsat 8 and Landsat 9 collection 2 image collection"""

    landsat8 = (
        ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterDate(start, end)
        .filterMetadata('WRS_PATH', 'equals', path)
        .filterMetadata('WRS_ROW', 'equals', row)
        .filter(ee.Filter.calendarRange(startmonth, endmonth, 'month'))
        .filterMetadata('CLOUD_COVER_LAND', 'less_than', cloud_cover_max)
        .filterMetadata('CLOUD_COVER_LAND', 'greater_than', -0.5)
        #.select(['ST_ATRAN', 'ST_DRAD', 'ST_EMIS', 'ST_TRAD', 'ST_URAD', 'QA_PIXEL'])
        .map(landsat_l2_preprocess)
    )

    return landsat8

    # landsat9 = (
    #     ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
    #     .filterDate(start, end)
    #     .filterMetadata('WRS_PATH', 'equals', path)
    #     .filterMetadata('WRS_ROW', 'equals', row)
    #     .filter(ee.Filter.calendarRange(startmonth, endmonth, 'month'))
    #     .filterMetadata('CLOUD_COVER_LAND', 'less_than', cloud_cover_max)
    #     .filterMetadata('CLOUD_COVER_LAND', 'greater_than', -0.5)
    #     .select(['ST_ATRAN', 'ST_DRAD', 'ST_EMIS', 'ST_TRAD', 'ST_URAD', 'QA_PIXEL'])
    # )

    # return landsat8.merge(landsat9)


def landsat_rt_preprocess(img):
    """Scale factors and convert thermal DN value to TOA temperature (Kelvin)"""

    opticalBands = img.select('B.').multiply(0.00002).add(-0.1)
    thermalBands = img.select('B10').multiply(0.0003342).add(0.1)
    thermalBands = thermalBands.expression(
        'k2 / (log(k1 / rc + 1))', {'k2': 1321.0789, 'k1': 774.8853, 'rc': thermalBands}
    ).rename('B10')
    date1 = ee.Date(img.get('system:time_start'))
    miltime = ee.Date.fromYMD(date1.get('year'), date1.get('month'), date1.get('day')).millis()

    return (
        ee.Image(img).addBands(opticalBands, overwrite=True)
        .addBands(thermalBands, overwrite=True)
        .set({'date': miltime})
    )


def landsat_l2_preprocess(img):
    """Scale factors and convert thermal DN value to TOA temperature (Kelvin)"""

    opticalBands = img.select('SR_B.').multiply(0.0000275).add(-0.2)
    thermalBands = img.select('ST_B10').multiply(0.00341802).add(149.0).rename('ST_B10')

    return ee.Image(img).addBands(opticalBands, overwrite=True).addBands(thermalBands, overwrite=True)
