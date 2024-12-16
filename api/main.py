from fastapi import FastAPI

from routers import (
    auth, users, roles, permissions, countries, organisations
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Donativ APP API",
    description="The Donativ API connects donors and recipients across countries. It allows recipients to create calls for donations with specific needs, while donors can browse or search calls by location, type, or recipient.",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Joel",
        "url": "https://github.com/jkumwenda",
        "email": "jkumwenda@gmail.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

origins = [
    # settings.CLIENT_ORIGIN,
    "https://events.ecsaconm.org",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Auth"], prefix="/auth")
app.include_router(users.router, tags=["Users"], prefix="/users")
app.include_router(roles.router, tags=["Roles"], prefix="/roles")
app.include_router(permissions.router, tags=[
                   "Permissions"], prefix="/permissions")
app.include_router(countries.router, tags=["Countries"], prefix="/countries")
app.include_router(organisations.router, tags=[
                   "Organisations"], prefix="/organisations")
