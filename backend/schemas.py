from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class CreateUser(BaseModel):
    name: str         
    email: str         
    password: str  

class UserLogin(BaseModel):
    email: str         
    password: str 

class PersonalInfo(BaseModel):
    email:str
    name:str
    image_path:str
    height:float
    weight:float
    fights:int
    wins:int
    losses:int
    draws:int

class ExperienceLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class TrainingGoal(str, Enum):
    stamina = "stamina"
    power = "power"
    technique = "technique"
    weight_loss = "weight_loss"
    fight_prep = "fight_prep"

class GoalInfo(BaseModel):
    primary_goals: List[TrainingGoal]
    fight_date: Optional[str] = None

class TrainingTime(str, Enum):
    morning = "morning"
    evening = "evening"

class Availability(BaseModel):
    days_per_week: int = Field(..., ge=1, le=7)
    session_duration: Optional[int] = Field(default=60, ge=15, le=180)
    preferred_time: Optional[TrainingTime] = None

class Equipment(BaseModel):
    has_heavy_bag: Optional[bool] = None
    has_speed_bag: Optional[bool] = None
    has_sparring_partner: Optional[bool] = None
    has_gym: Optional[bool] = None
    has_weights: Optional[bool] = None

class Weakness(str, Enum):
    cardio = "cardio"
    defense = "defense"
    power = "power"
    speed = "speed"
    technique = "technique"

class TrainingContext(BaseModel):
    current_week: int = Field(default=1, ge=1)
    missed_sessions_last_week: int = Field(default=0, ge=0)
    fatigue_level: int = Field(default=5, ge=1, le=10)

class TrainingRequest(BaseModel):
    
    experience: ExperienceLevel
    goal: GoalInfo
    availability: Availability
    equipment: Optional[Equipment] = None
    weakness: Optional[List[Weakness]] = None
    context: Optional[TrainingContext] = None


class PerformanceBase(BaseModel):
    sprint_100m_seconds: Optional[float] = Field(default=None, ge=0)
    sprint_400m_seconds: Optional[float] = Field(default=None, ge=0)
    run_5k_minutes: Optional[float] = Field(default=None, ge=0)
    bench_press_kg: Optional[float] = Field(default=None, ge=0)
    squat_kg: Optional[float] = Field(default=None, ge=0)
    deadlift_kg: Optional[float] = Field(default=None, ge=0)
    pull_ups: Optional[int] = Field(default=None, ge=0)
    push_ups: Optional[int] = Field(default=None, ge=0)
    rounds_completed: Optional[int] = Field(default=None, ge=0)


class PerformanceRequest(PerformanceBase):
    email: str

    
