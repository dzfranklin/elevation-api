# elevation-api

## Further work

An interesting comparative analysis: https://www.mdpi.com/2072-4292/12/21/3482

Based on this lets focus on AW3D30 and 3DEP

Try to build a single DEM with nodatafilled and just use that

Interesting: https://forum.step.esa.int/t/difference-between-using-a-dem-of-30m-and-90-m-to-insar/13128/5

## Cost-effective hosting

Let's try a hetzner storage box

TODO: Credit https://kokoalberti.com/articles/experiments-with-the-global-jaxa-alos-world-30m-dem-on-aws-s3/ in attribution
of https://earth.jaxa.jp/en/data/policy/

What if we use AW3D30 data for just the UK, and 3DEP for the US?

I think jaxa just rounds to the nearest integer, which might be sensible?

---

gdaltindex -gti_filename cop90.gti -lyr_name elevation cop90.gti.gpkg --optfile cop90_filelist.txt
