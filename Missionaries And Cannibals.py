# ----------------------------------------------------------------------------------------------------------------------
# Missionaries and Cannibals (also knows as Preachers and Demons)
# ----------------------------------------------------------------------------------------------------------------------
# Conditions:
#
# On the West coast of river are located 3 missionaries and 3 Cannibals.
# They have boat to move to opposite coast. Relocate all 6 people to the East coast.
#
# Rules:
#   1.  Boat could contain 1 or 2 persons
#   2.  If any coast has more cannibals than missionaries, cannibals eat missionaries
#   3.  Each of missionaries has to survive
#   4.  Boat can't be moved when it is empty
#
# ----------------------------------------------------------------------------------------------------------------------
# Extended requirements:
#   -   the program should have possibility to work with another number of participants
#       (like 4 missionaries and 4 cannibals, or even unequal amount of each category) and
#       another boat capacity
#   -   for each run, the system should return the number of boat crossing needed if there is a solution
#   -   if there is no solution, the system should return "no solution"
# ----------------------------------------------------------------------------------------------------------------------

# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import combinations

# ----------------------------------------------------------------------------------------------------------------------
# General game data
TOTAL_MISSIONARIES = 3
TOTAL_CANNIBALS = 3
# Maximum characters that could be moved in a single trip
BOAT_MAX_SIZE = 2

# Start conditions
# They are defined as amount of characters in each group on the left coast
# Boat position is defined as: True (1) for left coast, False (0) for right coast
# By default, program thinks that all characters are located on left coast
LEFT_START_MISSIONARIES = TOTAL_MISSIONARIES
LEFT_START_CANNIBALS = TOTAL_CANNIBALS
BOAT_STARTS_LEFT = 1

# Win conditions
# They are described the same manner as Start conditions
# By default, programs thinks that it need to move all characters to the right coast
# But it could be changed by editing following parameters
LEFT_END_MISSIONARIES = 0
LEFT_END_CANNIBALS = 0
BOAT_ENDS_LEFT = 0
# ----------------------------------------------------------------------------------------------------------------------

# Build-in library for combinatorial calculus purpose
from itertools import combinations


# Class to describe coast state. Requires amount of cannibals and missionaries on it
class Coast:
    def __init__(self, missionaries, cannibals):
        self.missionaries = missionaries
        self.cannibals = cannibals

    def __str__(self):
        # Just a function to have readable output
        return '{0} Missionary(ies) and {1} Cannibal(s)'.format(self.missionaries, self.cannibals)

    def alive(self):
        # Function to check if all characters on coast are alive
        # (Missionaries are not eaten)
        return self.missionaries == 0 or self.missionaries >= self.cannibals

    def opposite(self):
        # Calculating content of opposite coast
        # Result is object of class Coast
        return Coast(TOTAL_MISSIONARIES - self.missionaries, TOTAL_CANNIBALS - self.cannibals)

    def list(self):
        # returns array fo comparison purpose
        return [self.missionaries, self.cannibals]

    def possible_moves(self):
        # Function generates all possible combinations of characters, that could be relocated to opposite coast

        # This creates an array of positive ann negative integers
        # Amount of positive integers is equal to number of missionaries
        # Amount of negative integers is equal to number of cannibals
        all_items = [x for x in range(1, 1 + self.missionaries)] + [-x for x in range(1, 1 + self.cannibals)]

        # Array to store all combination af characters to move
        moves = []

        # Since boat could contain from 1 to BOAT_MAX_SIZE
        # We are checking all options of transfers for each amount of characters to transfer
        for boat_size in range(1, BOAT_MAX_SIZE + 1):

            # For each amount of characters we creation all combinations of characters
            for combination in combinations(all_items, boat_size):

                # In each combination amount of positive numbers is amount of missionaries to move
                moved_missionaries = sum([1 for element in combination if element > 0])
                # In each combination amount of negative numbers is amount of cannibals to move
                moved_cannibals = sum([1 for element in combination if element < 0])

                # Check if in movement cannibals will not eat missionaries (in boat)
                if moved_missionaries >= moved_cannibals or moved_missionaries == 0:
                    # Each move is described as array of 2 integers
                    # First integer - amount of missionaries to move
                    # Second integer - amount of cannibals to move
                    move = [moved_missionaries, moved_cannibals]
                    # Check if we didn't
                    if move not in moves:
                        moves.append(move)
        return moves


