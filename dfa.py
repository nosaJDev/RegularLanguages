
import random
import math
from nfa import NFA, kleene_NFA, base_NFA, concat_NFA

class DFA:
    # This is a representation of a DFA
    
    def __init__(self,alphab):
        
        # The alphabet that is used
        # The alphabet is a list of the different characters that can constitute an input
        self.alphabet = list(alphab)
        self.alphabet.sort()
        
        # States are numbered
        self.num_states = 1
        self.start_state = 0
        self.target_states = set()

        # These are extra calculations that should be done once after every change
        # So we include some booleans so that the calcuation is not repeated again by mistake
        self.computed_dead_states = False
        self.computed_target_distance = False
        self.dead_states = set() # These are found separately
        self.target_distance = {} # The minimum distance each state has from a target state
        self.target_max_length = float('inf') # The maximum distance the furthest state has from a target state
        
        # Edges are a dictionary of states, corresponding to a filled dictionary of the alphabet
        # that has the value of the next state
        # If one or more of the dictionaries is not yet filled, the DFA is invalid
        self.num_edges = 0 # Take note of number of edges to know if you are complete
        self.edges = {0:{}}
        
        # Extra variables to calculate the next string on set
        self.next_len = 0
        self.next_in = 0
        self.depth_list = []
        self.backtracked = False
        self.ab_next = { self.alphabet[i]:self.alphabet[i+1] for i in range(len(self.alphabet)-1)}
    
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

        # Reset the computations
        self.computed_dead_states = False
        self.computed_target_distance = False

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
        
        # Reset the computations
        self.computed_dead_states = False
        self.computed_target_distance = False

        # Check that the states are valid
        if ss >= self.num_states or se >= self.num_states:
            print("Tried to add an edge between non-existent states")
            return
        
        # Check that the character is in the alphabet
        if not char in self.alphabet:
            print("Tried to add an edge with invalid character")
            return
        
        # Check if it's a new edge
        if char not in self.edges[ss]:
            self.num_edges += 1

        # If the checks are correct, add the edge
        self.edges[ss][char] = se
    
    def find_state(self,state_from, char):
        st = self.edges[state_from][char]
        return (st,st in self.target_states)

    def set_state_target(self,state, target):
        # Sets the target status of a state
        
        # Reset the computations
        self.computed_dead_states = False
        self.computed_target_distance = False

        # Check that it's a vaild state
        if state >= self.num_states:
            print("Tried to alter invalid state")
            return
        
        # Take cases
        if target:
            self.target_states.add(state)
        else:
            self.target_states.discard(state)
    
    def is_complete(self):
        # Returns whether the dfa has all the edges it needs to be complete
        return self.num_edges == self.num_states*len(self.alphabet)

    def make_complete(self):
        # This will check if the dfa is complete, and if it isn't it will create or
        # find a new dead state to place all the pending edges so that it will be complete

        # Check incomplete
        if self.is_complete():
            return

        # Find a dead state
        if self.computed_dead_states == False:
            self.compute_dead_states()

        # Check if there are dead states
        dead_state = -1
        if len(self.dead_states) != 0:
            dead_state = list(self.dead_states)[0]
        else:
            dead_state = self.add_state()

        # Now that you have the dead state, add edges leading to it for all other incomplete states
        for i in range(self.num_states):
            for char in self.alphabet:
                if char not in self.edges[i]:
                    self.edges[i][char] = dead_state

    def negate(self):
        # Makes all the target states non-target, and all the non-target states target
        # Basically negates the dfa
        for i in range(self.num_states):
            self.set_state_target(i,i not in self.target_states)

    def compute_dead_states(self):
        # This is run once and it speeds up other procedures
        
        # Check if you have done this before
        if self.computed_dead_states:
            return

        def check_state_dead(state):
            # This checks if a single state is dead
            visited = set()
            pending = [state]
            
            # Start from this state and do a breath-first till you find a target state
            while True:
                
                if len(pending) == 0:
                    break
                
                # Get the next state
                state_at = pending.pop()
                
                # Check that it is not yet visited
                if state_at in visited:
                    continue
                visited.add(state_at)
                
                if state_at in self.target_states:
                    return False

                # Add the other states
                for char in self.edges[state_at]:
                    pending.append(self.edges[state_at][char])
            
            return True
        
        for i in range(self.num_states):
            if check_state_dead(i):
                self.dead_states.add(i)
                
        # After you compute the dead states, you can compute the distance from each state
        for i in self.dead_states:
            self.target_distance[i] = 999999999999
        for i in self.target_states:
            self.target_distance[i] = 0
        
        for i in range(self.num_states):
            visited = set()
            visited.update(self.dead_states)
            visited.update(self.target_states)
            for s in range(self.num_states):
                if s in visited:
                    continue
                found = False
                self.target_distance[s] = 999999999999999
                for s2 in self.edges[s].values():
                    if s2 in self.target_distance:
                        found = True
                        if s not in self.target_distance or self.target_distance[s2]+1<self.target_distance[s]:
                            self.target_distance[s] = self.target_distance[s2]+1

        # Then you can compute the maximum distance each state has from a target
        # To do that we need a function that computes if a state is part of a circle first
        def check_state_cycle(state):

            # Which states have already been processed
            looked_at = set()

            # Which states are pending for processing 
            pending = [state]

            # Process them all
            while True:

                # If a circle is non found yet, there is none
                if len(pending) == 0:
                    return False

                # Bring out the next pending state
                state_at = pending.pop()
                if state_at in looked_at:
                    continue
                looked_at.add(state_at)
                    
                # For that state, check every neighbor
                for neighbor in self.edges[state_at].values():
                    if neighbor == state:
                        return True
                    pending.append(neighbor)

        # If a non dead state is part of a cycle, then the maximum distance from a target is infinite
        self.target_max_length = -1
        for i in range(self.num_states):
            if i not in self.dead_states and check_state_cycle(i):
                self.target_max_length = float('inf')
        
        # If there is no cycle in the valid paths, you just need to calculate the furthest path from the
        # start state to one of the target states. For that, we need a dictionary for the maximum length
        # from the start state
        if self.target_max_length == -1:
            distance_start = {}
            pending = [(0,0)] # State, distance from start

            while True:

                # Check if you are done
                if len(pending) == 0:
                    break

                # Get the next state
                state_at, dist = pending.pop()
                if state_at in distance_start and distance_start[state_at] <= dist:
                    continue
                distance_start[state_at] = dist

                # See all the possible connections
                for neighbor in self.edges[state_at].values():
                    # Skip dead states
                    if neighbor not in self.dead_states:
                        pending.append((neighbor,dist+1))
            
            # Now you have all the distances you need, check the longest to a target state
            for st in self.target_states:
                if st in distance_start:
                    self.target_max_length = max(self.target_max_length, distance_start[st])

        # Completed the computations
        self.computed_dead_states = True
        self.computed_target_distance = True
            
    def check_string(self,string):
        # Checks if a string is accepted in the language
        
        # Start at the beginning
        state_at = self.start_state
        
        # Loop through
        for char in string:
            state_at = self.edges[state_at][char]
        
        # Check if you are at a target state
        return state_at in self.target_states
    
    def get_next_string(self, reset = False):
        # This function will find all the strings till specified length that are accepted by the automaton
        # Careful because it is slow as fuck
        
        # depth list contains (state, char_at)
        # state is the state you are in
        # char_at is the character you will be searching next
        
        # First of all, you have to have computed the dead states for this to work reliably
        if not self.computed_dead_states:
            self.compute_dead_states()

        # If you wish to reset, you must clear all the helper variables
        if reset:
            self.next_len = 0
            self.next_in = 1
            self.depth_list = []
            self.backtracked = False
            
        
        # Special case for the null string
        if self.next_len == 0:
            self.next_len = 1
            self.next_in = 1
            self.depth_list.append((0,self.alphabet[0]))
            if 0 in self.target_states:
                return '<null_string>'
        
        # The next found string
        result = ""
        
        # Dive into the tree till you are next_in = next_len
        while True:

            # Special case for when you are done
            if self.target_max_length < self.next_len:
                return None

            if len(self.depth_list) == 0:
                self.depth_list.append((0,self.alphabet[0]))
                self.next_len += 1
                self.next_in = 1
                self.backtracked = False
                continue
            
            # Get the frame you are in
            frame = self.depth_list[-1]
            
            # If you backtracked get the next character
            if self.backtracked:
                self.next_in -= 1
                if frame[1] not in self.ab_next:
                    # Backtrack further
                    self.depth_list.pop()
                    continue
                else:
                    # Skip to the next character
                    self.depth_list[-1] = (frame[0],self.ab_next[frame[1]])
                    self.backtracked = False
                    frame = self.depth_list[-1]
            
            # If you are not at the correct level ascend forward
            if self.next_len > self.next_in:
                
                # Check if you are hopeless first
                if self.target_distance[frame[0]] > self.next_len-self.next_in+1:
                    self.backtracked = True
                    self.depth_list.pop()
                    continue
                
                # Don't forward to a dead state
                all_dead = False
                while self.target_distance[self.edges[frame[0]][frame[1]]] > self.next_len-self.next_in+1:
                    if frame[1] in self.ab_next:
                        frame = (frame[0],self.ab_next[frame[1]])
                        break
                    else:
                        all_dead = True
                        break
                
                # If all else states are dead, you need to backtrack
                if all_dead:
                    self.backtracked = True
                    self.depth_list.pop()
                    continue
                
                # If some state is not dead, just visit it forward
                self.depth_list[-1] = frame
                self.next_in += 1
                self.depth_list.append((self.edges[frame[0]][frame[1]],self.alphabet[0]))
                continue
            
            # There you are at the correct level, start checking where they all lead
            # Till you find one that leads to a target state
            found = False
            while True:
                if self.edges[frame[0]][frame[1]] in self.target_states:
                    found = True
                    break
                elif frame[1] in self.ab_next:
                    frame = (frame[0],self.ab_next[frame[1]])
                else:
                    # You have consumed everything and found nothing
                    break
            
            # If you didn't find it, you need to backtrack
            if not found:
                self.backtracked = True
                self.depth_list.pop()
                continue
            else:
                # You found it, so update the table
                self.depth_list[-1] = (frame[0],frame[1])
                
                # Construct the string
                for el in self.depth_list:
                    result += el[1]
                
                # Try to go the next character
                if frame[1] not in self.ab_next:
                    # You need to backtrack
                    self.backtracked = True
                    self.depth_list.pop()
                    return result
                else:
                    self.depth_list[-1] = (frame[0],self.ab_next[frame[1]])
                    return result

    def extract_nfa(self):
        # Creates and extracts the nfa from this dfa
        # Quite simpler than the other way around

        # Create the new NFA
        new_nfa = NFA()

        # Add the appropriate states
        for i in range(self.num_states-1):
            new_nfa.add_state()

        # Add the appropriate edges
        for state in range(self.num_states):
            # Search it's edges
            for char in self.edges[state]:
                # Add each one to the nfa
                new_nfa.add_edge(state,self.edges[state][char],char)

        # Finally determine which are target
        for ts in self.target_states:
            new_nfa.set_state_target(ts,True)

        # And after all this, return the nfa
        return new_nfa

    def generate(self,num_chars):
        # This is a function that will randomly generate a string that has exactly n characters
        # and is accepted by the automaton
        # It is also close to obsolete, may redo in the future
        
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


