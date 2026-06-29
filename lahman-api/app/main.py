"""FastAPI surface. Thin: models, routes, lifespan. Logic lives in engine.py."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from . import db, engine, lookups


class Player(BaseModel):
    rank: int
    name: str
    position: str | None = None
    career: str | None = None
    bbref_id: str | None = None


class AnswerResult(BaseModel):
    question: str
    category: str
    count: int
    players: list[Player]


class BatchRequest(BaseModel):
    questions: list[str] = Field(..., min_length=1)
    limit: int = Field(100, ge=1, le=500)
    obscure: bool = Field(False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.pool.open()
    yield
    await db.pool.close()


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Lahman Immaculate-Grid API",
    version="2.0.0",
    summary="Answers two-condition baseball grid questions from the Lahman database.",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/up")
async def up():
    return {"status": "ok"}


@app.get("/health")
async def health():
    return {"ok": await db.ping()}


@app.get("/answer", response_model=AnswerResult)
@limiter.limit("30/minute")
async def answer(
    request: Request,
    question: str = Query(..., examples=["Washington Nationals + 300+ HR Career Batting"]),
    limit: int = Query(100, ge=1, le=500),
    obscure: bool = Query(False, description="True = most obscure players first"),
):
    return await engine.answer(question, limit=limit, obscure=obscure)


@app.post("/answers", response_model=list[AnswerResult])
@limiter.limit("10/minute")
async def answers(request: Request, req: BatchRequest):
    return [await engine.answer(q, limit=req.limit, obscure=req.obscure) for q in req.questions]


@app.get("/help")
async def help():
    """The supported condition vocabulary, for building/validating questions."""
    return {
        "format": "Two conditions joined by ' + ', e.g. 'Washington Nationals + Gold Glove'.",
        "teams": sorted(lookups.KNOWN_TEAM_NAMES),
        "awards": sorted(lookups.KNOWN_AWARD_NAMES),
        "player_flags": sorted(lookups.PLAYER_LOOKUP),
        "positions": {
            "format": "Played <Position> min. 1 game",
            "values": sorted(set(lookups.POSITION_LOOKUP) - {"P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "OF", "DH"}),
            "abbreviations": sorted({"P", "C", "1B", "2B", "3B", "SS", "LF", "CF", "RF", "OF", "DH"}),
            "special": ["Pitched min. 1 game", "Designated Hitter min. 1 game"],
        },
        "stats": {
            "counting": "e.g. '300+ HR Career Batting', '100+ RBI Season Batting', "
                        "'200+ K Season Pitching', '20+ Win Season Pitching'",
            "rate": "e.g. '.300+ AVG Season Batting', '≤ 3.00 ERA Season'",
            "compound": "e.g. '30+ HR / 30+ SB Season Batting'",
            "supported_tokens": sorted(lookups.STAT_LOOKUP),
        },
    }
