import attribution

description = f"""
Use this API to lookup elevation data for coordinates.

**All coordinates are in [WGS84](https://epsg.io/4326) and specified in longitude, latitude order.**

## License

You must follow the applicable terms of the license or licenses for any data you use.

Note that I have altered the data used here. The original data has a higher precision. See the source code of this 
service at [github.com/dzfranklin/elevation-api](https://github.com/dzfranklin/elevation-api) for more information. 
Any errors in the data are probably my fault. This is a hobby project provided as-is and is not suitable for any serious 
use. You can contact me at daniel@danielzfranklin.org if you have any questions.

This API includes data from:

{attribution.html}
"""
