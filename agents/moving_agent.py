from math import sqrt
from mesa import Agent, Model
from mesa.space import Position

from agents.cell import Cell
from common.directions import Directions


class MovingAgent(Agent):
    def __init__(self, unique_id: str, model: Model, destination: Position):
        super().__init__(unique_id, model)
        self.destination = destination

    def is_in_same_direction(self, agent_1: Agent, agent_2: Agent):
        return agent_1.direction == self.get_direction_to_position(agent_1.pos, agent_2.pos)

    def calculate_distance(self, pos1: Position, pos2: Position):
        pos1_x, pos1_y = pos1
        pos2_x, pos2_y = pos2

        diff_y = pos2_y - pos1_y
        diff_x = pos2_x - pos1_x

        return sqrt(pow(diff_y, 2) + pow(diff_x, 2))

    def get_direction_to_position(self, origin: Position, destination: Position) -> Directions:
        x_origin, y_origin = origin
        x_destination, y_destination = destination

        if x_destination < x_origin:
            return Directions.West
        elif x_destination > x_origin:
            return Directions.East
        elif y_destination > y_origin:
            return Directions.North
        elif y_destination < y_origin:
            return Directions.South
        else:
            raise ValueError("Origin and destination are the same position")

    def get_cell_on(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=False,
            include_center=True
        )

        for neighbor in neighbors:
            if isinstance(neighbor, Cell) and neighbor.pos == self.pos:
                return neighbor

        return None
        # Logica del movimiento aqui

    def move(self):
        if self.direction == Directions.North:
            self.next_position = (self.pos[0], self.pos[1] + 1)
        if self.direction == Directions.East:
            self.next_position = (self.pos[0] + 1, self.pos[1])
        if self.direction == Directions.South:
            self.next_position = (self.pos[0], self.pos[1] - 1)
        if self.direction == Directions.West:
            self.next_position = (self.pos[0] - 1, self.pos[1])

    def jsonify(self):
        pos_x, pos_y = 0, 0
        if not self.pos is None:
            pos_x, pos_y = self.pos
        
        json = {
            "unique_id": self.unique_id,
            "destination": {
                "x": self.destination[0],
                "y": self.destination[1],
            },
            "position": {
                "x": pos_x,
                "y": pos_y,
            },
        }

        if self.next_position:
            json["next_position"] = {
                "x": self.next_position[0],
                "y": self.next_position[1]
            }

        return json
