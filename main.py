import logging
from typing import Annotated, Optional

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.responses import PlainTextResponse

import attribution
import docs
from attribution import Attribution
from dataset import Dataset


class Settings(BaseSettings):
    merit_dem_fixed1: str

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

dataset = Dataset(merit_dem_fixed1=settings.merit_dem_fixed1)


@app.get("/", include_in_schema=False)
def get_root():
    return RedirectResponse(url="/docs")


@app.get("/health", include_in_schema=False)
def health():
    return PlainTextResponse("OK")


class GetElevationResponse(BaseModel):
    elevation: Optional[float]
    attribution: list[Attribution]


@app.get(
    "/api/v1/elevation",
    summary="Lookup elevation for a single coordinate",
    description="Use the POST method if you have more than one coordinate.",
)
def get_elevation(
        lng: Annotated[float, Query(description="Longitude", openapi_examples={"Lake Granby": {"value": -105.85858}})],
        lat: Annotated[float, Query(description="Latitude", openapi_examples={"Lake Granby": {"value": 40.160080}})],
) -> GetElevationResponse:
    value = dataset.lookup([(lng, lat)])[0]
    attributions = [attribution.value.root["merit"]]
    return GetElevationResponse(elevation=value, attribution=attributions)


class PostElevationRequest(BaseModel):
    coordinates: list[tuple[float, float]]

    # example

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


class PostElevationResponse(BaseModel):
    elevations: list[float]
    attributions: list[Attribution]


@app.post("/api/v1/elevation", summary="Lookup elevation for multiple coordinates",
          description="Provide a list of coordinates in pairs of longitude, latitude.")
def post_elevation(req: PostElevationRequest) -> PostElevationResponse:
    values = dataset.lookup(req.coordinates)
    attributions = [attribution.value.root["merit"]]
    return PostElevationResponse(elevations=values, attributions=attributions)


@app.get("/api/v1/attribution", summary="Get attribution information")
def get_attributions() -> attribution.Attributions:
    return attribution.value