# class to describe the state of system
class State:
    # Just an internal traceable identifier
    ID = 0

    # State of system is generated using left coast and location of boat as input
    def __init__(self, left_coast, boat_left):
        self.left_coast = left_coast
        # content of right coast is generated automatically as opposite to the left coast
        self.right_coast = self.left_coast.opposite()
        self.boat_left = boat_left
        self.id = State.ID
        State.ID += 1

    def __str__(self):
        # Just a function to have readable output
        return '{id:>3}:\t [{left} \t|| Boat {location:>6} ||\t {right}]'.format(
             id=self.id,
             left=self.left_coast,
             right=self.right_coast,
             location='left' if self.boat_left else 'right'
             )

    def possible_transfers(self):
        # If boat is on left coast we check possible moves from left coast, otherwise - from the right coast
        return self.left_coast.possible_moves() if self.boat_left else self.right_coast.possible_moves()

    def valid(self):
        # Check if system is valid. System is valid if all characters on each coast are alive
        # Returns True if valid, otherwise - False
        return self.left_coast.alive() and self.right_coast.alive()

    def different(self, compared_state):
        # Compare current state with another
        # Returns True if states are different and False otherwise
        return [self.left_coast.list(), self.boat_left] != [compared_state.left_coast.list(), compared_state.boat_left]

    def is_solution(self):
        # Check if our current state is a solution
        return [self.left_coast.list(), self.boat_left] == [[LEFT_END_MISSIONARIES, LEFT_END_CANNIBALS], BOAT_ENDS_LEFT]

    def generate_descendant(self, moving_characters):
        # Generates a descendant
        moving_missionaries = moving_characters[0]
        moving_cannibals = moving_characters[1]

        # Since system State is generated by Left Coast as input,
        # Programs calculates the changes of left coast to feed to constructor of class
        # Variable "direction" is describing if we want to remove characters from left coast
        # or add characters from right coast
        direction = (-1) if self.boat_left else 1
        descendant = State(Coast(self.left_coast.missionaries + direction * moving_missionaries,
                                 self.left_coast.cannibals + direction * moving_cannibals), not self.boat_left)

        # result is a movement
        return Transfer(self, descendant, moving_characters)

    def detailed_str(self):
        # datailed descriprion of system state for printable output
        return '{status} {system} {explanation}'.format(
            status='+' if self.valid() else '-',
            system=self,
            explanation='Missionaries are eaten' if not self.valid() else '')

    def __in__(self, states):
        # Check if current state has analog in array of some states
        for state in states:
            if not self.different(state):
                return state
        return None


# Class to describe the transfers between coasts
class Transfer:
    ID = 0

    def __init__(self, ancestor, descendant, moving_characters):
        # It is described as original state, next state and characters, that has been moved
        # Characters are represented as array of 2 integers
        # First integer - amount of missionaries to move
        # Second integer - amount of cannibals to move
        self.ID = Transfer.ID
        self.ancestor = ancestor
        self.descendant = descendant
        self.moving_missionaries, self.moving_cannibals = moving_characters[0], moving_characters[1]
        Transfer.ID += 1

    def __str__(self):
        # Readable output for printing
        return 'Transfer from # {3:>3} to #{4:>3} : Moving {0} Cannibal(s) and {1} Missionary(ies) to the {2}'.format(
            self.moving_cannibals,
            self.moving_missionaries,
            'left' if self.descendant.boat_left else 'right',
            self.ancestor.id,
            self.descendant.id
        )


# Class to describe the path from final state to initial and contains all paths to gain it
class SolutionTrail:
    def __init__(self, states, transfers):
        self.states = states
        self.transfers = transfers


