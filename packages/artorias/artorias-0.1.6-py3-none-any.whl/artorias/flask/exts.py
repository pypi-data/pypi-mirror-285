from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from redis_om import get_redis_connection
from sqlalchemy.orm import DeclarativeBase

from artorias.flask.jwt import JWTManager


class BaseModel(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=BaseModel)
migrate = Migrate(db=db)
cors = CORS()
redis = get_redis_connection()
jwt = JWTManager()
