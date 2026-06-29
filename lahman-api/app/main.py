"""FastAPI surface. Thin: models, routes, lifespan. Logic lives in engine.py."""
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

from . import db, engine, lookups


class Sort(str, Enum):
    relevant = "relevant"      # most prominent players first (default)
    irrelevant = "irrelevant"  # most obscure first; also drops the rate-stat floor


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
    sort: Sort = Sort.relevant


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.pool.open()
    yield
    await db.pool.close()


app = FastAPI(
    title="Lahman Immaculate-Grid API",
    version="2.0.0",
    summary="Answers two-condition baseball grid questions from the Lahman database.",
    lifespan=lifespan,
)


@app.get("/health")
async def health():
    return {"ok": await db.ping()}


@app.get("/answer", response_model=AnswerResult)
async def answer(
    question: str = Query(..., examples=["New York Yankees + 300+ HR Career Batting"]),
    limit: int = Query(100, ge=1, le=500),
    sort: Sort = Sort.relevant,
):
    return await engine.answer(question, limit=limit, sort=sort.value)


@app.post("/answers", response_model=list[AnswerResult])
async def answers(req: BatchRequest):
    return [await engine.answer(q, limit=req.limit, sort=req.sort.value) for q in req.questions]


@app.get("/help")
async def help():
    """The supported condition vocabulary, for building/validating questions."""
    return {
        "format": "Two conditions joined by ' + ', e.g. 'Boston Red Sox + Gold Glove'.",
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
