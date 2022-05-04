# This is the second attempt at a parser, with more advanced features such as more set operations
# and specific number of repeats for star

from dfa import DFA, digify_DFA, kleene_DFA, base_DFA, combine_DFA, concat_DFA, modulo_DFA
import copy

class RegexpParser:
    # This class reads strings containing regexp, and outputs the dfa.

    def __init__(self):

        # The string you are parsing
        self.string = ""
        self.string_at = 0
        self.char_at = ""
        self.alphabet = []
        self.debug = False
        self.key_symbols = {'(',')','[',']','~','-','|','^','','*','&'}
        
    
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

    def get_special_chars(self, char):
        # Some special characters lead to more symbols than one
        # This function is a map between them

        # If its a length one character, just return that
        if len(char) == 1:
            if char in self.key_symbols:
                return []
            return [char]

        # If its a length two character check cases
        ret = {
            'A': [chr(ord('A')+i) for i in range(26)],
            'a': [chr(ord('a')+i) for i in range(26)],
            '0': [chr(ord('0')+i) for i in range(10)],
            '1': [chr(ord('1')+i) for i in range(9)],
        }
        return ret[char[1]] if char[1] in ret else char[1]

    def find_alphabet(self, string:str):
        # This will find register the complete alphabet for the string

        self.string = string
        self.string_at = 0
        self.char_at = ""
        self.alphabet = []

        # Pass the characters one by one
        while self.string_at < len(self.string):
            self.consume_char()
            self.alphabet.extend(self.get_special_chars(self.char_at))

        # Parse the string again to check for numbers (which is a very special case)
        self.alphabet = set(self.alphabet)-{str(i) for i in range(10)}
        wait_bracket = False
        wait_nondigit = False
        ignore_next = False
        for char in self.string:
            if ignore_next:
                if char == '0':
                    self.alphabet.update({str(i) for i in range(10)})
                if char == '1':
                    self.alphabet.update({str(i+1) for i in range(9)})
                ignore_next=False
                continue
            if char in {str(i) for i in range(10)}:
                if not (wait_nondigit or wait_bracket):
                    self.alphabet.add(char)
            else:
                wait_nondigit = False
            if char == '[':
                wait_bracket=True
                continue
            if char == ']':
                wait_bracket=False
                continue
            if char == '\\':
                ignore_next=True
            if char == '^':
                wait_nondigit = True

        self.alphabet = list(self.alphabet)
        self.alphabet.sort()
        # You found all the alphabet, time to parse!

    def parse_string(self,string:str,debug=False):
        # This will parse a string
        
        # Parse the alphabet first
        self.find_alphabet(string)
        self.debug = debug

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

    

    ## FROM HERE, WE DEFINE THE VARIOUS PARSING FUNCTIONS ACCORDING TO THE GRAMMAR

    def throw_unexpected(self,parsed:str):
        # Throws unexpected character exception
        raise Exception("Unexpected symbol '"+self.char_at+"' while parsing "+parsed) 
    
    def report_progress(self,at:str):
        if self.debug:
            print("Entering "+at+" with",self.string[:self.string_at-1],"{"+self.char_at+"}",self.string[self.string_at:])

    def report_exit(self,at:str):
        if self.debug:
            print("Exiting "+at+" with",self.string[:self.string_at-1],"{"+self.char_at+"}",self.string[self.string_at:])


    def expr(self):
        self.report_progress('expr')

        # Check that the character is correct
        if self.char_at in self.key_symbols - {'(', '|', '~', '', ')', '-', '&'}:
            self.throw_unexpected('expr')
        
        # If it's correct, parse the termlist and send it over to the restexpr
        termlist = self.ptermlist()
        res = self.restexpr(termlist)
        self.report_exit('expr')
        return res

    def restexpr(self,prev:DFA):
        self.report_progress('restexpr')

        
        # Check cases
        if self.char_at in {'|','&','-'}:
            
            # Get the operation and consume the character
            op = self.char_at
            self.consume_char()

            # Parse the expression
            expr = self.expr()

            # Combine with the previous and return it
            self.report_exit('restexpr')
            return combine_DFA(prev,expr,op)

        elif self.char_at in {')', ''}:

            # Just return the previous expression
            self.report_exit('restexpr')
            return prev

        else:
            self.throw_unexpected('restexpr')

    def ptermlist(self):
        self.report_progress('ptermlist')


        # Check that you have the correct characters
        if self.char_at in self.key_symbols-{'~', '('}:
            self.throw_unexpected('ptermlist')

        # If you got correct symbols, proceed with the parsing
        term = self.term()
        res = self.termlist(term)
        self.report_exit('ptermlist')
        return res

    def termlist(self,prev:DFA):
        self.report_progress('termlist')


        # Check that you have the correct characters
        if self.char_at in self.key_symbols-{'~', '(','|', '', ')', '-', '&'}:
            self.throw_unexpected('termlist')

        # Check if you are in the null condition
        if self.char_at in {'|', '', ')', '-', '&'}:
            self.report_exit('termlist')
            return prev
        else:
            # Parse and combine with the previous
            term = self.term()
            res = self.termlist(concat_DFA(prev,term))
            self.report_exit('termlist')
            return res

    def term(self):
        self.report_progress('term')


        # Check that you have correct characters
        if self.char_at in self.key_symbols-{'~', '('}:
            self.throw_unexpected('term')

        # Parse the negation and the rest term
        neg = self.neg()
        restterm = self.restterm()

        # Negate if there is negation, and return
        if neg:
            restterm.negate()
        self.report_exit('term')
        return restterm

    def restterm(self):
        self.report_progress('restterm')


        # Check that you have correct characters
        if self.char_at in self.key_symbols-{'('}:
            self.throw_unexpected('restterm')

        # Check if you have complex expression
        if self.char_at == '(':
            self.consume_char()
            expr = self.expr()
            if self.char_at != ')':
                self.throw_unexpected('restterm')
            self.consume_char()
        else:
            # You have a list of characters, create the new dfa
            
            # Get the list of characters
            char_list = self.get_special_chars(self.char_at)
            self.consume_char()

            # Create the union DFA from those characters
            expr = base_DFA(char_list[0],self.alphabet)
            for char in char_list[1:]:
                temp = base_DFA(char,self.alphabet)
                expr = combine_DFA(expr,temp,'|')
        
        # Finally parse the star
        star = self.star()

        # Check the star cases
        if type(star) == bool and star:
            # Add kleene star to the mix
            expr = kleene_DFA(expr)
        elif type(star) in {int,tuple}:
            # Find the start and the end
            if type(star) == int:
                start, end = (star, star)
            else:
                start, end = (star[0],star[1])

            # Repeat for every repetition number
            final = None
            for r in range(start,end+1):
                # R is the number of repetitions,
                # construct a DFA with this number of repetitions
                if r == 0:
                    # Special case for the zero repetitions
                    temp = DFA(self.alphabet)
                    temp.make_complete()
                else:
                    temp = copy.deepcopy(expr)
                    for i in range(r-1):
                        temp = concat_DFA(temp,expr)

                # Add to the final
                if not final:
                    final = temp
                else:
                    final = combine_DFA(final,temp,'|')

            # Set the expr to be the final
            expr = final

        # After all the parsing, return the expr
        self.report_exit('restterm')
        return expr

    def neg(self):
        self.report_progress('neg')

        
        # Check if you have the correct character
        if self.char_at in self.key_symbols-{'(','~'}:
            self.throw_unexpected('neg')

        # Check if you have a negative
        if self.char_at == '~':
            self.consume_char()
            self.report_exit('neg')
            return True
        
        # If it's the empty case, return false
        self.report_exit('neg')
        return False
        
    def star(self):
        self.report_progress('star')


        # Check that you have a correct character
        if self.char_at in self.key_symbols- {'^','*','(', '|', '~', '', ')', '-', '&'}:
            self.throw_unexpected('star')

        # Check if you have just a star
        if self.char_at == '*':
            self.consume_char()
            self.report_exit('star')
            return True

        # Check if you have a complex star
        if self.char_at == '^':
            self.consume_char()
            res = self.num()
            self.report_exit('star')
            return res

        # If nothing of the sort, just return false
        self.report_exit('star')
        return False
    
    def num(self):
        self.report_progress('num')


        # Case for real number
        if self.char_at.isdigit():
            res = self.actualnum()
            self.report_exit('num')
            return res
        
        # Case for [num-num]
        if self.char_at == '[':
            self.consume_char()
            num1 = self.actualnum()
            if self.char_at != '-':
                self.throw_unexpected('num')
            self.consume_char()
            num2 = self.actualnum()
            if self.char_at != ']':
                self.throw_unexpected('num')
            self.consume_char()
            if num1 > num2:
                raise Exception("Tried to define a range with descending order")
            self.report_exit('num')
            return (num1, num2)
        
        # If you didn't get any of those, there is an error
        self.throw_unexpected('num')

    def actualnum(self):
        self.report_progress('actualnum')


        # Check that you have a digit
        if not self.char_at.isdigit():
            self.throw_unexpected('actualnum')
        
        # Convert the digit and pass it to the rest of the number
        dchar = self.char_at
        self.consume_char()
        return self.restnum(ord(dchar)-ord('0'))
    
    def restnum(self,prev):
        self.report_progress('restnum')


        # Check if you have a digit
        if self.char_at.isdigit():
            # Parse the rest
            dchar = self.char_at
            self.consume_char()
            return self.restnum(prev*10+(ord(dchar)-ord('0')))

        # If you don't have a digit, check that you have a valid character
        if self.char_at in self.key_symbols-{'(', '|', ']', '~', '', ')', '-', '&'}:
            self.throw_unexpected('restnum')
        
        # If you don't have anything else, return the previous one
        return prev

def main():

    # Read the input
    reg = input()

    # Create a regular expression object and parse the input
    rexp = RegexpParser()
    dfa = rexp.parse_string(reg)
    #dfa.print_info()
    
    dfa = digify_DFA(dfa)


    dfa.compute_dead_states()
    while len(input()) == 0:
        res = dfa.get_next_string(False)
        if res:
            if res != '<null_string>':
                print(res,end = ', ')
        else:
            break

def test():
    # A test for the modulo DFA

    # Create a modulo dfa of 6
    my_dfa = modulo_DFA(6)

    # Turn states to final
    my_dfa.set_state_target(1,True)
    my_dfa.set_state_target(2,True)

    # Add the fix for starting with zero
    parser = RegexpParser()
    my_dfa = combine_DFA(my_dfa,parser.parse_string("\\1\\0*"),'&')

    # Check what it produces
    while len(input()) == 0:
        res = my_dfa.get_next_string(False)
        if res:
            if res != '<null_string>':
                print(res,end = ', ')
        else:
            break


    pass


if __name__ == "__main__":
    main()
    #test()