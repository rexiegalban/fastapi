
from typing import Annotated
from pydantic import Field, BaseModel
import sqlalchemy
from sqlalchemy.orm import Session

from fastapi import Depends, FastAPI, HTTPException, Path, status
import models  # Importing models to ensure they are registered
from models import TodoItem
from database import Base, engine, SessionLocal  # Importing the database engine

app = FastAPI()

models.Base.metadata.create_all(engine)  # Create tables 

#C:\sqlite3

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=250)
    priority: int = Field(default=1, gt=0, lt=6)
    completed: bool = False 


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    items = db.query(TodoItem).all()
    return items

@app.get("/item/{item_id}", status_code=status.HTTP_200_OK)
async def read_item( db: db_dependency,item_id: int = Path(gt=0, title="The ID of the item to get")):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if item is not None:
        return item
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/item", status_code=status.HTTP_201_CREATED)
async def create_item(db: db_dependency, todo_request: TodoRequest):
    todo_model = TodoItem(**todo_request.dict())
    db.add(todo_model)
    db.commit()
    if todo_model.id:
        return todo_model
    raise HTTPException(status_code=400, detail="Item could not be created")

@app.put("/item/{item_id}", status_code=status.HTTP_200_OK)
async def update_item( db: db_dependency,todo_request: TodoRequest, item_id: int = Path(gt=0, title="The ID of the item to update")):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item.title = todo_request.title
    item.description = todo_request.description
    item.priority = todo_request.priority
    item.completed = todo_request.completed
    db.commit()
    return item

@app.delete("/item/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item( db: db_dependency,item_id: int = Path(gt=0, title="The ID of the item to delete")):
    item = db.query(TodoItem).filter(TodoItem.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return item