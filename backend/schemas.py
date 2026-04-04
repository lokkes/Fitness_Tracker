from pydantic import BaseModel
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
    days_per_week: int
    session_duration: Optional[int] = None
    preferred_time: Optional[TrainingTime] = None

class BoxingSkills(BaseModel):
    weaknesses: Optional[List[str]] = None
    strengths: Optional[List[str]] = None
    style: Optional[str] = None

class HealthInfo(BaseModel):
    injuries: Optional[List[str]] = None


class Equipment(BaseModel):
    has_heavy_bag: Optional[bool] = None
    has_speed_bag: Optional[bool] = None
    has_sparring_partner: Optional[bool] = None
    has_gym: Optional[bool] = None
    has_weights: Optional[bool] = None

class TrainingPlan(BaseModel):
    
    experience: ExperienceLevel

    goal: GoalInfo
    availability: Availability

    skills: Optional[BoxingSkills] = None
    health: Optional[HealthInfo] = None
    equipment: Optional[Equipment] = None

    
