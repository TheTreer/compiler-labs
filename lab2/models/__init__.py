from typing import List
from enum import Enum

EPSILON = '<epsilon>'
END_OF_INPUT = '$'
DOT = '.'

class Symbol:
    EPSILON = EPSILON
    END = END_OF_INPUT
    def __init__(self, name):
        self.value = name

    def __str__(self):
        if self.value == EPSILON:
            return 'ε'
        return self.value

    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(str(self.value))

class Production:
    def __init__(self, head:Symbol, body: List[Symbol]):
        self.head = head
        self.body = body

    def __str__(self):
        return str(self.head) + ' -> ' + ' '.join([str(x) for x in self.body])

    def __repr__(self):
        return str(self.head) + ' -> ' + ' '.join([str(x) for x in self.body])

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(str(self.head) + str(self.body))

class Grammar:
    __first = None
    __follow = None
    
    def __init__(self, productions: List[Production]):
        self.productions = productions
        self.start_symbol = productions[0].head
        
        # check if the productions are valid
        non_terminals = {}
        terminals = {}
        for prod in productions:
            non_terminals[prod.head.value] = prod.head
        for prod in productions:
            for sym in prod.body:
                if sym.value not in non_terminals:
                    terminals[sym.value] = sym
                    
        self._non_terminals = [x for x in non_terminals.values()]
        self._terminals = [x for x in terminals.values()]
        
        print('Non-terminals:', self._non_terminals)
        print('Terminals:', self._terminals)
        
        # self.init_first()
        # self.init_follow()
        
    def init_first(self):
        self.__first = {}
        for non_term in self._non_terminals:
            self.__first[non_term] = set()
        for term in self._terminals:
            self.__first[term] = set([term])
        
        # Assumption: max iterations equals the number of productions
        for _ in range(len(self.productions)):
            for production in self.productions:
                head_symbol = production.head
                body_symbols = production.body
                for symbol in body_symbols:
                    # If the symbol is a terminal, add it to the FIRST set
                    if symbol in self._terminals:
                        self.__first[head_symbol].add(symbol)
                        break
                    # If the symbol is a non-terminal, add its FIRST set to the current head symbol's FIRST set
                    elif symbol in self._non_terminals:
                        self.__first[head_symbol] |= (self.__first[symbol] - {Symbol(EPSILON)})
                        # If the current symbol's FIRST set does not contain EPSILON, break the loop
                        if Symbol(EPSILON) not in self.__first[symbol]:
                            break
                # If the loop finished without breaking, it means all symbols in the production can derive EPSILON
                else:
                    self.__first[head_symbol].add(Symbol(EPSILON))
    
    def init_follow(self):
        # TO-DO
        # Generated by Copilot, to be refactored
        self.__follow = {}
        for non_term in self._non_terminals:
            self.__follow[non_term] = set()
        self.__follow[self.start_symbol] = set([Symbol(END_OF_INPUT)])
        
        # Assumption: max iterations equals the number of productions
        for _ in range(len(self.productions)):
            for production in self.productions:
                head_symbol = production.head
                body_symbols = production.body
                for i, symbol in enumerate(body_symbols):
                    # If the symbol is a non-terminal
                    if symbol in self._non_terminals:
                        # If the symbol is the last in the body, add the FOLLOW set of the head to its FOLLOW set
                        if i == len(body_symbols) - 1:
                            self.__follow[symbol] |= self.__follow[head_symbol]
                        else:
                            added_terminal = False
                            for j in range(i + 1, len(body_symbols)):
                                next_symbol = body_symbols[j]
                                # If the next symbol is a terminal, add it to the current symbol's FOLLOW set
                                if next_symbol in self._terminals:
                                    self.__follow[symbol].add(next_symbol)
                                    added_terminal = True
                                    break
                                # If the next symbol is a non-terminal, add its FIRST set (minus EPSILON) to the current symbol's FOLLOW set
                                elif next_symbol in self._non_terminals:
                                    self.__follow[symbol] |= (self.__first[next_symbol] - {Symbol(EPSILON)})
                                    # If EPSILON is not in the next symbol's FIRST set, break the loop
                                    if Symbol(EPSILON) not in self.__first[next_symbol]:
                                        added_terminal = True
                                        break
                            # If the loop finished without breaking, it means all symbols after the current one can derive EPSILON
                            # So, add the FOLLOW set of the head to the current symbol's FOLLOW set
                            if not added_terminal:
                                self.__follow[symbol] |= self.__follow[head_symbol]

    def first(self, term: List[Symbol] | Symbol):
        if self.__first is None:
            self.init_first()
        if isinstance(term, Symbol):
            return self.__first[term]
        first_set = set()
        for sym in term:
            if sym in self._terminals:
                first_set.add(sym)
                break
            elif sym in self._non_terminals:
                first_set |= self.__first[sym] - set([Symbol(EPSILON)])
                if Symbol(EPSILON) not in self.__first[sym]:
                    break
        return first_set
    def follow(self, term: List[Symbol] | Symbol):
        if self.__follow is None:
            self.init_follow()
        if isinstance(term, Symbol):
            return self.__follow[term]
        follow_set = set()
        for sym in term:
            if sym in self._terminals:
                follow_set.add(sym)
                break
            elif sym in self._non_terminals:
                follow_set |= self.__follow[sym]
                if Symbol(EPSILON) not in self.__follow[sym]:
                    break
        return follow_set
    def __str__(self):
        return '\n'.join([str(x) for x in self.productions])

    def __repr__(self):
        return '\n'.join([str(x) for x in self.productions])

    def __eq__(self, other):
        return self.productions == other.productions

    def __hash__(self):
        return hash(str(self.productions))
    
    def __iter__(self):
        return iter(self.productions)

class Item(Production):
    def __init__(self, production: Production, dot_index: int, forward: List[Symbol] = None):
        super().__init__(production.head, production.body)
        self.dot_index = dot_index
        self.forward = forward

    def get_production(self):
        return Production(self.head, self.body)

    def __str__(self):
        if self.forward is None:
            return f'{self.head} -> {" ".join([str(x) for x in self.body[:self.dot_index]] + [DOT] + [str(x) for x in self.body[self.dot_index:]])}'
        return f'{self.head} -> {" ".join([str(x) for x in self.body[:self.dot_index]] + [DOT] + [str(x) for x in self.body[self.dot_index:]])} forward: {self.forward}'
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(str(self.head) + str(self.body) + str(self.dot_index))

    def next_symbol(self):
        if self.dot_index == len(self.body):
            return None
        return self.body[self.dot_index]

    def advance(self):
        return Item(Production(self.head, self.body), self.dot_index + 1)
    
    def is_reduce(self) -> bool:
        return self.dot_index == len(self.body)

class State:
    states : List[Item]
    def __init__(self, kernel: List[Item]):
        self.kernel = kernel
        self.states = []
        self.states += kernel
    
    def __str__(self):
        return f'{self.states}'
    
    def __repr__(self):
        return self.kernel
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    def __hash__(self):
        return hash(str(self.kernel))

class Action(Enum):
    SHIFT = 1
    REDUCE = 2
    ACCEPT = 3
    GOTO = 4

class Behavior:
    def __init__(self, action: Action, value: int):
        self.action = action
        self.value = value

    def __str__(self):
        return f'{self.action.name} {self.value}'
    def __repr__(self) -> str:
        return self.__str__()
    