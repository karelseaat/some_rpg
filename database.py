from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, PickleType
from sqlalchemy.ext.mutable import MutableList, MutableDict, MutableSet

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///somerpg.db"
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
Base = declarative_base()

class PlayerState(Base):
    __tablename__ = 'player_state'
    name = Column(String, primary_key=True, index=True)
    password_hash = Column(String)
    location_id = Column(String)
    health = Column(Integer)
    max_health = Column(Integer)
    stamina = Column(Integer)
    max_stamina = Column(Integer)
    mana = Column(Integer, default=50)
    max_mana = Column(Integer, default=50)
    gold = Column(Integer)
    strength = Column(Integer, default=5)
    dexterity = Column(Integer, default=5)
    intelligence = Column(Integer, default=5)
    attack = Column(Integer, default=1)
    defense = Column(Integer, default=0)
    experience = Column(Integer)
    level = Column(Integer)
    skill_points = Column(Integer, default=0)
    attribute_points = Column(Integer, default=0)
    inventory = Column(MutableList.as_mutable(PickleType), default=[])
    equipment = Column(MutableDict.as_mutable(PickleType), default={})
    skills = Column(MutableList.as_mutable(PickleType), default=[])
    active_quests = Column(MutableList.as_mutable(PickleType), default=[])
    completed_quests = Column(MutableList.as_mutable(PickleType), default=[])
    visited_locations = Column(MutableSet.as_mutable(PickleType), default=set())


class WorldState(Base):
    __tablename__ = 'world_state'
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, unique=True)
    looted_treasures = Column(MutableList.as_mutable(PickleType), default=[])
    ground_items = Column(MutableList.as_mutable(PickleType), default=[])

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_db_and_tables())
    print("Database and tables created.")
