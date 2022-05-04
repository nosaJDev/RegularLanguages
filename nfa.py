

class NFA:
    # Representation of a NFA
    # One start state, multiple end states
    
    def __init__(self):
        
        # First the states, states are uniquly defined by numbers
        self.num_states = 1
        self.start_state = 0
        self.target_states = set()
        
        # Then the edges, which is a dictionary of the states
        # Each key has a list of edges
        # Edges are tupples (end_state, 'symbols')
        # Start state is inferred from the dictionary
        self.edges = {
            0:[]
        }
        
    def print_info(self):
        # Prints the whole of the nfa
        print("States:",self.num_states)
        print("Start-state:", self.start_state)
        print("End-states:",self.target_states)
        
        for elist in self.edges:
            print(str(elist)+":",end=' ')
            print(self.edges[elist])
                
    def add_state(self,target=False):
        # This will add a state to the NFA and return its number
        self.num_states += 1
        new_state = self.num_states-1
        
        # Set it to target if you need to
        if target:
            self.target_states.add(new_state)
            
        # Add new entry to the edges
        self.edges[new_state] = []
        
        return new_state
    
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
    
    def return_edges_offset(self, offset):
        # This will return the dictionary of states, but will offset every state by offset
        # It is particularly useful for combining NFAs derived from regular expressions
        
        edges_offset = {}
        for state in self.edges:
            
            edges_offset[state+offset] = []
            # Repeat for all the edges
            for edge in self.edges[state]:
                edges_offset[state+offset].append((edge[0]+offset,edge[1]))

        return edges_offset
            
    def reset_edges(self):
        # This will drop all the edges of the automaton
        self.edges = {}
        for i in range(self.num_states):
            self.edges[i] = []
    
    def add_edge(self, ss, se, string):
        # This will add an edge to the automaton
        
        # Edges have to be added on already existing states
        if ss >= self.num_states or se >= self.num_states:
            print("You tried to add an edge between non-existing state")
            return
        
        self.edges[ss].append((se,string))
          
    def simplify(self):
        # This will break up rules that consist of more than one characters
        # It will produce states as it goes
        
        # Get the old edges end drop them
        old_edges = self.edges.copy()
        self.reset_edges()
        
        # Loop through the old edges to see if you need to split
        for state in old_edges:
            for e in old_edges[state]:
                
                # Construct a useful edge representation
                edge = (state, e[0], e[1])
            
                # Check if the edge has more than one character
                if len(edge[2]) <= 1:
                    # Just add it as is
                    self.add_edge(edge[0],edge[1],edge[2])
                    continue
                
                # If you have more than one character, you need new edges
                ss = edge[0]
                se = edge[1]
                ne_num = len(edge[2])-1
                for i in range(ne_num):
                    
                    # Find the next character
                    char = edge[2][i]
                    
                    # Take a step
                    ns = self.add_state()
                    self.add_edge(ss,ns,char)
                    ss = ns
                
                # Finally connect the path to the old
                self.add_edge(ss,se,edge[2][-1])
                
    def derive_alphabet(self):
        
        # Runs through the edge list, and finds the characters of the alphabet
        alphabet = set()
        for state in self.edges:
            for edge in self.edges[state]:
                for char in edge[1]:
                    alphabet.add(char)
        
        # Return the alphabet
        return alphabet
    
    # Below are some functions that help turn the NFA into a DFA
    def instant_states(self,state):
        # This will return a set of all the states that are reachable from the supplied, with specific input character
        
        marked = set()
        tovisit = [state]
        
        # Begin the search
        while True:
            
            # If you don't have more you are done
            if len(tovisit) == 0:
                break
            
            # Take a pending state and check that it's not yet marked
            state_at = tovisit.pop()
            if state_at in marked:
                continue
            marked.add(state_at)
            
            # Mark it and find all the legit visitors
            for e in self.edges[state_at]:
                if e[1] == '':
                    tovisit.append(e[0])
        
        # After you finish, return all that were marked
        return marked
    
    def char_states(self, state_set, char):
        # This will return a set of states that are reachable by any of the states
        # in the provided set by use of one character
        # It is assumed that the provided states are inclusive of the instant states
        
        # The set to store all the results
        result = set()
        
        # Loop through all the states in the set
        for state in state_set:
            
            # Find all the states that you can access with the char
            access_states = set()
            for e in self.edges[state]:
                if e[1] == char:
                    access_states.add(e[0])
            
            # For all the states you found, try the instant_state and add the result to the end states
            for s in access_states:
                result.update(self.instant_states(s))
        
        return result
                
    def extract_dfa(self):
        
        from dfa import DFA
        # This function will extract a DFA from this NFA
        # Make sure to call simplify first
        
        # First we need to figure out the alphabet
        alphabet = self.derive_alphabet()
        
        # The following function will turn state sets into tupples that are hashable
        def tuple_from_states(states):
            ls = list(states)
            ls.sort()
            return tuple(ls)
        
        # Then I need to create a dictionary with all the new states
        # The dictionary will contain tupples with old states
        dfa_states = {}
        
        # I need to process all the states in that list
        start_state = tuple_from_states(self.instant_states(self.start_state))
        pending = [start_state]
        visited = set() # This will mark those that are already processed
        
        while True:
            
            # Check if you are done
            if len(pending) == 0:
                break
            
            # Put out the next state you will be visiting
            state_at = pending.pop()
            
            # Check if you have seen this one already
            if state_at in visited:
                continue

            visited.add(state_at)
            
            # Add it to the dictionary
            dfa_states[state_at] = {}
            
            # Do all the possible paths
            for char in alphabet:
                
                # Find the state for this character
                next_state = tuple_from_states(self.char_states(set(state_at),char))

                # Add it to the pending and to the dictionary
                dfa_states[state_at][char] = next_state
                pending.append(next_state)

        # After you finish, create a mapping between the states and numbers
        at = 1
        mapping = {}
        for state in dfa_states:
            if state == start_state:
                mapping[state] = 0
                continue
            mapping[state] = at
            at += 1
        
        # Then create the dfa
        mydfa = DFA(alphabet)
        
        # Create for the dfa as many states as you must
        for i in range(len(dfa_states)-1):
            mydfa.add_state()         

        # Add all the edges that you found
        for state in dfa_states:
            d_state = mapping[state]
            for char in dfa_states[state]:
                mydfa.add_edge(d_state,mapping[dfa_states[state][char]],char)
        
        # Finally, make the targets state correct
        for state in dfa_states:
            for s in state:                
                if s in self.target_states:
                    mydfa.set_state_target(mapping[state],True)
                    
        # You are done, return the DFA
        return mydfa

