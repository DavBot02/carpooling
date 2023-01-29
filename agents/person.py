from mesa import Model
from mesa.space import Position

from enum import Enum
from agents.car import Car
from agents.cell import Cell
from agents.moving_agent import MovingAgent
from common.directions import Directions


class Person(MovingAgent):
    class States(Enum):
        Walking = 0
        Stopped = 1
        Onboard = 2
        Inactive = 3

    def __init__(self, unique_id: str, model: Model, origin: Position, destination: Position) -> None:
        super().__init__(unique_id, model, destination)
        self.state = Person.States.Stopped
        self.direction = Directions.North
        self.next_position = self.pos
        self.next_state = None
        self.distance_to_destination = self.calculate_distance(
            origin, destination)
        self.boarded_car = None

    def get_opposite_direction(self):
        if self.direction == Directions.North:
            return Directions.South
        elif self.direction == Directions.South:
            return Directions.North
        elif self.direction == Directions.West:
            return Directions.East
        elif self.direction == Directions.East:
            return Directions.West
        else:
            raise ValueError("Invalid direction")

    def is_closer_to_destination(self, pos):
        return self.calculate_distance(self.destination, pos) < self.calculate_distance(self.pos, self.destination)

    def check_neighbors(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=False,
            include_center=False
        )
        for neighbor in neighbors:
            if isinstance(neighbor, Cell) and neighbor.category == Cell.Category.Intersection:
                if neighbor.is_green != self.direction and neighbor.is_green != self.get_opposite_direction() and self.get_direction_to_position(self.pos, neighbor.pos) == self.direction:
                    self.next_state = Person.States.Stopped
                    return True

            if isinstance(neighbor, Car):
                if neighbor.can_board() and self.is_closer_to_destination(neighbor.destination):
                    self.boarded_car = neighbor
                    self.next_state = Person.States.Onboard
                    neighbor.board(self)
                    return True
        return False

    def step(self):

        self.next_position = self.pos
        self.next_state = self.state

        if self.state == Person.States.Onboard:
            return

        if self.check_neighbors():
            return

        if self.model.counter % 5 != 0:
            return

        if self.pos == self.destination:
            self.next_state = Person.States.Inactive
            return

        if self.direction is None or self.state == Person.States.Stopped:
            neighbors = self.model.grid.get_neighbors(
                self.pos,
                moore=False,
                include_center=False
            )

            closest_pos, closest_distance = None, float("inf")

            for neighbor in neighbors:
                if isinstance(neighbor, Cell) and neighbor.category != Cell.Category.Block:
                    distance = self.calculate_distance(
                        neighbor.pos, self.destination)

                    if distance < closest_distance:
                        closest_pos, closest_distance = neighbor.pos, distance

            if not closest_pos is None:
                self.direction = self.get_direction_to_position(
                    self.pos, closest_pos)
                self.next_state = Person.States.Walking

            self.move()

            return

        if not self.direction is None and self.state == Person.States.Walking:
            cell_on = self.get_cell_on()

            if not cell_on is None:
                if cell_on.category == Cell.Category.Intersection:
                    self.next_state = Person.States.Stopped

                if cell_on.category == Cell.Category.Street:
                    self.move()

    def advance(self):
        self.state = self.next_state
        if not self.model is None:
            self.model.grid.move_agent(self, self.next_position)

    def jsonify(self):
        json = super().jsonify()

        json["is_onboard"] = self.state == Person.States.Onboard

        return json
