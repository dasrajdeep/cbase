import os
import re
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

# TEST CODE

g = Grammar()
concepts = {
    1: True, 
    2: False, 
    3: False, 
    4: True
}

while True:
    try:
        code = g.generate(concepts).strip()
        whole = len(g.get_vars(code)) == 0
        if code != '' and whole:
            print code
            break
    except Exception as e:
        print e