from nfa import *

class RegexpParser:
    # This class will parse a string from regexp into an NFA

    def __init__(self):

        # The string you are parsing
        self.string = ""
        self.string_at = 0
        self.char_at = ""
    
    def consume_char(self):
        # This will discard the current character and read the next one

        # Check if you have reached the end
        if self.string_at >= len(self.string):
            self.char_at = ""
            return
        
        # Check if the next character is a \
        if self.string[self.string_at] == "\\":
            
            # Check if there is a next character
            self.string_at += 1
            if len(self.string) == self.string_at:
                raise Exception()
            
            # If there is a next character, grab it as the current
            self.char_at = "\\"+self.string[self.string_at]
            self.string_at += 1
            return
        
        else:
            # Every other character is treated normally
            self.char_at = self.string[self.string_at]
            self.string_at += 1
            return

    def parse_string(self,string):
        # This will parse a string
        
        # Initiate the parser
        self.string = string
        self.string_at = 0
        self.char_at = ""

        # Get the first character
        self.consume_char()
        
        try:
            return self.expr()
        except Exception as e:
            print(e)

        pass

    # These are the parsing functions
    # Mostly they return the NFA
    def expr(self):
        # Expr

        # Check that the character is legal
        if self.char_at in [')','','|','*']:
            raise Exception("Rule expr did not expect "+self.char_at)
        
        # Check the term and the rest of the expression
        term = self.term()
        restexpr = self.restexpr(term)

        # Return the result of the restexpr
        return restexpr
    
    def restexpr(self,prev:NFA):
        # Restexpr

        # Check the case
        if self.char_at in ['|']:

            # Consume the next char
            self.consume_char()
        
            # Get the expression
            expr = self.expr()

            # Combine with the previous and return it
            return union_NFA(prev,expr)

        elif self.char_at in ['',')']:
            # Just return the previous
            return prev

        else:
            raise Exception("Rule restexpr expected |, ) or blank, not "+self.char_at)

    def term(self):
        # Term

        # Check the character
        if self.char_at not in [')','*','|','']:
            
            # Get the character
            char = self.char()
            
            # Get the following string
            string = self.str()
            
            # Combine and return them
            if string:
                return concat_NFA(char,string)
            else:
                return char
            
        else:
            raise Exception("Rule term did not expect "+self.char_at)
        
    def star(self):
        # Star
        
        # Check the next char
        if self.char_at in ['*']:
            
            # Consume the star
            self.consume_char()
            return True
        else:
            return False
        
    def str(self):
        # Str
        
        # Check that you have something correct
        if self.char_at == "*":
            raise Exception("Rule str did not expect *")
        
        # Check if it's an empty string
        if self.char_at in ['',')','|']:
            return None
        
        # In other cases get the char and the other str
        char = self.char()        
        str = self.str()
        
        # Combine for the result
        if str:
            return concat_NFA(char,str)
        else:
            return char
    
    def char(self):
        # Char
        
        # Check that you don't have garbage
        if self.char_at in [')','|','*','']:
            raise Exception("Rule char did not expect "+self.char_at)
        
        # Check if you have a (
        if self.char_at == '(':
            
            # Consume it
            self.consume_char()
            
            # Get the expression
            expr = self.expr()
            
            # Check that you have the ) and consume it
            if self.char_at != ')':
                raise Exception("Rule char has a dangling (")
            self.consume_char()
            
        else:
            
            # Produce the actual char NFA
            
            # Take cases for special nfas
            if len(self.char_at) == 2:
                # Special character that starts with \
                
                # Define the collections
                coll = {
                    'A': [chr(ord('A')+i) for i in range(26)],
                    'a': [chr(ord('a')+i) for i in range(26)],
                    '0': [chr(ord('0')+i) for i in range(10)],
                    '1': [chr(ord('1')+i) for i in range(9)]
                }

                if self.char_at[-1] in coll:
                    expr = NFA()
                    expr.add_state(True)
                    for l in coll[self.char_at[-1]]:
                        expr.add_edge(0,1,l)
                else:
                    # Not a special character
                    expr = base_NFA(self.char_at[-1])
            else:
                expr = base_NFA(self.char_at)
            self.consume_char()
            
        
        # Parse the star
        star = self.star()
        
        # kleene it if you have a star
        if star:
            return kleene_NFA(expr)
        else:
            return expr


def next_string(string, alphabet):
    # Produces the next string derived from that one according to the alphabet
    
    # Get a dictionary to process alphabet
    alpha = {}
    for i in range(len(alphabet)-1):
        alpha[alphabet[i]] = alphabet[i+1]
    
    # Create the new string
    new_string = ""
    incr = True
    for i in reversed(range(len(string))):
        if not incr:
            char = string[i]
        elif string[i] in alpha:
            char = alpha[string[i]]
            incr = False
        else:
            char = alphabet[0]
        new_string = char+new_string        
    if incr:
        new_string = alphabet[0]+new_string
    return new_string


def main():


    # Read the input
    reg = input()

    # Create a regular expression object and parse the input
    rexp = RegexpParser()
    nfa = rexp.parse_string(reg)
    #nfa.print_info()
    
    # Get the nfa and turn into dfa
    dfa = nfa.extract_dfa()
    #dfa.print_info()
    
    # Get the alphabet
    alphabet = list(dfa.get_alphabet())
    alphabet.sort()

    # Start with the null string and see how many can you find
    string = ""
    still = 10
    while len(string) < 10:
        if dfa.check_string(string):
            print(string,end=", ")
            still -= 1
            if still == 0:
                if len(input())>0:
                    break
                still = 10
        string = next_string(string,alphabet)
    


if __name__ == "__main__":
    main()