def combine_DFA(dfa1:DFA,dfa2:DFA,mode):
    # Combines two dfa's to create combinations
    # Mode determines which states are considered final in the combination
    # Different mode values produce &, |, - and other useful functions

    # DFA's must have the same alphabet
    if dfa1.alphabet != dfa2.alphabet:
        print("Tried to combine dfa's with different alphabet")
        return
    alphabet = dfa1.alphabet.copy()

    # The operation requires dfa's to be complete
    for dfa in (dfa1,dfa2):
        if not dfa.is_complete():
            dfa.make_complete()

    # Create a list for the new states, and for the pending ones
    new_states = []
    pending = []
    
    # Create dictionary for the new state edges
    new_state_edges = {}

    # Create the first state and add it to the pending
    pending.append((0,0))

    # Do the loop to produce the new dfa
    while True:

        # Check if you are done
        if len(pending) == 0:
            break

        # Get the next pending state
        state_at = pending.pop()
        if state_at in new_state_edges:
            continue

        # Add the state to the list and to the edges dictionary
        new_states.append(state_at)
        new_state_edges[state_at] = {}

        # Find all the edges of that state
        for char in alphabet:

            # Find the new state for the character
            state_next = (dfa1.edges[state_at[0]][char],dfa2.edges[state_at[1]][char])

            # Add it to the pending states
            pending.append(state_next)

            # Fill in the specific edge
            new_state_edges[state_at][char] = state_next

    # After that's done you have all the new states for the new dfa,
    # in an arbitrary order in new_states (but the start state is always the first one)
    # and you also have all the edges, so create the new dfa
    new_dfa = DFA(alphabet)

    # Add as many states as you need (the first one is already present)
    for i in range(len(new_states)-1):
        new_dfa.add_state()
    
    # Create a dictionary to enumerate the various states
    state_map = { s:i for i,s in enumerate(new_states)}

    # Fill in all the edges
    for state in new_states:
        # Find the state representation
        ds = state_map[state]
        # Fill in the edges for that one
        for char in new_state_edges[state]:
            # Find the corresponding representation
            cs = state_map[new_state_edges[state][char]]
            # Add the new edge to your new dfa
            new_dfa.add_edge(ds,cs,char)

    # Finally, according to the mode, map which states are final, and which are not
    # We do that by mapping the right function
    is_target = {
        '|': lambda x : x[0] in dfa1.target_states or x[1] in dfa2.target_states,
        '&': lambda x : x[0] in dfa1.target_states and x[1] in dfa2.target_states,
        '-': lambda x : x[0] in dfa1.target_states and x[1] not in dfa2.target_states,
    }[mode]
    for i in range(new_dfa.num_states):
        new_dfa.set_state_target(i,is_target(new_states[i]))

    # Finally, return the new dfa
    return new_dfa

def concat_DFA(dfa1:DFA, dfa2:DFA):
    return concat_NFA(dfa1.extract_nfa(),dfa2.extract_nfa()).extract_dfa()

def kleene_DFA(dfa1:DFA):
    # Produces the kleene star of the given dfa
    return kleene_NFA(dfa1.extract_nfa()).extract_dfa()

def base_DFA(string:str, alphabet):
    # Makes a dfa that recognises a specific string
    res =  base_NFA(string).extract_dfa()
    res.alphabet = alphabet
    res.make_complete()
    return res