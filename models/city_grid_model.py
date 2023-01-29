from mesa import Model
from mesa.time import SimultaneousActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from random import choice
from typing import Tuple

import numpy as np

from agents.car import Car
from agents.cell import Cell
from agents.person import Person


def get_status_grid(model):
    result = np.zeros((model.grid.height, model.grid.width))
    for (content, x, y) in model.grid.coord_iter():
        for obj in content:
            if isinstance(obj, Car):
                result[y][x] = 0
            elif isinstance(obj, Person):
                result[y][x] = 255
            elif isinstance(obj, Cell) and obj.category == obj.Category.Block:
                result[y][x] = 50
            elif isinstance(obj, Cell) and obj.category == obj.Category.Street:
                result[y][x] = 100
            elif isinstance(obj, Cell) and obj.category == obj.Category.Intersection:
                result[y][x] = 150
    return result


class CityGridModel(Model):
    def __init__(self, block_size, x_blocks, y_blocks, num_people, num_cars, carpooling_capacity, **kwargs) -> None:
        self.num_people = num_people
        self.num_cars = num_cars
        self.kwargs = kwargs

        self.counter = 0

        self.street_positions = []

        self.grid = MultiGrid(x_blocks * (block_size + 1) + 1,
                              y_blocks * (block_size + 1) + 1, False)
        self.schedule = SimultaneousActivation(self)

        self.people = []
        self.cars = []
        self.intersections = []
        self.intersection_positions = []

        self.setup_grid(block_size)
        self.setup_cars(carpooling_capacity)
        self.setup_people()
        self.datacollector = DataCollector(
            model_reporters={"Grid": get_status_grid}
        )

        self.agents_to_place = []
        self.agents_to_remove = []

    def setup_grid(self, block_size):
        for (content, x, y) in self.grid.coord_iter():
            id = f"Cell-{x},{y}"
            position = (x, y)

            if x % (block_size + 1) == 0 and y % (block_size + 1) == 0:
                new_cell = Cell(id, self, Cell.Category.Intersection)
                self.intersection_positions.append(position)
            elif x % (block_size + 1) == 0 or y % (block_size + 1) == 0:
                new_cell = Cell(id, self, Cell.Category.Street)
                self.street_positions.append(position)
            else:
                new_cell = Cell(id, self, Cell.Category.Block)

            self.schedule.add(new_cell)
            self.grid.place_agent(new_cell, position)

    def setup_cars(self, carpooling_capacity):
        for i in range(self.num_cars):
            origin = self.get_random_street_position()
            destination = self.get_random_street_position()

            new_car = Car(f"Car-{i+1}", self, destination, carpooling_capacity)

            self.schedule.add(new_car)
            self.grid.place_agent(new_car, origin)
            self.cars.append(new_car)

    def setup_people(self):
        for i in range(self.num_people):
            origin = self.get_random_street_position()
            destination = self.get_random_street_position()

            new_person = Person(f"Person-{i+1}", self, origin, destination)

            self.schedule.add(new_person)
            self.grid.place_agent(new_person, origin)
            self.people.append(new_person)

    def get_random_street_position(self) -> Tuple[int, int]:
        return choice(self.street_positions)

    def eventually_remove(self, agent):
        self.agents_to_remove.append(agent)

    def eventually_place(self, agent):
        self.agents_to_place.append(agent)

    def step(self):
        self.counter += 1
        self.datacollector.collect(self)
        self.schedule.step()

        if len(self.agents_to_remove):
            for agent in self.agents_to_remove:
                self.schedule.remove(agent)
                self.grid.remove_agent(agent)
                self.agents_to_remove.remove(agent)

        if len(self.agents_to_place):
            for drop_off in self.agents_to_place:
                self.schedule.add(drop_off.agent)
                self.grid.place_agent(drop_off.agent, drop_off.position)
                self.agents_to_place.remove(drop_off)
