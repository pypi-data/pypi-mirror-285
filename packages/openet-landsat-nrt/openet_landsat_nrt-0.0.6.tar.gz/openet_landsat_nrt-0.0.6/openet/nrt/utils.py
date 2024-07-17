import ee


def getAffineTransform(image):
    projection = image.projection()
    json = ee.Dictionary(ee.Algorithms.Describe(projection))
    return ee.List(json.get('transform'))
