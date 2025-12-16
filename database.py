from sqlalchemy import create_engine, Column, Integer, String, PickleType
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.mutable import MutableList

# Database setup
DATABASE_URL = "sqlite:///somerpg.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PlayerState(Base):
    __tablename__ = 'player_state'
    id = Column(Integer, primary_key=True, index=True, default=1)
    name = Column(String)
    location_id = Column(String)
    health = Column(Integer)
    max_health = Column(Integer)
    stamina = Column(Integer)
    max_stamina = Column(Integer)
    mana = Column(Integer, default=50)
    max_mana = Column(Integer, default=50)
    gold = Column(Integer)
    attack = Column(Integer, default=1)
    defense = Column(Integer, default=0)
    experience = Column(Integer)
    level = Column(Integer)
    skill_points = Column(Integer, default=0)
    inventory = Column(MutableList.as_mutable(PickleType), default=[])
    equipment = Column(MutableList.as_mutable(PickleType), default={})
    skills = Column(MutableList.as_mutable(PickleType), default=[])
    active_quests = Column(MutableList.as_mutable(PickleType), default=[])
    completed_quests = Column(MutableList.as_mutable(PickleType), default=[])
    visited_locations = Column(MutableList.as_mutable(PickleType), default=set())

class WorldState(Base):
    __tablename__ = 'world_state'
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(String, unique=True)
    looted_treasures = Column(MutableList.as_mutable(PickleType), default=[])

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_db_and_tables()
    print("Database and tables created.")