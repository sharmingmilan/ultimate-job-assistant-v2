"""GET/PUT /api/config — read or change the persisted project root."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from uja_host import config as host_config

router = APIRouter(prefix="/api/config", tags=["config"])


class ConfigResponse(BaseModel):
    project_root: str | None = None
    schema_version: int


class SetProjectRootRequest(BaseModel):
    project_root: str = Field(..., min_length=1)


@router.get("", response_model=ConfigResponse)
def get_config() -> ConfigResponse:
    cfg = host_config.load_config()
    return ConfigResponse(project_root=cfg.project_root, schema_version=cfg.schema_version)


@router.put("/project-root", response_model=ConfigResponse)
def put_project_root(body: SetProjectRootRequest) -> ConfigResponse:
    try:
        cfg = host_config.set_project_root(body.project_root)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return ConfigResponse(project_root=cfg.project_root, schema_version=cfg.schema_version)
