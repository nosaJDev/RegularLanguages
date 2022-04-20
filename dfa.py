
import random
import math

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
    
    def print_info(self):
        # Prints info on the DFA
        print("States:",self.num_states)
        print("Start-state:",self.start_state)
        print("End-states:",self.target_states)
        
        for s in self.edges:
            print(str(s)+": [",end=' ')
            first = True
            for e in self.edges[s]:
                if not first:
                    print(", ",end="")
                print("( "+str(self.edges[s][e])+", '"+e+"')",end="")
                first = False
            print("]")
    
    def get_alphabet(self):
        return self.alphabet
    
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
            
    def check_string(self,string):
        # Checks if a string is accepted in the language
        
        # Start at the beginning
        state_at = self.start_state
        
        # Loop through
        for char in string:
            state_at = self.edges[state_at][char]
        
        # Check if you are at a target state
        return state_at in self.target_states
    
    def find_all_till(self, length):
        # This function will find all the strings till specified length that are accepted by the automaton
        # Careful because it is slow as fuck
        
        # First initiate a dictionary for what goes where
        state_sets = {i:set() for i in range(self.num_states)}
        state_sets[0].add('')
        
        final_set = set()
        
        
        # Loop till desired length
        for i in range(length):
            
            
            for ts in self.target_states:
                final_set.update(state_sets[ts])
            
            state_sets_old = state_sets.copy()
            
            # Loop for every state
            for s in range(self.num_states):
                if len(state_sets[s]) != 0:
                    # Loop for every edge and organise states by characters
                    for char in self.edges[s]:
                        ns = self.edges[s][char]
                        state_sets[ns].update({char+x for x in state_sets_old[s]})
        
        return final_set
    
    def generate(self,num_chars):
        # This is a function that will randomly generate a string that has exactly n characters
        # and is accepted by the automaton
        
        # This will hold info on where this is visited from
        # It holds info in the form of (state_from, char_at)
        state_from = {}
        for i in range(self.num_states):
            state_from[i] = []
            
        state_from[0].append((None,-1,1))
        
        # Set a different dictionary to count how many times each is visited in each time
        visit_times = [[0]*self.num_states]*(num_chars+1)
        visit_times[0][0] = 1
        
        
        for i in range(num_chars):
            from_old = state_from.copy()
            for s in from_old: # For every state that has been visited before
                for e in from_old[s]: # For every visit that came to that state
                    if e[1] == i-1: # If it came at character i-1
                        sv = set()
                        for st in self.edges[s].values(): # Then add this state as a precursor for every state that it will visit
                            state_from[st].append((s,i)) # And set the character cound of that visit to i
                            sv.add(st)
                        for st in sv:
                            visit_times[i+1][st] += visit_times[i][s]
                        break # You break because you don't care how many they have visited it, just that it has i-1 count
        
        # This function will choose a state according to odds
        def choose_probs(viable,odds):

            # Viablity odd sum
            vos = []
            at = 0
            for s in viable:
                at += odds[s]
                vos.append(at)
                
            # Choose between at
            chosen = random.random()*at
            for i in range(len(vos)):
                if chosen <= vos[i]:
                    return viable[i]
            
            
            pass
        
        chars_need = num_chars-1
        state_at = None
        ves =  [ts for ts in self.target_states if chars_need in [x[1] for x in state_from[ts]]] # These are the viable end states
        if len(ves) == 0:
            return None
        else:
            state_at = choose_probs(list(ves),visit_times[chars_need+1])#ves[random.randint(0,len(ves)-1)] # Choose a random viable end state
        string = ""
        
        while chars_need >= 0:
            vps = set(); # These are the viable previous states
            for x in state_from[state_at]:
                if x[1] == chars_need:
                    vps.add(x[0])
            
            # Choose one vps at random
            prev_state = choose_probs(list(vps),visit_times[chars_need+1])#list(vps)[random.randint(0,len(vps)-1)]
            
            # See all the viable characters that lead there
            vc = set()
            for char in self.edges[prev_state]:
                if self.edges[prev_state][char] == state_at:
                    vc.add(char)
            
            # Choose the character to add to the string
            char = list(vc)[random.randint(0,len(vc)-1)]
            
            # Do the step
            string = char+string
            state_at = prev_state
            chars_need -= 1          
        
        return string