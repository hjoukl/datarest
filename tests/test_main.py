from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from pydantic import BaseModel, Field
from typing import Optional
import pytest
import sys
import csv
import os

from datarest._app import app


#create a test-csv file and safe it in the same directory
def create_test_data():

    file_name = "colors.csv"
    file_path = "/ae/data/work/lb10732/"+file_name

    #if os.path.exists(file_name) == True:
        #print("File already exists")
        #skip the rest

    header = ["no", "color", "description"]
    data = [
        ["1", "red", "The color of blood"],
        ["2", "green", "The color of hope"],
        ["3", "blue", "The color of oceans"],
        ["4", "yellow", "The color of the sun"],
        ["5", "black", "The color of the night"],
        ]

    with open (file_path, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(header)

        writer.writerows(data)

#adding folder src/datarest to the system path
sys.path.insert(0, "/ae/data/work/lb10732/datarest/src/datarest")

class Color(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    no : int
    color: str
    description: str
    


#Use the @pytest.fixture() decorator on top of the function to tell pytest that this is a fixture function (equivalent to a FastAPI dependency).
@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
#This client fixture, in turn, also requires the session fixture.
def client_fixture(session: Session):
    #Define the new function that will be the new dependency override
    #purpose is to use a different session object just for the tests
    def get_session_override():
        return session 

    #So, here we are telling the FastAPI app to use get_session_override instead of get_session in all the places in the code that depend on get_session
    #app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client #after the test function is done, pytest will come back to execute the rest of the code after yield
    #app.dependency_overrides.clear()

def test_get_all_colors(session: Session, client: TestClient):
    #create some test data in order to test the function
    color_1 = Color(no = 1, color = "Blue", description = "Blue as the ocean")
    session.add(color_1)
    session.commit()

    response = client.get(f"/colors/{color_1.id}")
    data = response.json()

    assert response.status_code == 200

    assert data["no"] == color_1.no
    assert data["color "] == color_1.color
    assert data["description"] == color_1.description
    assert data["id"] == color_1.id


#if __name__=="__main__":
    #print("Successful")
