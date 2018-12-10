import os
import re
import subprocess
from random import randint

class Grammar:

    def __init__(self):
        self.S = 'S'
        self.MAX_ITERS = 100
        self.g = {}
        self.symbols = {}
        self.source = None
        with open('cfg.txt') as f:
            self.source = f.read()
            f.close()
        self.parse()

    def __getitem__(self, key):
        if key == 'Const':
            return [{ 'prod': str(randint(0, 100)), 'id': 0 }]
        elif key == 'Vi':
            return self.get_varname('int')
        elif key == 'Vf':
            return self.get_varname('float')
        elif key == 'Vc':
            return self.get_varname('char')
        elif key == 'U':
            return self.lookup_varname()
        elif key in self.g:
            return self.g[key]
        return None

    def get_varname(self, type):
        varname = "var%d" % (len(self.symbols.keys()) + 1)
        self.symbols[varname] = type
        return [{ 'prod': varname, 'id': 0 }]

    def lookup_varname(self):
        syms = self.symbols.keys()
        if len(syms) == 0:
            raise Exception('Not enough variables declared')
        return [{ 'prod': syms[randint(0, len(syms) - 1)], 'id': 0 }]

    def parse(self):
        if self.source is None:
            return
        lines = self.source.splitlines()
        for line in lines:
            if line.strip() == '':
                continue
            head = line.split('#')
            id = int(head[1])
            tok = head[0].split('->')
            nterm = tok[0].strip()
            if nterm not in self.g:
                self.g[nterm] = []
            prods = tok[1].split('|')
            for p in prods:
                vars = re.findall("[A-Z][a-z]*", p)
                sanitized = p
                vars = list(set(vars))
                for v in vars:
                    sanitized = sanitized.replace(v, "<%s>" % v)
                self.g[nterm].append({ 'prod': sanitized.strip(), 'id': id })

    def get_vars(self, snippet):
        vars = re.findall("<[A-Z][a-z]*>", snippet)
        for i in range(0, len(vars)):
            vars[i] = vars[i].replace('<', '')
            vars[i] = vars[i].replace('>', '')
        return vars

    def generate(self, concepts):
        self.symbols = {}
        code = "<%s>" % self.S
        iter = 0
        while iter < self.MAX_ITERS:
            iter = iter + 1
            nterm = self.get_vars(code)
            if len(nterm) == 0:
                break
            nterm = nterm[0]
            #print "nterm:", nterm
            prod = self.__getitem__(nterm)
            #print prod
            if prod is None:
                raise Exception("Grammar is incomplete. '%s' has no production." % nterm)
            prod = prod[ randint(0, len(prod) - 1) ]
            if prod['id'] in concepts and not concepts[prod['id']]:
                continue
            code = code.replace("<%s>" % nterm, prod['prod'], 1)
            #print code
        code = code.replace('nil', '')
        return code

    def add_blanks(self, code, concepts, max_blanks):
        ctoks = re.findall("[a-z%;]+", code)
        ctokmap = {}
        for tok in ctoks:
            ctokmap[tok] = True
        count = 0
        for i in range(0, max_blanks):
            if randint(0, 100) % 5 == 0:
                for s in self.symbols:
                    code = code.replace(s, ' _FILL_ ', 1)
                    count = count + 1
                    if count >= max_blanks:
                        return code
        for nterm in self.g:
            for prod in self.g[nterm]:
                if prod['id'] in concepts and concepts[prod['id']]:
                    toks = re.findall("[a-z%;]+", prod['prod'])
                    for tok in toks:
                        if tok in ctokmap:
                            code = code.replace(tok, ' _FILL_ ', 1)
                            count = count + 1
                            if count >= max_blanks:
                                return code
        return code

    def wrap_code(self, code):
        source = "int main() { %s return 0; }" % code
        return source

    def compile(self, code):
        with open('./code.c', 'w') as out:
            out.write("\n".join(["#include <stdio.h>", "", code]))
            out.close()
            try:
                result = subprocess.check_output(['gcc', 'code.c'], stderr=subprocess.STDOUT)
                if result.strip() == '':
                    return True
            except:
                return False
        return False

    def prettify(self, code):
        with open('./code.c', 'w') as out:
            out.write("\n".join(["#include <stdio.h>", "", self.wrap_code(code)]))
            out.close()
            try:
                result = subprocess.check_output(['/opt/local/bin/uncrustify', '-c', "%s/ben.cfg.txt" % os.getcwd(), '-f', "%s/code.c" % os.getcwd()])
                return result
            except Exception as e:
                print e
                return None
        return None

# TEST CODE

g = Grammar()
concepts = {
    1: True, 
    2: False, 
    3: False, 
    4: True
}

source = None
while True:
    try:
        code = g.generate(concepts).strip()
        whole = len(g.get_vars(code)) == 0
        if code != '' and whole:
            compiles = g.compile(g.wrap_code(code))
            if compiles:
                source = g.prettify(code.replace(';', ";\n"))
                print source
                break
    except Exception as e:
        print e

problem = g.add_blanks(source, concepts, 10)
print problem