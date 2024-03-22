# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from fastapi_neon import settings
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI, Depends,HTTPException, Query


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, 
        )

def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

# Creating Todo
@app.post("/todos/", response_model=Todo)
def create_todo(todo: Todo, session: Annotated[Session, Depends(get_session)]):
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

# Selecting All Todo's
@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos
    

# Filtering Your Data Based on Content or Id
@app.get("/FilterMyData", response_model=list[Todo])
def filter_data(id: Optional[int] = Query(None), content: Optional[str] = Query(None), session: Session = Depends(get_session)):
    if id is not None:
        statement = select(Todo).where(Todo.id == id)
    elif content is not None:
        statement = select(Todo).where(Todo.content == content)
    else:
        statement = select(Todo)
    
    results = session.exec(statement).all()
    return results


# Deleting The Row From Todo
@app.delete("/deleteTodo", response_model=Todo)
def delete_todo(Id: int, session: Annotated[Session, Depends(get_session)]):

    statement = select(Todo).where(Todo.id == Id)
    todo_to_delete = session.exec(statement).first()
    if not todo_to_delete:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    session.delete(todo_to_delete)
    session.commit()
    
    return todo_to_delete

# Updating the Row.
@app.put("/Updatedata", response_model=Todo)
def update_data(id: int, content: str, session: Session = Depends(get_session)):
    statement = select(Todo).where(Todo.id == id)
    results = session.exec(statement).first()

    if not results:
        raise HTTPException(status_code=404, detail="Todo not found")

    if content:
        results.content = content
    else:
        raise HTTPException(status_code=400, detail="Content cannot be empty")

    session.commit()

    session.refresh(results)
    return results