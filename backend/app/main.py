from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, players, teams, leagues, gameweeks

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fantasy Soccer API",
    description="Build your dream squad, compete with friends using real FBRef stats.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(players.router)
app.include_router(teams.router)
app.include_router(leagues.router)
app.include_router(gameweeks.router)


@app.get("/")
def root():
    return {"message": "Fantasy Soccer API — visit /docs for the interactive API explorer"}


@app.get("/health")
def health():
    return {"status": "ok"}
