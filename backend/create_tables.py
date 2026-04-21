from .db import Base, engine
from .models import UserInfo, UserPerformance, user

Base.metadata.create_all(bind=engine)
print("table created")
