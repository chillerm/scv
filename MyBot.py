#!/usr/bin/env python3
# Python 3.6

# Import the Halite SDK, which will let you interact with the game.
import hlt

# This library contains constant values.
from hlt import constants

# This library contains direction metadata to better interface with the game.
from hlt.positionals import Direction, Position

# This library allows you to generate random numbers.
import random

# Logging allows you to save messages for yourself. This is required because the regular STDOUT
#   (print statements) are reserved for the engine-bot communication.
import logging

""" <<<Game Begin>>> """

# This game object contains the initial game state.
game = hlt.Game()

# Now that your bot is initialized, save a message to yourself in the log file with some important information.
#   Here, you log here your id, which you can always fetch from the game object by using my_id.
logging.info("Successfully created bot! My Player ID is {}.".format(game.my_id))

""" <<<Game Loop>>> """


def run():
    drop_off_locations = []
    # At this point "game" variable is populated with initial map data.
    # This is a good place to do computationally expensive start-up pre-processing.
    # As soon as you call "ready" function below, the 2 second per turn timer will start.
    game.ready("MyPythonBot")
    returning_ships = {}
    while True:
        # This loop handles each turn of the game. The game object changes every turn, and you refresh that state by
        #   running update_frame().
        game.update_frame()
        # You extract player metadata and the updated map metadata here for convenience.
        me = game.me
        game_map = game.game_map

        # A command queue holds all the commands you will run this turn. You build this list up and submit it at the
        #   end of the turn.
        command_queue = []

        direction_order = [Direction.North, Direction.South, Direction.East, Direction.West, Direction.Still]

        position_choices = []
        for ship in me.get_ships():
            if ship.halite_amount == 0 and ship.id in returning_ships.keys():
                returning_ships.pop(ship.id)

            if game.turn_number == 2:
                drop_off_locations.append(ship.position)
                logging.info("Drop off locations: {}".format(drop_off_locations))
            logging.info("Turn Number: {}".format(game.turn_number))
            logging.info("Drop off locations: {}".format(drop_off_locations))

            position_options = ship.position.get_surrounding_cardinals() + [ship.position]

            logging.info("position_options: {}".format(position_options))

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

                # If we have a ship moving to this position, do not add it as an eligible position.
                if position_dict[direction] not in position_choices:
                    halite_dict[direction] = halite_amount
                else:
                    logging.info("Attempting to move to same spot another ship\n")

            if game.turn_number == 15:
                logging.info(position_options)

            directional_choice = max(halite_dict, key=halite_dict.get)

            logging.info("directional_choice: {}".format(directional_choice))
            logging.info("Halite in directional_choice: {}".format(directional_choice[1]))

            if ship.is_full or (ship.id in returning_ships.keys()):
                logging.info("I'm full!!!!")
                navigate_to = me.shipyard.position
                logging.info("Navigating to: {}".format(navigate_to))

                move = game_map.naive_navigate(ship, navigate_to)
                move_to = Position(ship.position.x + move[0], ship.position.y + move[1])
                logging.info("move: {}".format(move))
                logging.info("move_to: {}".format(move_to))

                position_choices.append(move_to)
                command_queue.append(
                    ship.move(move)
                )
                returning_ships[ship.id] = ship

            elif (game_map[ship.position].halite_amount < halite_dict[directional_choice] or ship.position == me.shipyard.position) and position_dict[directional_choice] not in position_choices:
                position_choices.append(position_dict[directional_choice])

                command_queue.append(
                    ship.move(directional_choice)
                )
            else:
                position_choices.append(ship.position)
                command_queue.append(
                    ship.stay_still()
                )

        # If the game is in the first 200 turns and you have enough halite, spawn a ship.
        # Don't spawn a ship if you currently have a ship at port, though - the ships will collide.
        if game.turn_number <= 200 and me.halite_amount >= (constants.SHIP_COST) and not game_map[
            me.shipyard].is_occupied:
            # if game.turn_number == 1:
            command_queue.append(me.shipyard.spawn())

        # Send your moves back to the game environment, ending this turn.
        game.end_turn(command_queue)


def test_position_change():
    current_position = Position(100, 100)
    target_position = Position(0, 0)

    logging.info("Getting from {} to {}.".format(current_position, current_position))

    while current_position != target_position:
        def get_move(current_position, target_position):
            if current_position.x > target_position.x:
                return Position(-1, 0)
            elif current_position.x < target_position.x:
                return Position(1, 0)
            elif current_position.y > target_position.y:
                return Position(0, -1)
            elif current_position.y < target_position.y:
                return Position(0, 1)
            else:
                return Position(0, 0)

        move = get_move()
        logging.info("Moving {} from {}".format(current_position, move))
        current_position = current_position + move


run()
