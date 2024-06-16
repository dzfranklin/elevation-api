use std::{
    future::ready,
    sync::{Arc, Mutex},
    time::Instant,
};

use axum::{
    extract::{MatchedPath, Request},
    middleware::{self, Next},
    response::{Html, IntoResponse},
    routing::{get, post},
    Json, Router,
};
use elevation_api::ElevationDataset;
use metrics_exporter_prometheus::{Matcher, PrometheusBuilder, PrometheusHandle};
use tokio::signal;

#[tokio::main]
async fn main() -> eyre::Result<()> {
    if let Err(err) = dotenvy::from_filename(".env") {
        eprintln!("Skipping loading .env: {}", err);
    }
    color_eyre::install()?;
    tracing_subscriber::fmt::init();
    let metrics = setup_metrics()?;

    let host: String = dotenvy::var("HOST").unwrap_or_else(|_| "0.0.0.0".into());
    let port = dotenvy::var("PORT").unwrap_or_else(|_| "3000".into());
    let addr = format!("{}:{}", host, port);
    let dataset_path = dotenvy::var("ELEVATION_DATASET").expect("ELEVATION_DATASET must be set");

    let dataset = Arc::new(Mutex::new(ElevationDataset::open(&dataset_path)?));

    let app = Router::new()
        .route("/", get(|| async { Html("Data from European Space Agency, Sinergise (2021).  <i>Copernicus Global Digital Elevation Model</i>.  Distributed by OpenTopography.  https://doi.org/10.5069/G9028PQB")}))
        .route(
            "/elevation",
            post(move |req| post_elevations(req, dataset.clone())),
        )
        .route("/health", get(|| async { "OK" }))
        .route("/metrics", get(move || ready(metrics.render())))
        .route_layer(middleware::from_fn(track_metrics));

    tracing::info!("Starting server on http://{}", addr);
    let listener = tokio::net::TcpListener::bind(addr).await?;

    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;
    Ok(())
}

#[derive(serde::Deserialize)]
struct PostElevationRequest {
    points: Vec<(f64, f64)>,
}

#[derive(serde::Serialize)]
struct PostElevationsResponse {
    elevations: Vec<i32>,
}

async fn post_elevations(
    Json(payload): Json<PostElevationRequest>,
    dataset: Arc<Mutex<ElevationDataset>>,
) -> impl IntoResponse {
    let dataset = dataset.lock().unwrap();
    match dataset.lookup(payload.points) {
        Ok(elevations) => (
            http::StatusCode::OK,
            Json(PostElevationsResponse { elevations }),
        )
            .into_response(),
        Err(e) => match e {
            elevation_api::LookupError::TooManyPoints => {
                (http::StatusCode::BAD_REQUEST, "Too many points".to_string()).into_response()
            }
            elevation_api::LookupError::OutOfBounds((x, y)) => (
                http::StatusCode::BAD_REQUEST,
                format!("Point ({}, {}) is out of bounds", x, y),
            )
                .into_response(),
            elevation_api::LookupError::GdalError(e) => (
                http::StatusCode::INTERNAL_SERVER_ERROR,
                format!("Internal error: {}", e),
            )
                .into_response(),
        },
    }
}

fn setup_metrics() -> eyre::Result<PrometheusHandle> {
    const EXPONENTIAL_SECONDS: &[f64] = &[
        0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0,
    ];
    PrometheusBuilder::new()
        .set_buckets_for_metric(
            Matcher::Full("http_requests_duration_seconds".into()),
            EXPONENTIAL_SECONDS,
        )?
        .set_buckets_for_metric(
            Matcher::Full("lookup_duration_secs".into()),
            EXPONENTIAL_SECONDS,
        )?
        .set_buckets_for_metric(
            Matcher::Full("lookup_points".into()),
            &[10.0, 100.0, 1_000.0, 10_000.0, 100_000.0],
        )?
        .install_recorder()
        .map_err(Into::into)
}

async fn track_metrics(req: Request, next: Next) -> impl IntoResponse {
    let start = Instant::now();
    let path = if let Some(matched_path) = req.extensions().get::<MatchedPath>() {
        matched_path.as_str().to_owned()
    } else {
        req.uri().path().to_owned()
    };
    let method = req.method().clone();

    let response = next.run(req).await;

    let latency = start.elapsed().as_secs_f64();
    let status = response.status().as_u16().to_string();

    let labels = [
        ("method", method.to_string()),
        ("path", path),
        ("status", status),
    ];

    metrics::counter!("http_requests_total", &labels).increment(1);
    metrics::histogram!("http_requests_duration_seconds", &labels).record(latency);

    response
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }
    tracing::info!("Shutting down");
}
