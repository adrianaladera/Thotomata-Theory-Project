########################################################
# CLASS:    COP 4210-001                               #
# NAMES:    Jacob Hunt, Adriana Ladera, Brandon Phan   #
# PROJECT:  Converting Regular Expressions to NFA      #
########################################################

from enum import Enum
from collections import deque
from graphviz import Digraph
from graphviz import Graph

########################################################
#                  CLASS DECLARATIONS                  #
########################################################

# creates previous/from state with assigned transition
class State:
    def __init__(self, name_i='0', transition_i={}):
        self.name = str(name_i)
        self.transition = transition_i
        
# operator enumeration
class Operator(Enum):
    UNION = 1
    CONCATENATION = 2
    CLOSURE = 3
    LEFTPAREN = 0
    RIGHTPAREN = 0

# creating NFA with initial, created states, and final state
class NFA:
    def __init__(self, i_state, f_state):
        self.state_list = []
        self.i_state = i_state
        self.f_state = f_state
        self.state_list.append(i_state)
        self.state_list.append(f_state)  

########################################################
#                FUNCTION DECLARATIONS                 #
########################################################       

# converts regular expression to NFA
def regexToNFA(regex):
    nfas = []
    i = 0
    for char in regex:
        if char.isalpha() or char.isdigit() or char == '@':
            istate_trans = {i+1 : char}
            i_state = State(i, istate_trans)
            f_state = State(i+1)
            f_state.transition = {}
            i += 2
            nfa = NFA(i_state,f_state)
            nfas.append(nfa)
        elif char == '|': #if next character in expression is union
            nfa1 = nfas.pop()
            nfa2 = nfas.pop()
            istate_trans = {
                nfa1.i_state.name : '@', #empty transitions 
                nfa2.i_state.name : '@',
            }
            new_istate = State(i,istate_trans)
            new_fstate = State(i+1)
            i += 2
            nfa1.f_state.transition[new_fstate.name] = '@'
            nfa2.f_state.transition[new_fstate.name] = '@'
            nfa1.f_state = new_fstate
            nfa1.i_state = new_istate
            nfa1.f_state.transition = {}
            nfa1.state_list.append(new_istate)
            nfa1.state_list.append(new_fstate)
            for state in nfa2.state_list:
                nfa1.state_list.append(state)
            nfas.append(nfa1)
        elif char == '*': #if char is Kleene star
            nfa = nfas.pop()
            nfa.f_state.transition[nfa.i_state.name] = '@' #oldfinal -> oldintial
            nfa.f_state.transition[i+1] = '@' #oldfinal -> newfinal
            istate_trans = {
                nfa.i_state.name : '@', #newintial -> oldintial
                i+1 : '@' #newintial -> newfinal
            }
            new_istate = State(i,istate_trans) 
            new_fstate = State(i+1)
            i += 2 
            nfa.f_state = new_fstate 
            nfa.i_state = new_istate
            nfa.f_state.transition = {}
            nfa.state_list.append(new_istate)
            nfa.state_list.append(new_fstate)
            nfas.append(nfa)
        elif char == '?': #if char is concatenation
            nfa1 = nfas.pop()
            nfa2 = nfas.pop()
            newfstate_trans = {**nfa2.f_state.transition, **nfa1.i_state.transition}
            nfa2.f_state.transition = newfstate_trans
            nfa2.f_state = nfa1.f_state
            for state in nfa1.state_list:
                if state != nfa1.i_state:
                    nfa2.state_list.append(state)
            nfas.append(nfa2)
    return nfas.pop()

# converts regular expression to Shunting-Yard form to be converted to NFA
def shuntingYard(regex):
    queue = deque()
    stack = []
    for char in regex:
        if char.isalpha() or char.isdigit() or char == '@':
            queue.append(char)

        elif isOperator(char):
            if char == '|':
                operator = Operator.UNION
            elif char == '?':
                operator = Operator.CONCATENATION
            elif char == '*':
                operator = Operator.CLOSURE
            
            while stack and stack[-1].value >= operator.value and stack[-1] != Operator.LEFTPAREN:
                queue.append(stack.pop())

            stack.append(operator)
    
        elif char == '(':
            stack.append(Operator.RIGHTPAREN)

        elif char == ')':
            while stack[-1] != Operator.RIGHTPAREN:
                queue.append(stack.pop())
            if stack[-1] != '(':
                stack.pop()

    while stack:
        queue.append(stack.pop())
    
    outputList = list(queue)

    for index, element in enumerate(outputList):
        if element == Operator.CLOSURE:
            outputList[index] = '*'
        elif element == Operator.CONCATENATION:
            outputList[index] = '?'
        elif element == Operator.UNION:
            outputList[index] = '|'
        
    return ''.join(outputList)

# '?' represents concatenation in Shunting-Yard conversion
def insertQuestionMark(regex):
    charList = list(regex)
    prev = '#'
    for i, char in enumerate(charList):
        if (prev.isalnum() or prev == ')' or prev == '*' or char == '@') and (char.isalnum() or char == '(' or char =='@'):
            charList.insert(i, '?')
            prev = '?'
        else:
            prev = char
    return ''.join(charList)

# checks if input is one of the operators in NFA         
def isOperator(char):
    return char in ('*', '|', '?')
    
########################################################
#                   BEGINNING OF MAIN                  #
########################################################
# regex = "aab|*?b?" 
# nfa = regexToNFA(regex)

# print("\nYour regular expression", regex, "converted to NFA:\n")

# for state in nfa.state_list:
#     print(state.name, " ", state.transition)

# for state in nfa.state_list:
#     print(state.name)
#         # for key, value in state.transition.items():
#         #     print(state.name,' ',key, ' : ', value)


regex = input('Enter regular expression: ')
regex = insertQuestionMark(regex)
regex = shuntingYard(regex)
nfa = regexToNFA(regex)
print("\nYour regular expression", regex, "has been converted to an NFA.\n")

########################################################
#                   GRAPH VISUALIZATION                #
########################################################
graph = Digraph(format='jpeg')

for state in nfa.state_list:
    if state == nfa.i_state: #indicate initial state
        graph.node(state.name, shape='invtriangle')
    elif state == nfa.f_state: #final state
        graph.node(state.name, shape='doublecircle')
    else:
        graph.node(state.name)

for state in nfa.state_list:
    for edge in state.transition.items():
        graph.edge(str(state.name), str(edge[0]), str(edge[1]))

graph.graph_attr['rankdir'] = 'LR' #changing graph orientation
graph.render('regex_to_NFA', view=True) #create graph

#
