use std::time::Instant;

use gdal::{errors::GdalError, raster::ResampleAlg, GeoTransformEx};

const MAX_POINTS: usize = 10_000;

pub struct ElevationDataset {
    ds: gdal::Dataset,
}

#[derive(thiserror::Error, Debug, Clone)]
pub enum LookupError {
    #[error("out of bounds: {0:?}")]
    OutOfBounds((f64, f64)),
    #[error("too many points")]
    TooManyPoints,
    #[error(transparent)]
    GdalError(GdalError),
}

impl ElevationDataset {
    pub fn open(path: &str) -> eyre::Result<Self> {
        let ds = gdal::Dataset::open(path)?;
        Ok(Self { ds })
    }

    pub fn lookup(&self, points: Vec<(f64, f64)>) -> Result<Vec<i32>, LookupError> {
        if points.len() > MAX_POINTS {
            return Err(LookupError::TooManyPoints);
        }

        let start = Instant::now();
        metrics::counter!("lookup_total").increment(1);
        metrics::histogram!("lookup_points").record(points.len() as f64);
        let band = self.ds.rasterband(1).map_err(LookupError::GdalError)?;
        let t = self.ds.geo_transform().map_err(LookupError::GdalError)?;

        let mut vals = Vec::new();
        for &(x, y) in &points {
            let (p, l) = t.invert().map_err(LookupError::GdalError)?.apply(x, y);

            let res = band.read_as::<i32>(
                (p.floor() as isize, l.floor() as isize),
                (1, 1),
                (1, 1),
                Some(ResampleAlg::NearestNeighbour),
            );
            match res {
                Ok(buf) => {
                    vals.push(buf.data[0]);
                }
                Err(GdalError::CplError {
                    class: 3,
                    number: 5,
                    msg,
                }) => {
                    tracing::warn!(%msg, %x, %y, "out of supported bounds");
                    metrics::counter!("lookup_out_of_bounds").increment(1);
                    return Err(LookupError::OutOfBounds((x, y)));
                }
                Err(e) => {
                    return Err(LookupError::GdalError(e));
                }
            }
        }
        let elapsed = start.elapsed().as_secs_f64();
        metrics::histogram!("lookup_duration_secs").record(elapsed);
        tracing::info!("Looked up {} points in {:.2}s", points.len(), elapsed);
        Ok(vals)
    }
}

#[cfg(test)]
mod tests {
    #![feature(assert_matches)]

    use super::*;
    use std::assert_matches::assert_matches;

    const SAMPLE_DATA: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/sample_data/index.vrt");

    fn init() {
        static INIT: std::sync::Once = std::sync::Once::new();
        INIT.call_once(|| {
            tracing_subscriber::fmt::init();
        });
    }

    #[test]
    fn test_known_good_value() {
        init();
        let ds = ElevationDataset::open(SAMPLE_DATA).unwrap();
        let vals = ds.lookup(vec![(-105.6732, 40.0968)]).unwrap();
        assert_eq!(vals[0], 2983);
    }

    #[test]
    fn test_outside() {
        init();
        let ds = ElevationDataset::open(SAMPLE_DATA).unwrap();
        let res = ds.lookup(vec![(0.0, 0.0)]);
        assert_matches!(res, Err(LookupError::OutOfBounds((0.0, 0.0))));
    }
}
