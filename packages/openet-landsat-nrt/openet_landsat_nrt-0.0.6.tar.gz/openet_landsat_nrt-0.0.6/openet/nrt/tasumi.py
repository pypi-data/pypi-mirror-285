import math

import ee


def surface_reflectance(refl_toa_image, meteo_coll):
    """Tasumi at-surface reflectance

    Parameters
    ----------
    refl_toa_image : ee.Image
    meteo_coll : ee.ImageCollection

    Returns
    -------
    ee.Image

    """

    scene_time = ee.Number(refl_toa_image.get('system:time_start'))
    scene_date = ee.Date(refl_toa_image.get('system:time_start'))
    doy = ee.Number(scene_date.getRelative('day', 'year')).add(1).double()
    hour = ee.Number(scene_date.getFraction('day')).multiply(24)

    # TODO: This should be a function parameter or a global dataset
    #   to support global applications
    # CGM - The NED asset is deprecated, switching to the SRTM asset
    #   since it is already being used in model.py and provides global support
    elev = ee.Image('USGS/SRTMGL1_003')
    # elev = ee.Image('USGS/3DEP/10m')
    # elev = ee.Image('NASA/NASADEM_HGT/001')
    # # elev = ee.Image('USGS/NED')

    lat = ee.Image.pixelLonLat().select(['latitude']).multiply(math.pi / 180)
    lon = ee.Image.pixelLonLat().select(['longitude']).multiply(math.pi / 180)

    terrain = ee.call('Terrain', elev)

    slope = terrain.select(['slope']).multiply(math.pi / 180)
    aspect = terrain.select(['aspect']).multiply(math.pi / 180).subtract(math.pi)

    # Mean atmospheric pressure [kPa]
    pair = elev.expression('101.3 * pow((293 - 0.0065 * b()) / 293, 5.26)')

    # Interpolate meteorology (NLDAS) image at Landsat scene time
    meteo_prev_img = meteo_coll.filterDate(scene_date.advance(-1, 'hour'), scene_date).first()
    meteo_next_img = meteo_coll.filterDate(scene_date, scene_date.advance(1, 'hour')).first()
    meteo_prev_time = ee.Number(meteo_prev_img.get('system:time_start'))
    meteo_next_time = ee.Number(meteo_next_img.get('system:time_start'))

    # Calculate time ratio of Landsat image between meteorology images
    time_ratio_img = scene_time.subtract(meteo_prev_time).divide(meteo_next_time.subtract(meteo_prev_time))

    # Interpolate NLDAS values at Landsat image time
    meteo_img = (
        meteo_next_img.subtract(meteo_prev_img).multiply(time_ratio_img).add(meteo_prev_img)
        .set({'system:time_start': scene_time, 'system:time_end': scene_time})
    )

    # Calculate vapor pressure from specific humidity
    # TODO: Band name should be a function parameter
    q = meteo_img.select(['specific_humidity'])
    ea = pair.multiply(q).divide(q.multiply(0.378).add(0.622))

    # Atmospheric precipitable water
    w = pair.multiply(0.14).multiply(ea).add(2.1)

    def cos_theta_mountain_func(acq_doy, acq_time, lat, lon, slope, aspect):
        delta = acq_doy.multiply(2 * math.pi / 365).subtract(1.39435).sin().multiply(0.40928)
        b = acq_doy.subtract(81).multiply(2 * math.pi / 364)
        sc = b.multiply(2).sin().multiply(0.1645).subtract(b.cos().multiply(0.1255)).subtract(b.sin().multiply(0.025))
        solar_time = lon.multiply(12 / math.pi).add(acq_time).add(sc)
        # solar_time = lon.expression(
        #     't + (lon * 12 / pi) + sc',
        #     {'pi': math.pi, 't': ee.Image.constant(acq_time), 'lon': lon, 'sc': ee.Image.constant(sc)}
        # )
        omega = solar_time.subtract(12).multiply(math.pi / 12)
        cos_theta = lat.expression(
            '(sin(lat) * slope_c * delta_s) - '
            '(cos(lat) * slope_s * cos(aspect) * delta_s) + '
            '(cos(lat) * slope_c * cos(omega) * delta_c) + '
            '(sin(lat) * slope_s * cos(aspect) * cos(omega) * delta_c) + '
            '(sin(aspect) * slope_s * sin(omega) * delta_c)',
            {
                'lat': lat, 'aspect': aspect, 'slope_c': slope.cos(), 'slope_s': slope.sin(),
                'omega': omega,
                # CGM - Do these need to be constant images?
                'delta_c': ee.Image.constant(delta.cos()),
                'delta_s': ee.Image.constant(delta.sin()),
            }
        )
        cos_theta = cos_theta.divide(slope.cos()).max(ee.Image.constant(0.1))

        return cos_theta

    cos_theta = cos_theta_mountain_func(doy, hour, lat, lon, slope, aspect)

    # TODO: Add support back in for running Landsat 5 and 7 images also
    # TODO: Double check the coefficients since the original band numbers seemed to be for L5/L7
    #   but maybe the values are right and it is just the column headings
    # Calibrated Landsat Constants LS8
    # Coeff        Band2      Band3      Band4      Band5     Band6      Band7
    c1 = ee.Image([0.987,     2.148,     0.942,     0.248,    0.260,     0.315])
    c2 = ee.Image([-0.000727, -0.000199, -0.000261, -0.00041, -0.001084, -0.000975])
    c3 = ee.Image([0.000037,  0.000058,  0.000406,  0.000563, 0.000675,  0.004012])
    c4 = ee.Image([0.0869,    0.0464,    0.0928,    0.2256,   0.0632,    0.0116])
    c5 = ee.Image([0.0788,    -1.0962,   0.1125,    0.7991,   0.7549,    0.6906])
    cb = ee.Image([0.640,     0.310,     0.286,     0.189,    0.274,     -0.186])

    tau_in = pair.multiply(c2).divide(cos_theta).subtract(w.multiply(c3).add(c4).divide(cos_theta))\
        .exp().multiply(c1).add(c5)
    tau_out = pair.multiply(c2).subtract(w.multiply(c3).add(c4)).exp().multiply(c1).add(c5)

    refl_sur_image = (
        refl_toa_image
        .select(['B2', 'B3', 'B4', 'B5', 'B6', 'B7'])
        .expression(
            '(b() + cb * (tau_in - 1)) / (tau_in * tau_out)',
            {'cb': cb, 'tau_in': tau_in, 'tau_out': tau_out})
        .rename(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7'])
    )

    return refl_sur_image
