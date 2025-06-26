from sqlalchemy import Boolean, Column, text
from sqlalchemy import Column, Integer, String, ForeignKey, text, Float, Boolean
from sqlalchemy.sql.sqltypes import TIMESTAMP

from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, nullable=False, primary_key=True)
    user_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False, unique=True)
    user_password = Column(String, nullable=False)
    role = Column(String, nullable=False, server_default=text("'user'"))

class TVShow(Base):
    __tablename__ = "tv_shows"

    tv_show_id = Column(Integer, nullable=False, primary_key=True)
    tv_show_name = Column(String, nullable=False, unique=True)
    number_of_seasons = Column(Integer, nullable=False, server_default=text("0"))
    number_of_episodes = Column(Integer, nullable=False, server_default=text("0"))
    tv_show_image_url = Column(String, nullable=False)


class FavoriteTVShows(Base):
    __tablename__ = "favorite_tv_shows"

    favorite_tv_show_id = Column(Integer, nullable=False, primary_key=True)
    tv_show_id = Column(Integer, ForeignKey("tv_shows.tv_show_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))


class Seasons(Base):
    __tablename__ = "seasons"

    season_id = Column(Integer, nullable=False, primary_key=True)
    number_of_episodes = Column(Integer, nullable=False, server_default=text("0"))
    tv_show_id = Column(Integer, ForeignKey("tv_shows.tv_show_id"))
    season_number = Column(Integer, nullable=False)
    season_image_url = Column(String, nullable=True)


class Episodes(Base):
    __tablename__ = "episodes"

    episode_id = Column(Integer, nullable=False, primary_key=True)
    episode_name = Column(String, nullable=False)
    episode_nuber = Column(Integer, nullable=False)
    duration_of_episode = Column(String, nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.season_id"))
    tv_show_id = Column(Integer, ForeignKey("tv_shows.tv_show_id"))
    episode_image_url = Column(String, nullable=True)
    episode_video_url = Column(String, nullable=True)
