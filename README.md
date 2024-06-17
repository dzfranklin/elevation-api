# elevation-api

## Dataset preparation

The index vrt file must be built with the argument `-srcnodata "2147483647"`

E.g.

```bash
gdalbuildvrt -srcnodata "2147483647" index.vrt *.tif
```
