#![cfg_attr(test, feature(assert_matches))]

use std::time::Instant;

use gdal::{
    errors::{CplErrType, GdalError},
    raster::ResampleAlg,
    GeoTransformEx,
};

const MAX_POINTS: usize = 10_000;

const CPLE_ILLEGAL_ARG: i32 = 5;

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
        maybe_init_gdal();
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
                Err(e) => {
                    if let GdalError::CplError { class, number, .. } = e {
                        if class == CplErrType::Failure as u32 && number == CPLE_ILLEGAL_ARG {
                            tracing::info!(%x, %y, "out of bounds");
                            metrics::counter!("lookup_out_of_bounds").increment(1);
                            return Err(LookupError::OutOfBounds((x, y)));
                        }
                    }
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

fn maybe_init_gdal() {
    static INIT: std::sync::Once = std::sync::Once::new();
    INIT.call_once(|| {
        gdal::config::set_error_handler(|class, number, msg| match class {
            CplErrType::None => (),
            CplErrType::Debug => {
                tracing::debug!("gdal debug: {number}: {msg}");
            }
            CplErrType::Warning => {
                tracing::warn!("gdal warning: {number}: {msg}");
            }
            CplErrType::Failure => {
                if number == CPLE_ILLEGAL_ARG {
                    return;
                }
                tracing::warn!("gdal failure: {number}: {msg}");
            }
            CplErrType::Fatal => {
                tracing::error!("gdal fatal: {number}: {msg}");
            }
        });
    });
}

#[cfg(test)]
mod tests {
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
