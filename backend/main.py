"""FastAPI app: extract, match, schemes, applications and reminders.

Run from the project root so the `backend` package imports resolve:
    uvicorn backend.main:app --reload
"""
import os
import secrets
from typing import Optional

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend import engine, extract, store, tracker

app = FastAPI(title="Claim What's Yours")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("ALLOWED_ORIGIN", "http://localhost:5173")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error(status_code, code, message):
    return JSONResponse(
        status_code=status_code,
        content={"error": code, "message": message},
    )


class ExtractBody(BaseModel):
    text: str


class MatchBody(BaseModel):
    profile: dict


class ApplicationCreate(BaseModel):
    scheme_id: str


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
    reminder_date: Optional[str] = None


@app.post("/api/extract")
def extract_route(body: ExtractBody):
    return extract.extract_profile(body.text)


@app.post("/api/match")
def match_route(body: MatchBody):
    schemes = store.load_schemes()
    return {"results": engine.match_all(body.profile, schemes)}


@app.get("/api/schemes")
def list_schemes():
    return store.load_schemes()


@app.get("/api/schemes/{scheme_id}")
def get_scheme(scheme_id: str):
    scheme = store.get_scheme(scheme_id)
    if scheme is None:
        return _error(404, "not_found", "Scheme not found")
    return scheme


@app.put("/api/schemes/{scheme_id}")
def put_scheme(
    scheme_id: str,
    scheme: dict,
    x_admin_key: Optional[str] = Header(default=None),
):
    admin_key = os.environ.get("ADMIN_KEY", "")
    if not admin_key:
        return _error(503, "admin_disabled", "Admin is not enabled")
    if not x_admin_key or not secrets.compare_digest(
        x_admin_key.encode("utf-8"), admin_key.encode("utf-8")
    ):
        return _error(401, "unauthorized", "Invalid admin key")

    schemes = store.load_schemes()
    index = next(
        (i for i, existing in enumerate(schemes) if existing["id"] == scheme_id),
        None,
    )
    if index is None:
        return _error(404, "not_found", "Scheme not found")
    if scheme.get("id") != scheme_id:
        return _error(422, "invalid_scheme", "Scheme id in body must match the URL")

    updated = list(schemes)
    updated[index] = scheme
    try:
        store.save_schemes(updated)
    except ValueError as exc:
        return _error(422, "invalid_scheme", str(exc))
    return scheme


@app.get("/api/applications")
def list_applications():
    return tracker.list_applications()


@app.post("/api/applications", status_code=201)
def create_application(body: ApplicationCreate):
    scheme = store.get_scheme(body.scheme_id)
    if scheme is None:
        return _error(404, "not_found", "Scheme not found")
    steps = scheme.get("apply_steps") or []
    next_action = steps[0] if steps else ""
    return tracker.create_application(body.scheme_id, next_action)


@app.patch("/api/applications/{app_id}")
def update_application(app_id: str, body: ApplicationUpdate):
    try:
        application = tracker.update_application(
            app_id,
            status=body.status,
            notes=body.notes,
            reminder_date=body.reminder_date,
        )
    except ValueError as exc:
        return _error(422, "invalid_status", str(exc))
    if application is None:
        return _error(404, "not_found", "Application not found")
    return application


@app.get("/api/reminders")
def list_reminders():
    return tracker.list_reminders()
