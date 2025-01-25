from typing import Annotated

import uvicorn
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = FastAPI()

engine = create_async_engine("sqlite+aiosqlite:///cookingbook.db")

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class CookingModel(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    ingredients: Mapped[str]
    directions: Mapped[str]


@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    return {"ok": True}


class RecipeAddSchema(BaseModel):
    title: str
    ingredients: str
    directions: str


class RecipeSchema(RecipeAddSchema):
    id: int


@app.post("/recipes", tags=["Recipes"], summary="Add new recipe")
async def add_recipe(data: RecipeAddSchema, session: SessionDep):
    new_recipe = CookingModel(
        title=data.title,
        ingredients=data.ingredients,
        directions=data.directions,
    )
    session.add(new_recipe)
    await session.commit()
    return {"ok": True}


@app.get("/recipes", tags=["Recipes"], summary="Get all recipes")
async def get_recipes(session: SessionDep):
    query = select(CookingModel)
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/recipes/{recipe_id}", tags=["Recipes"], summary="Get recipe by id")
async def get_recipe(recipe_id: int, session: SessionDep):
    req_recipe = await session.get(CookingModel, recipe_id)
    return req_recipe


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
