import pytest
import requests

from automation_framework.utilities.api_helpers import ApiHelper
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import session
from automation_framework.utilities.db_helpers import DatabaseHelper

Base = declarative_base()


class Weather(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    city = Column(String)
    temperature = Column(Float)
    feels_like = Column(Float)

    engine = create_engine('sqlite:///weather.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

@pytest.fixture(scope="module")
def api():
    return ApiHelper()

@pytest.fixture(scope="module")
def db():
    return DatabaseHelper()
@pytest.fixture(scope='module')
def db_session():
    db_uri = 'sqlite:///weather.db'
    return init_db(db_uri)

def init_db(db_uri):
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


@pytest.mark.parametrize("city_name", ["London", "Paris", "Berlin"])
def test_get_current_weather(city_name, api, db_session):
    # Make a request to the API
    params = {
        'q': api.city_name,
        'appid': api.API_KEY,
        'units': 'metric',
        'lang': 'en'
    }
    response = requests.get(api.BASE_URL, params=params)
    data = response.json()

    # Validate status code
    assert response.status_code == 200, f"Failed to get weather data for {city_name}"

    data = response.json()
    temperature = data['main']['temp']
    feels_like = data['main']['feels_like']

    # Insert data into the database
    weather_data = Weather(city=city_name, temperature=temperature, feels_like=feels_like)
    db_session.add(weather_data)
    db_session.commit()

    # Query the database for the weather data

    #db_data = session.query(Weather).filter_by(city=city).first()

    # Verify that the temperature and feels_like values from the database match the API response
    if weather_data.temperature == temperature and weather_data.feels_like == feels_like:
        print("Data from the database matches the API response")
    else:
        print("Data from the database does not match the API response")

    # Close the session
    #  session.close()

