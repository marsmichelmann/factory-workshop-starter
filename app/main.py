from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl

from app.store import Link, LinkStore

app = FastAPI(title="factory-workshop-starter")

_store = LinkStore()


def get_store() -> LinkStore:
    return _store


Store = Annotated[LinkStore, Depends(get_store)]


class LinkIn(BaseModel):
    url: HttpUrl


class LinkOut(BaseModel):
    code: str
    url: str
    created_at: datetime


def _out(link: Link) -> LinkOut:
    return LinkOut(code=link.code, url=link.url, created_at=link.created_at)


@app.post("/links", status_code=201, response_model=LinkOut)
def create_link(body: LinkIn, store: Store) -> LinkOut:
    return _out(store.add(str(body.url)))


@app.get("/links", response_model=list[LinkOut])
def list_links(store: Store) -> list[LinkOut]:
    return [_out(link) for link in store.all()]


@app.get("/{code}")
def follow_link(code: str, store: Store) -> RedirectResponse:
    link = store.get(code)
    if link is None:
        raise HTTPException(status_code=404, detail="unknown code")
    return RedirectResponse(link.url, status_code=307)
