from . import Production, Symbol, Node, Action, EPSILON, END_OF_INPUT, DOT, logger
from typing import List

from compiler_labs.lab2.models import Action

class Grammar:
    _first = {}
    _follow = {}
    _non_terminals = []
    _terminals = []
    start_symbol: str = ''
    
    def __init__(self, productions: List[Production] = None):
        if productions is None:
            return
        self.productions = productions
        self.start_symbol = productions[0].head
        
        # check if the productions are valid
        non_terminals = {}
        terminals = {}
        for prod in productions:
            non_terminals[prod.head.value] = prod.head
        for prod in productions:
            for sym in prod.body:
                if sym.value not in non_terminals and sym.value != EPSILON:
                    terminals[sym.value] = sym
                    
        self._non_terminals = [x for x in non_terminals.values()]
        self._terminals = [x for x in terminals.values()]
        self._terminals += [Symbol(END_OF_INPUT)]
        
        self.init_first()
        self.init_follow()
        
        logger.info(f'Start to build a grammar...')
        logger.debug(f'Productions: \t"{productions}"')
        logger.debug(f'Non-terminals: \t"{self._non_terminals}"')
        logger.debug(f'Terminals: \t"{self._terminals}"')
        logger.debug(f'Start symbol: \t"{self.start_symbol}"')
        logger.debug(f'First set: \t"{self._first}"')
        logger.debug(f'Follow set: \t"{self._follow}"')
        logger.info(f'Grammar built successfully')
        
        
    def init_first(self):
        self._first = {}
        for non_term in self._non_terminals:
            self._first[non_term] = set()
        for term in self._terminals:
            self._first[term] = set([term])
        
        # Assumption: max iterations equals the number of productions
        for _ in range(len(self.productions)):
            for production in self.productions:
                head_symbol = production.head
                body_symbols = production.body
                for symbol in body_symbols:
                    # If the symbol is a terminal, add it to the FIRST set
                    if symbol in self._terminals:
                        self._first[head_symbol].add(symbol)
                        break
                    # If the symbol is a non-terminal, add its FIRST set to the current head symbol's FIRST set
                    elif symbol in self._non_terminals:
                        self._first[head_symbol] |= (self._first[symbol] - {Symbol(EPSILON)})
                        # If the current symbol's FIRST set does not contain EPSILON, break the loop
                        if Symbol(EPSILON) not in self._first[symbol]:
                            break
                # If the loop finished without breaking, it means all symbols in the production can derive EPSILON
                else:
                    self._first[head_symbol].add(Symbol(EPSILON))
    
    def init_follow(self):
        # TO-DO
        # Generated by Copilot, to be refactored
        self._follow = {}
        for non_term in self._non_terminals:
            self._follow[non_term] = set()
        self._follow[self.start_symbol] = set([Symbol(END_OF_INPUT)])
        
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
                            self._follow[symbol] |= self._follow[head_symbol]
                        else:
                            added_terminal = False
                            for j in range(i + 1, len(body_symbols)):
                                next_symbol = body_symbols[j]
                                # If the next symbol is a terminal, add it to the current symbol's FOLLOW set
                                if next_symbol in self._terminals:
                                    self._follow[symbol].add(next_symbol)
                                    added_terminal = True
                                    break
                                # If the next symbol is a non-terminal, add its FIRST set (minus EPSILON) to the current symbol's FOLLOW set
                                elif next_symbol in self._non_terminals:
                                    self._follow[symbol] |= (self._first[next_symbol] - {Symbol(EPSILON)})
                                    # If EPSILON is not in the next symbol's FIRST set, break the loop
                                    if Symbol(EPSILON) not in self._first[next_symbol]:
                                        added_terminal = True
                                        break
                            # If the loop finished without breaking, it means all symbols after the current one can derive EPSILON
                            # So, add the FOLLOW set of the head to the current symbol's FOLLOW set
                            if not added_terminal:
                                self._follow[symbol] |= self._follow[head_symbol]


         
    def first(self, term: List[Symbol] | Symbol):
        if isinstance(term, Symbol):
            return self._first[term]
        first_set = set()
        for sym in term:
            if sym in self._terminals:
                first_set.add(sym)
                break
            elif sym in self._non_terminals:
                first_set |= self._first[sym] - set([Symbol(EPSILON)])
                if Symbol(EPSILON) not in self._first[sym]:
                    break
        return first_set
    def follow(self, term: List[Symbol] | Symbol):
        if isinstance(term, Symbol):
            return self._follow[term]
        follow_set = set()
        for sym in term:
            if sym in self._terminals:
                follow_set.add(sym)
                break
            elif sym in self._non_terminals:
                follow_set |= self._follow[sym]
                if Symbol(EPSILON) not in self._follow[sym]:
                    break
        return follow_set
    
    def augment_grammar(self, productions: List[Production]):
        logger.info(f'Augmenting grammar...')
        new_start = productions[0].head
        while new_start in [x.head for x in productions]:
            new_start = Symbol(new_start.value + "'")
        new_production = Production(new_start, [productions[0].head])
        productions.insert(0, new_production)
        logger.debug(f'Augmented grammar: {productions}, new start symbol: "{new_start}"')
        return productions, new_start

    
    def dump_state_names(self):
        state_name = {}
        for index, state in enumerate(self.states):
            state_name[state] = f'{index}'
        return state_name

    def dump(self):
        return pickle.dumps(self)
    
    def load(data):
        return pickle.loads(data)

    def parse(self, input: str):
        logger.info(f'Parsing input "{input}"')
        table, _ = self.dump_table()
        state_name_map = self.dump_state_names()
        
        input = [Symbol(x) for x in input.split()]
        input += [Symbol(END_OF_INPUT)]
        result = []
        
        state_stack = [next(iter(table))]
        symbol_stack = [Symbol(END_OF_INPUT)]
        input_index = 0
        while True:
            input_ch = input[input_index]
            if input_ch not in self._terminals:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': 'Unknown symbol'})
                break
            action = table[state_stack[-1]][input[input_index]]
            if action.action == Action.SHIFT:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': f'Shift {action.value}'})
                state_stack.append(action.value)
                symbol_stack.append(input[input_index])
                input_index += 1
            elif action.action == Action.REDUCE:
                production = self.productions[action.value]
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': f'Reduce {production}'})
                for _ in range(len(production.body)):
                    state_stack.pop()
                    symbol_stack.pop()
                symbol_stack.append(production.head)
                state_stack.append(table[state_stack[-1]][symbol_stack[-1]].value)
            elif action.action == Action.ACCEPT:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': 'Accept'})
                break
            else:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': 'Error'})
                break
        return result
    
    
    
    def parse_node(self, input: str | list[Node]):
        logger.info(f'Parsing input "{input}"')
        table, _ = self.dump_table()
        
        if isinstance(input, str):
            input = [Node(Symbol(x)) for x in input.split()]
        input += [Node(Symbol(END_OF_INPUT))]
        result = []
        
        state_stack = [next(iter(table))]
        symbol_stack = [Node(Symbol(END_OF_INPUT))]
        input_index = 0
        
        while True:
            try:
                action = table[state_stack[-1]][input[input_index].symbol]
            except:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': 'Unknown symbol'})
                available_symbols = list(table[state_stack[-1]].keys())
                def show_node(node: Node):
                    if node.value is not None:
                        return node.value
                    return node.symbol
                error_context = f'{" ".join([str(show_node(x)) for x in input[input_index-5:input_index+5]])}'
                # logger.error(f'Unknown symbol "{input[input_index].symbol}" at index {input_index}, context: "{error_context}"\ndid you mean "{[x for x in available_symbols if x in self._terminals and x != Symbol(END_OF_INPUT)]}" \n| available symbols: {available_symbols}')
                raise ValueError(f'Unknown symbol "{input[input_index].symbol}" at index {input_index}, context: "{error_context}"\ndid you mean "{[x for x in available_symbols if x in self._terminals and x != Symbol(END_OF_INPUT)]}" \n| available symbols: {available_symbols}', input_index)
                break
            
            if action.action == Action.SHIFT:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': f'Shift {action.value}'})
                state_stack.append(action.value)
                symbol_stack.append(input[input_index])
                input_index += 1
            elif action.action == Action.REDUCE:
                production = action.value
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': f'Reduce {production}'})
                
                popped_node = []
                new_node = Node(production.head)
                new_node.set_production(production)
                if production.body == [Symbol(EPSILON)]:
                    epsilon_node = Node(Symbol(EPSILON))
                    epsilon_node.parent = new_node
                    new_node.children = [epsilon_node]
                else:
                    for _ in range(len(production.body)):
                        state_stack.pop()
                        popped_node.append(symbol_stack.pop())
                    popped_node.reverse()
                    new_node.children = popped_node
                for node in popped_node:
                    node.parent = new_node
                symbol_stack.append(new_node)
                
                state_stack.append(table[state_stack[-1]][symbol_stack[-1].symbol].value)
            elif action.action == Action.ACCEPT:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': 'Accept'})
                break
            else:
                result.append({'state': state_stack.copy(), 'symbol': symbol_stack.copy(), 'input': input[input_index:], 'action': 'Error'})
                break
        logger.debug('Parse result:')
        logger.debug(',\n'.join([str(x) for x in result]))
        logger.info(f'Parsing completed')
        return result, symbol_stack[1:]
    
    def dump_table(self):
        logger.error('Method not implemented')
        return
    
    def get_first_set(self):
        return self._first.copy()  
    
    def get_follow_set(self):
        return self._follow.copy()

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