# Below are useful functions for combining NFAs and producing the kleene star
def union_NFA(nfa1:NFA, nfa2:NFA):
    # This will produce the nfa that is the union of the above
    
    # First get their edges by offset
    nfa1_edges = nfa1.return_edges_offset(1)
    nfa2_edges = nfa2.return_edges_offset(nfa1.num_states+1)
    
    # Construct the new NFA
    new_nfa = NFA()
    
    # Combine to the new nfa
    for i in range(nfa1.num_states+nfa2.num_states+1):
        new_nfa.add_state()
    new_nfa.num_states = nfa1.num_states+nfa2.num_states+2
    new_nfa.edges.update(nfa1_edges)
    new_nfa.edges.update(nfa2_edges)
    
    # Add missing edges
    new_nfa.edges[0] = [(1,''),(nfa1.num_states+1,'')]
    for state1 in nfa1.target_states:
        new_nfa.add_edge(state1+1,new_nfa.num_states-1,'')
    for state2 in nfa2.target_states:
        new_nfa.add_edge(state2+nfa1.num_states+1,new_nfa.num_states-1,'')
    
    # Set the final state to be a target
    new_nfa.set_state_target(new_nfa.num_states-1,True)
    
    # The nfa is complete
    return new_nfa

def concat_NFA(nfa1:NFA, nfa2:NFA):
    # This will create the concatenation of the two NFAs into one
    
    # Get their edges by offset
    nfa1_edges = nfa1.return_edges_offset(0)
    nfa2_edges = nfa2.return_edges_offset(nfa1.num_states)
    
    # Create a new NFA with as many states as the two together
    new_nfa = NFA()
    for i in range(nfa1.num_states+nfa2.num_states-1):
        new_nfa.add_state()
    
    # Copy over the edge mappings
    new_nfa.edges.update(nfa1_edges)
    new_nfa.edges.update(nfa2_edges)
    
    # Create the missing edges
    for s1 in nfa1.target_states:
        new_nfa.add_edge(s1,nfa1.num_states,'')
    
    # Set the appropriate states to final
    for s2 in nfa2.target_states:
        new_nfa.set_state_target(s2+nfa1.num_states,True)
        
    # The new nfa is complete
    return new_nfa

def kleene_NFA(nfa1:NFA):
    # This will produce the kleene star nfa of the given
    
    # Get the old nfa edges by offset
    nfa1_edges = nfa1.return_edges_offset(1)
    
    # Create the new nfa and add the appropriate states 
    new_nfa = NFA()
    for i in range(nfa1.num_states):
        new_nfa.add_state()
        
    # Copy over the edges
    new_nfa.edges.update(nfa1_edges)
    
    # Add missing edges
    for s in nfa1.target_states:
        new_nfa.add_edge(s+1,0,'')
    new_nfa.add_edge(0,1,'')
    
    # Set a target state
    new_nfa.set_state_target(0,True)
    
    # The nfa is complete
    return new_nfa

def base_NFA(string:str):
    # This will create a base nfa that only accepts a single string
    
    # Initialize the NFA
    new_nfa = NFA()

    # Add the target state
    new_nfa.add_state(True)

    # Add the single edge
    new_nfa.add_edge(0,1,string)

    # Return the newly created nfa
    return new_nfa

    