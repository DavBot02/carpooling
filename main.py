from fastapi import FastAPI
from pydantic import BaseModel

from models.city_grid_model import CityGridModel

app = FastAPI()

model = None


class SimulationStartData(BaseModel):
    num_cars: int
    num_people: int
    block_size: int
    x_blocks: int
    y_blocks: int
    carpooling_capacity: int


def build_response(model: CityGridModel):
    cars = [car.jsonify() for car in model.cars]
    people = [person.jsonify() for person in model.people]
    intersections = [intersection.jsonify()
                     for intersection in model.intersections]

    return {
        "step": model.counter,
        "cars": cars,
        "people": people,
        "intersections": intersections
    }

# ENDPOINTS


@app.get("/")
def read_root():
    return {"hello": "jarocho"}


@app.post("/start")
async def start_simulation(data: SimulationStartData):
    global model

    model = CityGridModel(
        num_cars=data.num_cars,
        num_people=data.num_people,
        block_size=data.block_size,
        x_blocks=data.x_blocks,
        y_blocks=data.y_blocks,
        carpooling_capacity=data.carpooling_capacity
    )

    return build_response(model)


@app.get("/next-step")
def get_next_step():
    global model

    model.step()

    return build_response(model)

