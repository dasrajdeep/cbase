import os
import re
import subprocess
import configparser
import random
from random import randint

class Grammar:

    def __init__(self):
        self.DEBUG = False
        self.CONFIG_FILE = '291.cnf'
        self.config = configparser.ConfigParser()
        if not os.path.exists(self.CONFIG_FILE):
            self.config.set('DEFAULT', 'S', 'S')
            self.config.set('DEFAULT', 'MAX_BLANKS', '10')
            self.config.set('DEFAULT', 'MAX_ITERS', '100')
            self.config.set('DEFAULT', 'PROB_DECAY', '2')
            self.config.set('DEFAULT', 'PROB_DEFAULT', '5')
            self.config.set('DEFAULT', 'PRETTIFIER_PATH', '/opt/local/bin/uncrustify')
            with open(self.CONFIG_FILE, 'w') as out:
                self.config.write(out)
                out.close()
        else:
            self.config.read(self.CONFIG_FILE)
        self.S = self.config.get('DEFAULT', 'S')
        self.MAX_BLANKS = int(self.config.get('DEFAULT', 'MAX_BLANKS'))
        self.MAX_ITERS = int(self.config.get('DEFAULT', 'MAX_ITERS'))
        self.PROB_DECAY = int(self.config.get('DEFAULT', 'PROB_DECAY'))
        self.PROB_DEFAULT = int(self.config.get('DEFAULT', 'PROB_DEFAULT'))
        self.PRETTIFIER_PATH = self.config.get('DEFAULT', 'PRETTIFIER_PATH')
        self.g = {}
        self.symbols = {}
        self.source = None
        with open('cfg.txt') as f:
            self.source = f.read()
            f.close()
        self.parse()

    def __getitem__(self, key):
        if key == 'Const':
            # HACK
            return [{ 'prod': str(randint(0, 100)), 'id': 0,'prod_dist': self.PROB_DEFAULT }]
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
        # HACK
        return [{ 'prod': varname, 'id': 0 ,'prod_dist': self.PROB_DEFAULT }]

    def lookup_varname(self):
        syms = self.symbols.keys()
        if len(syms) == 0:
            raise Exception('Not enough variables declared')
        # HACK
        return [{ 'prod': syms[randint(0, len(syms) - 1)], 'id': 0 ,'prod_dist': self.PROB_DEFAULT }]

    def parse(self):
        if self.source is None:
            return
        lines = self.source.splitlines()
        for line in lines:
            if line.strip() == '':
                continue
            #head = line.split('#')
            # Use this for multiple delimiters
            head = re.split('#|@',line)
            if self.DEBUG:
                print head
            
            # If it is >2 then we are doing probability productions
            if(len(head) > 2):
                # Grab the concept ID here
                id = int(head[1])

                # Grab the production distrubtion here
                prod_dist = int(head[2])
            else:
                # Grab the concept ID here
                id = int(head[1])

                # Set production distrubtion to default
                prod_dist = self.PROB_DEFAULT

            tok = head[0].split('->')
            nterm = tok[0].strip()
            if nterm not in self.g:
                self.g[nterm] = []
            prods = tok[1].split('|')
            for p in prods:
                if self.DEBUG:
                    print prods
                ##print p
                w = p.split('?')
                if self.DEBUG:
                    print len(w)
                ## This means we have a production specific weight
                if(len(w) > 1):
                    # The production weight
                    prod_dist = int(w[1])
                    p = w[0]

                vars = re.findall("[A-Z][a-z]*", p)
                sanitized = p
                vars = list(set(vars))
                for v in vars:
                    sanitized = sanitized.replace(v, "<%s>" % v)
                self.g[nterm].append({ 'prod': sanitized.strip(), 'id': id, 'prod_dist': prod_dist })
                if self.DEBUG:
                    print self.g[nterm]

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
            if self.DEBUG:
                print "nterm is", nterm
            if len(nterm) == 0:
                break
            nterm = nterm[0]
            prod = self.__getitem__(nterm)
            if prod is None:
                raise Exception("Grammar is incomplete. '%s' has no production." % nterm)
            if self.DEBUG:
                print prod

#########Weight Selection#####################################
            freq_list = []
            total_weight = 0

            for prod_index in range(0,len(prod)):
                if prod[prod_index]['prod_dist'] <= 0:
                    continue
                for i in range(0,prod[prod_index]['prod_dist']):
                    freq_list.append(prod_index)

            if self.DEBUG:
                print "prod_dist->" 
                print prod[prod_index]['prod_dist'] 
                print "freq_list->" 
                print freq_list
            #prod_index = randint(0,len(freq_list) - 1)


            #for i in range(0,len(prod)):
            #    freq_list.append(
            #    total_weight = total_weight + prod[i]["prod_dist"]
            #for i in range(0,total_weight):
            #    freq_list.append(

                #if (prod[i]["prod_dist"] > max_val):
                #    prod_select = i
                #    max_val = prod[i]["prod_dist"]
            

#            prod_select = -1
#            max_val = -1
#            for i in range(0,len(prod)):
#                if (prod[i]["prod_dist"] > max_val):
#                    prod_select = i
#                    max_val = prod[i]["prod_dist"]
#
#            if max_val < 0:
#                continue

##############################################
            rand_int = randint(0, len(freq_list) - 1)
            if self.DEBUG:
                print rand_int

            prod_index = freq_list[rand_int]
            if self.DEBUG:
                print "Prod index is -> "
                print prod_index

            #prod = prod[ randint(0, len(prod) - 1) ]
            prod = prod[prod_index]

            if prod['id'] in concepts and not concepts[prod['id']]:
                continue
            code = code.replace("<%s>" % nterm, prod['prod'], 1)
            if self.DEBUG:
                print "code is"
                print code
        code = code.replace('nil', '')
        return code

    def add_blanks(self, code, concepts):
        ctoks = re.findall("[a-z%;]+", code)
        ctokmap = {}
        for tok in ctoks:
            ctokmap[tok] = True
        count = 0
        for i in range(0, self.MAX_BLANKS):
            if randint(0, 100) % 5 == 0:
                for s in self.symbols:
                    code = code.replace(s, ' _FILL_ ', 1)
                    count = count + 1
                    if count >= self.MAX_BLANKS:
                        return code
        for nterm in self.g:
            for prod in self.g[nterm]:
                if prod['id'] in concepts and concepts[prod['id']]:
                    toks = re.findall("[a-z%;]+", prod['prod'])
                    for tok in toks:
                        if tok in ctokmap:
                            code = code.replace(tok, ' _FILL_ ', 1)
                            count = count + 1
                            if count >= self.MAX_BLANKS:
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
                result = subprocess.check_output([self.PRETTIFIER_PATH, '-c', "%s/ben.cfg.txt" % os.getcwd(), '-f', "%s/code.c" % os.getcwd()])
                return result
            except Exception as e:
                print e
                return None
        return None

    def generate_problem(self, concepts):
        source = None
        while True:
            try:
                code = self.generate(concepts).strip()
                whole = len(self.get_vars(code)) == 0
                if code != '' and whole:
                    compiles = self.compile(self.wrap_code(code))
                    if compiles:
                        source = self.prettify(code.replace(';', ";\n"))
                        break
            except:
                pass
        problem = self.add_blanks(source, concepts)
        return { 'code': source, 'problem': problem }
