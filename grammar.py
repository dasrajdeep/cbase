import os
import re
from random import randint

class Grammar:

    def __init__(self):
        self.S = 'S'
        self.MAX_ITERS = 100
        self.g = {}
        self.source = None
        with open('cfg.txt') as f:
            self.source = f.read()
            f.close()
        self.parse()

    def __getitem__(self, key):
        if key == 'Const':
            return [str(randint(0, 100))]
        elif key == 'V':
            return ['var']
        elif key in self.g:
            return self.g[key]
        return None

    def parse(self):
        if self.source is None:
            return
        lines = self.source.splitlines()
        for line in lines:
            if line.strip() == '':
                continue
            tok = line.split('->')
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
                self.g[nterm].append(sanitized.strip())

    def get_vars(self, snippet):
        vars = re.findall("<[A-Z][a-z]*>", snippet)
        for i in range(0, len(vars)):
            vars[i] = vars[i].replace('<', '')
            vars[i] = vars[i].replace('>', '')
        return vars

    def generate(self):
        code = "<%s>" % self.S
        iter = 0
        while iter < self.MAX_ITERS:
            iter = iter + 1
            nterm = self.get_vars(code)
            #print nterm
            if len(nterm) == 0:
                break
            nterm = nterm[0]
            prod = self.__getitem__(nterm)
            #print prod
            if prod is None:
                raise Exception('Grammar is incomplete.')
            prod = prod[ randint(0, len(prod) - 1) ]
            code = code.replace("<%s>" % nterm, prod)
            #print code
        code = code.replace('nil', '')
        return code

# TEST CODE

g = Grammar()
print g.generate()