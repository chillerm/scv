#!/usr/bin/env python3

# Import the Halite SDK, which will let you interact with the game.
import hlt
from hlt import constants

import random
import logging

# This game object contains the initial game state.
game = hlt.Game()
# Respond with your name.
game.ready("MyTempBot")

ship_status = {}

while True:
    # Get the latest game state.
    game.update_frame()
    # You extract player metadata and the updated map metadata here for convenience.
    me = game.me
    game_map = game.game_map

    # A command queue holds all the commands you will run this turn.
    command_queue = []

    for ship in me.get_ships():
        logging.info("Ship {} has {} halite.".format(ship.id, ship.halite_amount))

        if ship.id not in ship_status:
            ship_status[ship.id] = "exploring"

        if ship_status[ship.id] == "returning":
            if ship.position == me.shipyard.position:
                ship_status[ship.id] = "exploring"
            else:
                move = game_map.naive_navigate(ship, me.shipyard.position)
                command_queue.append(ship.move(move))
                continue
        elif ship.halite_amount >= constants.MAX_HALITE / 4:
            ship_status[ship.id] = "returning"

        # For each of your ships, move randomly if the ship is on a low halite location or the ship is full.
        #   Else, collect halite.
        if game_map[ship.position].halite_amount < constants.MAX_HALITE / 10 or ship.is_full:
            cards = ship.position.get_surrounding_cardinals()
            cardinals = ", ".join([str(x) for x in cards])
            logging.info(
                "ship: {ship} at: {at} ::\n\t{cardinals}".format(ship=ship.id, at=ship.position, cardinals=cardinals))
            current_ammount = game_map[ship.position].halite_amount
            move_to = None

            logging.error("Starting Ammount: {}".format(current_ammount))

            for potential_move_position in cards:
                if game_map[potential_move_position].halite_amount > current_ammount:
                    move_to = potential_move_position
                    current_ammount = game_map[potential_move_position].halite_amount

            logging.error("Ending Ammount: {}".format(str(current_ammount)))

            command_queue.append(
                ship.move(random.choice(["n", "s", "e", "w"])))
        else:
            command_queue.append(ship.stay_still())

    # If you're on the first turn and have enough halite, spawn a ship.
    # Don't spawn a ship if you currently have a ship at port, though.
    if me.halite_amount >= (constants.SHIP_COST * 1.5) and not game_map[me.shipyard].is_occupied:
        command_queue.append(game.me.shipyard.spawn())

    # Send your moves back to the game environment, ending this turn.
    game.end_turn(command_queue)
