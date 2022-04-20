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
            self.char_at = self.string[self.string_at]
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

        pass

    # These are the parsing functions
    # Mostly they return the NFA
    def expr(self):
        # Expr

        # Get the next character
        self.consume_char()
        
        # Every character is allowed in the expression
        term = self.term()
        restexpr = self.restexpr(term)

        # Return the result of the restexpr
        return restexpr
    
    def restexpr(self,prev):
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
            raise Exception()

    def term(self):

        # Check the character
        if self.char_at in ['(']
