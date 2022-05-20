from copy import deepcopy


class Node:
    '''Node data structure for search space bookkeeping.'''
    
    def __init__(self, state, parent, action, path_cost):
        '''Constructor for the node state with the required parameters.'''
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost

    @classmethod
    def root(cls, init_state):
        '''Factory method to create the root node.'''
        return cls(init_state, None, None, 0)

    @classmethod
    def child(cls, problem, parent, action):
        '''Factory method to create a child node.'''
        return cls(
            problem.result(deepcopy(parent.state), action),
            parent,
            action,
            parent.path_cost + problem.step_cost(deepcopy(parent.state), action))

def solution(node):
    '''A method to extract the sequence of actions representing the solution from the goal node.'''
    actions = []
    cost = node.path_cost
    while node.parent is not None:
        actions.append(node.action)
        node = node.parent
    actions.reverse()
    return actions, cost


class Problem:
    '''
    Abstract base class for problem formulation.
    It declares the expected methods to be used by a search algorithm.
    All the methods declared are just placeholders that throw errors if not overriden by child "concrete" classes!
    '''
    
    def __init__(self):
        '''Constructor that initializes the problem. Typically used to setup the initial state and, if applicable, the goal state.'''
        self.init_state = None
    
    def actions(self, state):
        '''Returns an iterable with the applicable actions to the given state.'''
        raise NotImplementedError
    
    def result(self, state, action):
        '''
        This function represents the transition model.
        It returns the resulting state from applying the given action to the given state.
        '''
        raise NotImplementedError
    
    def goal_test(self, state):
        '''Returns whether or not the given state is a goal state.'''
        raise NotImplementedError
    
    def step_cost(self, state, action):
        '''Returns the step cost of applying the given action to the given state.'''
        raise NotImplementedError


class Game:
    '''
    Abstract game class for game formulation.
    It declares the expected methods to be used by an adversarial search algorithm.
    All the methods declared are just placeholders that throw errors if not overriden by child "concrete" classes!
    '''
    
    def __init__(self):
        '''Constructor that initializes the game. Typically used to setup the initial state, number of players and, if applicable, the terminal states and their utilities.'''
        self.init_state = None
    
    def player(self, state):
        '''Returns the player whose turn it is.'''
        raise NotImplementedError
    
    def actions(self, state):
        '''Returns an iterable with the applicable actions to the given state.'''
        raise NotImplementedError
    
    def result(self, state, action):
        '''Returns the resulting state from applying the given action to the given state.'''
        raise NotImplementedError
    
    def terminal_test(self, state):
        '''Returns whether or not the given state is a terminal state.'''
        raise NotImplementedError
    
    def utility(self, state, player):
        '''Returns the utility of the given state for the given player, if possible (usually, it has to be a terminal state).'''
        raise NotImplementedError

class StochasticGame(Game):
    '''
    Abstract cass for stochastic games which inherits from game base class.
    It adds the necessary functions to implement stochastic games.
    '''
    def chances(self, state):
        '''Return a list of all possible uncertain events at a state.'''
        raise NotImplementedError

    def outcome(self, state, chance):
        '''Return the state which is the outcome of a chance trial.'''
        raise NotImplementedError

    def probability(self, chance):
        '''Return the probability of occurrence of a chance.'''
        raise NotImplementedError