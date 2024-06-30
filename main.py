import logging
from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.responses import PlainTextResponse, HTMLResponse

import attributions
import docs
from dataset import Dataset
from dataset.source import Source


class Settings(BaseSettings):
    dem_source: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
app = FastAPI(
    title="Elevation API",

    # Configure docs
    openapi_url="/docs/openapi.json",
    redoc_url=None,
    swagger_ui_parameters={
        "useUnsafeMarkdown": True
    },
    description=docs.description,
)

logger = logging.getLogger(__name__)

dataset = Dataset(settings.dem_source)


@app.get("/", include_in_schema=False)
def get_root():
    return RedirectResponse(url="/docs")


@app.get("/health", include_in_schema=False)
def health():
    return PlainTextResponse("OK")


class ElevationResponse(BaseModel):
    elevation: list[int]


def perform_lookup(lnglats: list[tuple[float, float]]) -> ElevationResponse:
    elevations = dataset.lookup(lnglats)
    return ElevationResponse(elevation=elevations)


example_lng = dict((k, {"value": v}) for k, v in [
    ("Cairn Gorm", -3.643455),
    ("Lake Granby", -105.85858),
])

example_lat = dict([(k, {"value": v}) for k, v in [
    ("Cairn Gorm", 57.116658),
    ("Lake Granby", 40.160080),
]])


@app.get(
    "/api/v1/elevation",
    summary="Lookup elevation for a single coordinate",
    description="Use the POST method if you have more than one coordinate.",
)
def get_elevation(
        lng: Annotated[float, Query(description="Longitude", openapi_examples=example_lng)],
        lat: Annotated[float, Query(description="Latitude", openapi_examples=example_lat)],
) -> ElevationResponse:
    return perform_lookup([(lng, lat)])


class PostElevationRequest(BaseModel):
    coordinates: list[tuple[float, float]]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "coordinates": [
                        [-105.883643, 40.176097],
                        [-105.861114, 40.150743],
                        [-105.822319, 40.141820],
                    ],
                },
            ],
        },
    }


@app.post("/api/v1/elevation", summary="Lookup elevation for multiple coordinates",
          description="Provide a list of coordinates in pairs of longitude, latitude.")
def post_elevation(req: PostElevationRequest) -> ElevationResponse:
    return perform_lookup(req.coordinates)


@app.get("/api/v1/attribution", summary="Get attribution information")
def get_attributions():
    return HTMLResponse(attributions.html)
