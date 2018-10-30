#!/usr/bin/env python3
# Python 3.6

import logging

import hlt
from hlt import constants
from hlt.positionals import Direction

COLLECTING = "collecting"
DEPOSITING = "depositing"

game = hlt.Game()

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

game.ready("MyPythonBot")

ship_states = {}
while True:
    game.update_frame()

    me = game.me
    game_map = game.game_map

    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

    position_choices = []
    for ship in me.get_ships():
        if ship.id not in ship_states:
            ship_states[ship.id] = COLLECTING

        position_options = ship.position.get_surrounding_cardinals() + [ship.position]

        # {Direction: Position}
        # {(0,1): (19.38)}
        position_dict = {}

        # {Direction: Halite}
        # {(0,1): 500}
        halite_dict = {}

        for n, direction in enumerate(direction_order):
            position_dict[direction] = position_options[n]

        for direction in position_dict:
            position = position_dict[direction]
            halite_amount = game_map[position].halite_amount

            if position_dict[direction] not in position_choices:
                halite_dict[direction] = halite_amount
            else:
                logging.info("Attempting to move to same spot another ship\n")

        if ship.halite_amount == 0 and ship_states[ship.id] == DEPOSITING:
            ship_states[ship.id] = COLLECTING

        if ship_states[ship.id] == DEPOSITING:
            move = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(position_dict[move])
            command_queue.append(ship.move(move))

        elif ship_states[ship.id] == COLLECTING:
            directional_choice = max(halite_dict, key=halite_dict.get)
            position_choices.append(position_dict[directional_choice])
            command_queue.append(ship.move(game_map.naive_navigate(ship, position_dict[directional_choice])))

            if ship.halite_amount > constants.MAX_HALITE / 3:
                ship_states[ship.id] = DEPOSITING

    if game.turn_number <= 200 and me.halite_amount >= (constants.SHIP_COST) and not game_map[
        me.shipyard].is_occupied:
        # if game.turn_number == 1:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)

# def test_position_change():
#     current_position = Position(100, 100)
#     target_position = Position(0, 0)
#
#     logging.info("Getting from {} to {}.".format(current_position, current_position))
#
#     while current_position != target_position:
#         def get_move(current_position, target_position):
#             if current_position.x > target_position.x:
#                 return Position(-1, 0)
#             elif current_position.x < target_position.x:
#                 return Position(1, 0)
#             elif current_position.y > target_position.y:
#                 return Position(0, -1)
#             elif current_position.y < target_position.y:
#                 return Position(0, 1)
#             else:
#                 return Position(0, 0)
#
#         move = get_move()
#         logging.info("Moving {} from {}".format(current_position, move))
#         current_position = current_position + move
#
#
