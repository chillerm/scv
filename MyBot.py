#!/usr/bin/env python3
# Python 3.6

import logging

import hlt
from hlt import constants
from hlt.positionals import Direction, Position

EXPLORING = "exploring"
HARVESTING = "harvesting"
DEPOSITING = "depositing"
NEED_TILE = "need tile"

game = hlt.Game()

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

game.ready("ChillBotTheStar")

ship_states = {}
previous_positions = {}
ship_targets = {}


def calculate_tile_value(halite_tile: Position, dropoff: Position):
    _inverse_point = dropoff - halite_tile
    distance = abs(_inverse_point.x) + abs(_inverse_point.y)
    return min(1000, game.game_map[halite_tile].halite_amount) * (0.9 ** distance)


tileValues = []
for i in range(0, game.game_map.height):
    current_value = []
    for j in range(0, game.game_map.width):
        current_value.append(calculate_tile_value(Position(i, j), game.me.shipyard.position))
    tileValues.append(current_value)

while True:
    game.update_frame()

    me = game.me
    game_map = game.game_map

    command_queue = []

    direction_order = Direction.get_all_cardinals() + [Direction.Still]


    def _ship_needs_tile(ship):
        "Simply Writing out for clarity."
        if ship.id not in ship_states:
            return True
        if ship_states[ship.id] in [EXPLORING, DEPOSITING] and ship.position == previous_positions[ship.id]:
            return True
        if ship_states[ship.id] == HARVESTING and game_map[ship.position].halite_amount <= 10:
            return True
        else:
            return False


    for ship in me.get_ships():
        if _ship_needs_tile(ship):
            ship_states[ship.id] = NEED_TILE

        if ship_states[ship.id] == NEED_TILE:
            maxVal = 0
            maxPos = 0
            for i in range(0, len(tileValues)):
                for j in range(0, len(tileValues[i])):
                    if tileValues[i][j] > maxVal:
                        maxVal = tileValues[i][j]
                        maxPos = Position(i, j)

            tileValues[maxPos.x][maxPos.y] = 0
            ship_targets[ship.id] = maxPos
            ship_states[ship.id] = EXPLORING

        if ship_states[ship.id] == DEPOSITING:
            move = game_map.naive_navigate(ship, me.shipyard.position)
            command_queue.append(ship.move(move))
            tileValues[ship.position.x][ship.position.y] = calculate_tile_value(ship.position,
                                                                                game.me.shipyard.position)

        elif ship_states[ship.id] == EXPLORING:
            # If it has reached it's destination, start harvesting.
            if ship_targets[ship.id] == ship.position:
                ship_states[ship.id] = HARVESTING

            direction = game_map.naive_navigate(ship, ship_targets[ship.id])
            command_queue.append(ship.move(direction))

            if ship.halite_amount > constants.MAX_HALITE / 2:
                # Set ship to depositing and reset the tile's value to the amount of halite on the tile.
                current_value = calculate_tile_value(ship.position, game.me.shipyard.position)
                tileValues[ship_targets[ship.id].x][ship_targets[ship.id].y] = current_value
                ship_states[ship.id] = DEPOSITING

        # Be sure to keep this at the end of the for ship loop.
        # Track previous position to see if we got stuck.
        previous_positions[ship.id] = ship.position

    # Spawn a ship if our conditions are met.
    if game.turn_number <= 200 and (
            me.halite_amount >= (constants.SHIP_COST * (game.turn_number * 1.25)) or game.turn_number == 0) and not \
            game_map[
                me.shipyard].is_occupied:
        logging.info("Spawning Ship on turn {} with {} halite".format(str(game.turn_number), me.halite_amount))
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
