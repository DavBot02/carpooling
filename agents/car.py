from mesa import Model
from mesa.space import Position
from enum import Enum

from .cell import Cell
from enum import Enum
from .moving_agent import MovingAgent
from common.directions import Directions


class DropOff:
    def __init__(self, agent, position: Position) -> None:
        self.agent = agent
        self.position = position


class Car(MovingAgent):
    class States(Enum):
        Moving = 0
        Stopped = 1
        Unstoppable = 2
        Inactive = 3

    def __init__(self, unique_id: str, model: Model, destination: Position, capacity: int) -> None:
        super().__init__(unique_id, model, destination)
        self.state = Car.States.Stopped
        self.people_on_board = []
        self.direction = None
        self.next_position = self.pos
        self.next_state = None
        self.capacity = capacity

    def check_neighbors(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=False,
            include_center=False
        )
        for neighbor in neighbors:
            if isinstance(neighbor, Car) and neighbor.state != Car.States.Stopped and self.is_in_same_direction(self, neighbor):
                self.next_state = Car.States.Stopped
                return True

            if isinstance(neighbor, Cell) and neighbor.category == Cell.Category.Intersection:
                if neighbor.is_green != self.direction and self.get_direction_to_position(self.pos, neighbor.pos) == self.direction:
                    self.next_state = Car.States.Stopped
                    return True

        return False

    def check_offboard(self):
        for person in self.people_on_board:
            current_distance = self.calculate_distance(
                self.pos, person.destination)
            if current_distance <= person.distance_to_destination:
                person.distance_to_destination = current_distance
                return
            self.offboard(person)

    def can_board(self):
        return len(self.people_on_board) < self.capacity

    def board(self, person):
        self.people_on_board.append(person)
        self.model.eventually_remove(person)

    def offboard(self, person):
        person.next_state = Person.States.Stopped
        drop_off = DropOff(person, self.pos)
        self.people_on_board.remove(person)
        self.model.eventually_place(drop_off)

    def check_same_position(self, position_1, position_2):
        x_1, y_1 = position_1
        x_2, y_2 = position_2

        return x_1 == x_2 and y_1 == y_2

    def step(self):
        self.next_position = self.pos

        self.check_offboard()

        if self.check_neighbors():
            return

        if self.check_same_position(self.pos, self.destination):
            for person in self.people_on_board:
                self.offboard(person)
            self.next_state = Car.States.Inactive
            return

            # A lo mejor no es necesario?
        if self.direction is None or self.state == Car.States.Stopped or self.state == Car.States.Unstoppable:
            neighbors = self.model.grid.get_neighbors(
                self.pos,
                moore=False,
                include_center=False
            )

            closest_pos, closest_distance = None, float("inf")

            for neighbor in neighbors:

                if isinstance(neighbor, Cell):

                    if neighbor.category != Cell.Category.Block:
                        distance = self.calculate_distance(
                            neighbor.pos, self.destination)
                        if distance < closest_distance:
                            closest_pos, closest_distance = neighbor.pos, distance

                    if neighbor.category == Cell.Category.Intersection:
                        closest_pos = neighbor.pos

            if not closest_pos is None:
                self.direction = self.get_direction_to_position(
                    self.pos, closest_pos)
                self.next_state = Car.States.Moving

            self.move()

            return

        if self.state == Car.States.Moving:
            cell_on = self.get_cell_on()

            if not cell_on is None:
                if cell_on.category == Cell.Category.Intersection:
                    self.next_state = Car.States.Unstoppable

                if cell_on.category == Cell.Category.Street:
                    self.move()

    def advance(self):
        self.state = self.next_state
        self.model.grid.move_agent(self, self.next_position)

    def jsonify(self):
        json = super().jsonify()

        json["capacity"] = self.capacity
        # json["people_on_board"] = self.people_on_board

        return json


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
