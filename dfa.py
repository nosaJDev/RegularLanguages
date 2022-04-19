
class DFA:
    # This is a representation of a DFA
    
    def __init__(self,alphab):
        
        # The alphabet that is used
        # The alphabet is a list of the different characters that can constitute an input
        self.alphabet = alphab
        
        # States are numbered
        self.num_states = 1
        self.start_state = 0
        self.target_states = set()
        
        # Edges are a dictionary of states, corresponding to a filled dictionary of the alphabet
        # that has the value of the next state
        # If one or more of the dictionaries is not yet filled, the DFA is invalid
        self.edges = {0:{}}
    
    def add_state(self, target = False):
        # Adds a new state to the DFA
        new_state = self.num_states
        self.num_states += 1
        
        # If it's a target, add it to the set
        if target:
            self.target_states.add(new_state)
        
        # Make and edge dictionary addition
        self.edges[new_state] = {}
        
        # Finally return the state
        return new_state
    
    def add_edge(self, ss, se, char):
        # Adds a new edge to the state
        # If it exists, it will replace it
        
        # Check that the states are valid
        if ss >= self.num_states or se >= self.num_states:
            print("Tried to add an edge between non-existent states")
            return
        
        # Check that the character is in the alphabet
        if not char in self.alphabet:
            print("Tried to add an edge with invalid character")
            return
        # If the checks are correct, add the edge
        self.edges[ss][char] = se
        
    def set_state_target(self,state, target):
        # Sets the target status of a state
        
        # Check that it's a vaild state
        if state >= self.num_states:
            print("Tried to alter invalid state")
            return
        
        # Take cases
        if target:
            self.target_states.add(state)
        else:
            self.target_states.discard(state)