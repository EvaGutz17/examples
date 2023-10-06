from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel
from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str]


class ItemCreate(BaseModel):
    name: str
    description: Optional[str]


class ItemUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]


DATABASE_URL = "sqlite:///test.db"
engine = create_engine(DATABASE_URL, echo=True)

app = FastAPI()


# Dependency to get the database session
def get_session():
    with Session(engine) as session:
        yield session


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)


@app.post("/items")
def create_item(item: Item, db: Session = Depends(get_session)) -> Item:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_session)) -> Item:
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.put("/items/{item_id}")
def update_item(
    item_id: int, item: ItemUpdate, db: Session = Depends(get_session)
) -> Item:
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.model_dump_json():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return Item(**db_item.__dict__)


@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_session)) -> Item:
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return db_item