def main():
    initial_state = State(Coast(LEFT_START_MISSIONARIES, LEFT_START_CANNIBALS), BOAT_STARTS_LEFT)
    print(initial_state.detailed_str())

    # Array to store all possible transfers
    transfers = []
    # Array to store all solved states
    # Theoretically, it shouldn't be array, it should be the only one value. But not all start conditions were checked.
    # Assuming there could be multiple states, that satisfies win conditions
    final_states = []
    # Array to store all visited states (and further comparison with newly generated states
    visited_states = [initial_state]
    # Queue of States to be considered and processed
    queued_states = [initial_state]

    # While we have something to consider
    while len(queued_states) > 0:
        # Take one state from the head of queue
        current_state = queued_states.pop(0)

        if current_state.is_solution():
            final_states.append(current_state)
        # If state is not a solution and all characters are alive
        elif current_state.valid():
            # For each combination of possible moves from this state produce the next state
            for moving_actors in current_state.possible_transfers():
                transfer = current_state.generate_descendant(moving_actors)

                # Check if newly generated state has not been met before (f it is really 'new')
                visited = transfer.descendant.__in__(visited_states)
                if transfer.descendant.__in__(visited_states) is None:
                    # if it is - add it for considering on the next stage, and mak as visited
                    queued_states.append(transfer.descendant)
                    visited_states.append(transfer.descendant)
                    print(transfer)
                    print(transfer.descendant.detailed_str())
                else:
                    # If it was met before - print info and replace it in tranfser by previously met
                    # It will be necessary for building of back path
                    print(transfer)
                    print('*', transfer.descendant, ': VISITED, equal to', visited.id)
                    transfer.descendant = visited
                transfers.append(transfer)

    # If we have any solution
    if len(final_states) > 0:
        # Now we have all states and transfers between states to build the tree of solutions
        print('Total number of unique states\t:\t', len(visited_states))
        print('Total number of transfers\t:\t', len(transfers))

        print('\nSolution(s) exists:\nTotal amount of states that meet win requirements: \t', len(final_states))
        print('\nState(s), that meet win requirements:')

        # Full paths
        full_paths = []
        # Not full paths to consider
        queued_paths = []

        for final_state in final_states:
            queued_paths.append(SolutionTrail([final_state], []))
            print(final_state)

        while len(queued_paths) > 0:
            # pick up first path from queue
            trail = queued_paths[0]
            # if the state in it's head is not an initial state
            if trail.states[0].different(initial_state):
                # Building a list of transfers that lead to creation of this state and
                # simultaneous check if origins of those transvers are not in passed trail
                income_transfers = list(filter(lambda e: e.descendant == trail.states[0] and
                                                         e.ancestor not in trail.states, transfers))
                # If income transfers exist
                if len(income_transfers) > 0:
                    # Update the head of traile
                    trail.states.insert(0, income_transfers[0].ancestor)
                    trail.transfers.insert(0, income_transfers[0])
                    # If multiple inputs occurs - copy and update others
                    if len(income_transfers) > 1:
                        for transfer in income_transfers[1:]:
                            extra_trail = SolutionTrail([transfer.ancestor] + trail.states[1:], [transfer] \
                                                        + trail.transfers[1:])
                            queued_paths.append(extra_trail)
                # If no income transfers - path is gotten into loop
                if len(income_transfers) == 0:
                    # Kick out this trail from paths to consider
                    queued_paths.pop(0)
                    # Next command also works, instead of 'queued_paths.pop(0)', but is significantly slower
                    # queued_paths.remove(trail)

            else:
                queued_paths.pop(0)
                full_paths.append(trail.transfers)

        solution_amount = len(full_paths)
        print('\nTotal number of solutions\t:\t', solution_amount)

        for number, path in enumerate(full_paths):
            print('\n\nSolution #{0} of {1}\t({2} Steps):'.format(number + 1, solution_amount, len(path)))
            print('\tBeginning', path[0].ancestor)
            for i, transfer in enumerate(path):
                print('\t#{0:>3} {1} \t ==> {2}'.format(i + 1, transfer, transfer.descendant))

    else:
        print('Solution is not found')


if __name__ == "__main__":
    main()
