from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from routers import (
    auth,
    dashboard,
    users,
    roles,
    permissions,
    countries,
    participants,
    events,
    organisers,
    event_types,
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ECSA CONFERENCE APP API",
    description="East, Central and Southern Africa Conference App Programmable Application Interface",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "HashTagIO",
        "url": "https://github.com/jkumwenda",
        "email": "jkumwenda@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

origins = [
    # settings.CLIENT_ORIGIN,
    "https://events.ecsaconm.org",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=origins,
    # allow_credentials=True,
    # allow_methods=["*"],
    # allow_headers=["*"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Auth"], prefix="/auth")
app.include_router(dashboard.router, tags=["Dashboard"], prefix="/dashboard")
app.include_router(users.router, tags=["User"], prefix="/users")
app.include_router(roles.router, tags=["Role"], prefix="/roles")
app.include_router(permissions.router, tags=["Permission"], prefix="/permissions")
app.include_router(countries.router, tags=["Country"], prefix="/countries")
app.include_router(organisers.router, tags=["Organiser"], prefix="/organisers")
app.include_router(event_types.router, tags=["Event Type"], prefix="/event_types")
app.include_router(participants.router, tags=["Participants"], prefix="/participants")
app.include_router(events.router, tags=["Events"], prefix="/events")
