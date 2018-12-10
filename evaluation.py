import os

from grammar import *

g = Grammar()
concepts = {
    1: True, 
    2: False, 
    3: True, 
    4: True
}

def save_code(filename, code):
    with open(filename, 'w') as out:
        out.write(code)
        out.close()

result = g.generate_problem(concepts)
print "[ORIGINAL]"
print result['code']
save_code('code-prettified.c', result['code'])
print "[WITH_BLANKS]"
print result['problem']
save_code('code-blanks.c', result['problem'])