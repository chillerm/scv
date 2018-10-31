#!/usr/bin/env python3
# Python 3.6

import logging

import hlt
from hlt import constants
from hlt.positionals import Direction, Position

COLLECTING = "collecting"
DEPOSITING = "depositing"
NEED_TILE = "need tile"

game = hlt.Game()

logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))


# Value / Cost of a map tile
tileValues = []
for i in range(0, game.game_map.height):
    # Adds value of current tile from with "width" loop
    current_value = []
    for j in range(0, game.game_map.width):
        distanceToShipyard = game.me.shipyard.position - Position(i, j)
        distance = abs(distanceToShipyard.x) + abs(distanceToShipyard.y)
        # The weighted value of a tile is:
        #    either the max a ship can carry (1000) or the amount of halit in a tile (whichever is less)
        #   MULTIPLED by 0.9^(distance from dropoff) this is the cost of a ship to move (1/10 of it's cargo per move)
        current_value.append((min(1000, game.game_map[Position(i, j)].halite_amount) * (0.9 ** distance)))
    # Adds value of tiles from the "height" loop (which includes all associated horizontal tiles)
    tileValues.append(current_value)


game.ready("ChillBotTheSecond")

ship_states = {}
ship_targets = {}
while True:
    game.update_frame()

    me = game.me
    game_map = game.game_map

    command_queue = []

    direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

    position_choices = []
    for ship in me.get_ships():
        if ship.id not in ship_states:
            ship_states[ship.id] = NEED_TILE

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

            ship_states[ship.id] = COLLECTING

        if ship.halite_amount == 0 and ship_states[ship.id] == DEPOSITING:
            ship_states[ship.id] = NEED_TILE

        if ship_states[ship.id] == DEPOSITING:
            move = game_map.naive_navigate(ship, me.shipyard.position)
            position_choices.append(position_dict[move])
            command_queue.append(ship.move(move))

        elif ship_states[ship.id] == COLLECTING:
            direction = game_map.naive_navigate(ship, ship_targets[ship.id])
            position_choices.append(position_dict[direction])
            command_queue.append(ship.move(direction))

            if ship.halite_amount > constants.MAX_HALITE / 3:
                ship_states[ship.id] = DEPOSITING

                distanceToShipyard = game.me.shipyard.position - ship_targets[ship.id]
                distance = abs(distanceToShipyard.x) + abs(distanceToShipyard.y)
                current_value = (min(1000, game.game_map[ship_targets[ship.id]].halite_amount) * (0.9 ** distance))

                tileValues[ship_targets[ship.id].x][ship_targets[ship.id].y] = current_value

    # Spawn a ship if our conditions are met.
    if game.turn_number <= 200 and me.halite_amount >= (constants.SHIP_COST) and not game_map[
        me.shipyard].is_occupied:
        # if game.turn_number == 1:
        command_queue.append(me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
