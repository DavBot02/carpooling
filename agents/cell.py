from enum import Enum
from mesa import Agent, Model

from common.directions import Directions


class Cell(Agent):
    class Category(Enum):
        Block = "BLOCK"
        Intersection = "INTERSECTION"
        Street = "STREET"

    def __init__(self, unique_id: int, model: Model, category: Category) -> None:
        super().__init__(unique_id, model)
        self.category = category
        self.steps_elapsed = 0

        self.traffic_directions = [direction for direction in Directions]
        self.index = 0
        self.is_green = self.traffic_directions[self.index]
        self.next_is_green = None

    def step(self):
        self.next_is_green = self.is_green

        if self.category == Cell.Category.Intersection:
            if self.steps_elapsed % 10 == 0:
                self.index += 1
                self.next_is_green = self.traffic_directions[self.index % 4]

        self.steps_elapsed += 1

    def advance(self):
        self.is_green = self.next_is_green

    def jsonify(self):
        return {
                "unique_id": self.unique_id,
                "position": {
                    "x": self.pos[0],
                    "y": self.pos[1]
                    },
                }
