# OpenET - Landsat Near Realtime (NRT) Algorithms

Generate synthetic level 2 (surface reflectance) images for any Landsat 8 collection 2 tier 1 TOA image.

## Example

```
image_id = 'LANDSAT/LC08/C02/T1_RT_TOA/LC08_043034_20230710'
sr_image = openet.nrt.landsat8(ee.Image(image_id))
```
