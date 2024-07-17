import random
from .membrane import *
import re
import copy

class PSystem:

    def __init__(self, H=None, V:list=[], base_struct="[1]1", m_objects={0:''}, m_plasmids=None, m_rules={0:{}}, p_rules={0:[]}, i0=1):
        """PSystem class constructor.

        Args:
            H (dict, optional): Plasmids' alphabet and its rules. Defaults to None.
            V (list, optional): System's alphabet. Defaults to [].
            base_struct (str, optional): Initial system's structure. Defaults to "[1]1".
            m_objects (dict, optional): Membranes' objects | key:int = memb_id, value:str = memb_objects. Defaults to {0:''}.
            m_plasmids (dict, optional): Membranes' plasmids. Defaults to None.
            m_rules (dict, optional): Membranes' rules | key:int = memb_id, value:dict = memb_rules. Defaults to {0:{}}.
            p_rules (dict, optional): Rules priority in each membrane | key:int = memb_id, value:list = memb_priority. Defaults to {0:[]}.
            i0 (int, optional): Output membrane. Defaults to 1.
        """      
        self.alphabet = set(V)
        self.membranes = {}
        self.out_region = i0

        struct = base_struct.replace("[", ' ')
        struct = struct.replace("]", ' ')
        struct = struct.split()
        struct = [int(i) for i in struct]

        # preparar por si no se trabaja con plásmidos que no de ningún tipo de error
        if H == None:
            self.plasmids = {}
            m_plasmids = {i: set() for i in range(int(max(struct)) + 1)}
        else:
            self.plasmids = H

        # en el caso de que no le pasemos a alguna membrana los plasmidos, los inicializa a sin plásmidos
        if len(m_plasmids.keys()) != int(max(struct)) + 1:
            for i in range(int(max(struct)) + 1):
                m_plasmids[i] = m_plasmids.get(i, set())

        # en el caso de que no le pasemos a alguna membrana los objetos, los inicializa a sin objetos
        if len(m_objects.keys()) != int(max(struct)) + 1:
            for i in range(int(max(struct)) + 1):
                m_objects[i] = m_objects.get(i, '')
        
        # en el caso de que no le pasemos a alguna membrana las reglas, las inicializa a sin reglas
        if len(m_rules.keys()) != int(max(struct)) + 1:
            for i in range(int(max(struct)) + 1):
                m_rules[i] = m_rules.get(i, {})

        # en el caso de que no le pasemos a alguna membrana las prioridades, los inicializa a sin prioridades
        if len(p_rules.keys()) != int(max(struct)) + 1:
            for i in range(int(max(struct)) + 1):
                p_rules[i] = p_rules.get(i, [])

        # genera la estructura dada
        self._gen_struct(struct, m_objects, m_plasmids, m_rules, p_rules)

    def _gen_struct(self, struct, m_objects, m_plasmids, m_rules, p_rules):
        """Creates system structure.

        Args:
            struct (str): Initial structure
            m_objects (dict): Membrane's objects | key:int = memb_id, value:str = memb_objects
            m_plasmids (dict): Membrane's plasmids | key:int = memb_id, value:set = plasmids set
            m_rules (dict): Membrane's rules | key:int = memb_id, value:dict = memb_rules
            p_rules (dict): Rules priority in each membrane | key:int = memb_id, value:list = memb_priority
        """

        self.membranes[0] = self.membranes.get(0, Membrane(V=self.alphabet, id=0, parent=None, objects=m_objects[0], plasmids=m_plasmids[0], rules=m_rules[0], p_rules=p_rules[0]))

        open = [struct[0]]    # variable que indica en qué membrana estamos generando (permite comprobar a la vez que se va generando que la estructura inicial sea correcta)
        id = int(open[0])      # identificador de la membrana abierta
        # creamos entrada para la primera membrana con sus parametros correspondientes
        self.membranes[0].add_child(id)
        self.membranes[id] = self.membranes.get(id, Membrane(V=self.alphabet, id=id, parent=0, objects=m_objects[id], plasmids=m_plasmids[id], rules=m_rules[id], p_rules=p_rules[id]))
        # recorremos todas las posiciones del array de estructura 
        for m in struct[1:]:
            # print(open)
            # si nos encontramos con un numero diferente al anterior significa que se trata de una membrana hija
            if m != open[-1] and m not in open[:-1]:
                # añadimos un hijo a la membrana padre
                self.membranes[int(open[-1])].add_child(int(m))
                id = int(m) # actualizamos el identificador
                # creamos la membrana hija con sus parametros correspondientes
                memb = Membrane(V=self.alphabet, id=id, parent=int(open[-1]), objects=m_objects[id], plasmids=m_plasmids[id], rules=m_rules[id], p_rules=p_rules[id])
                # añadimos la membrana al diccionario de mebranas
                self.membranes[id] = self.membranes.get(id, memb)
                # añadimos a la variable auxiliar la membrana hija que se ha abierto
                open += [m]
            
            # si ya estaba abierta y no es la ultima abierta error por cerrar una membrana que no es la última abierta
            elif m in open[:-1]:
                raise NameError('Incorrect membrane structure 1')
            # si es el mismo numero 'cerramos' la membrana
            else:
                open = open[:-1]

        # en el caso de que sea una estructura incorrecta (creo que podría haber error cuando '123231')
        if open != []:
            raise NameError('Incorrect membrane structure 2')

    def steps(self, n=1, verbose=False):
        """Evolve the system n steps or until finish

        Args:
            n (int, optional): Number of steps to evolve. Defaults to 1.
            verbose (bool, optional): if verbose = True, prints system's structure in each step. Default to False.
        """
        cont = n
        feasible_rules = self.get_feasible_rules()
        while cont > 0 and feasible_rules != None:
            if verbose: 
                self.print_system()
                print("\n--------------------------------------------------------------------------------------------\n")
            self.evolve(feasible_rules, verbose)
            feasible_rules = self.get_feasible_rules()
            cont -= 1
        return self.to_dict()
        # self.print_system()
        
    def while_evolve(self, verbose=False):
        """Evolve the system until finish

        Args:
            verbose (bool, optional): if verbose = True, prints system's structure in each step. Default to False.
        """
        if verbose: print()
        feasible_rules = self.get_feasible_rules()
        while feasible_rules != None:
            if verbose: 
                self.print_system()
                print("\n--------------------------------------------------------------------------------------------\n")
            self.evolve(feasible_rules, verbose)
            feasible_rules = self.get_feasible_rules()
        if verbose:
            self.print_system()
            print("\n============================================================================================\n")
        # objectos tras aplicar todas las iteraciones posibles en la región de salida
        # print(sorted(self.membranes[self.out_region].objects.items()))
        return self.to_dict()

    def _struct_rule(self, memb_id, rule_id):
        """Divides the rule into left hand side and right hand side, gives format to the rule to be feasible to apply in the system

        Args:
            memb_id (int): Membrane's id
            rule_id (int|str): Rule's id

        Returns:
            membs_lhs: List of the parts of the lhs rule divided by membranes
            membs_rhs: List of the parts of the rhs rule divided by membranes
        """
        if type(rule_id) == int:
            lhs, rhs =  self.membranes[memb_id].rules[rule_id]
        else:
            plasmid_id = re.findall(r'(P_[a-z0-9]+)_[0-9]+', rule_id)[0]
            lhs, rhs =  self.plasmids[plasmid_id][rule_id]
        
        # divide la parte izquierda por membranas si hay una regla de multiple membrana ej. "P1P2ac[P3b[d]2[e]3]1"
        match = re.search(r'(?m)^((?:(?!\[).)*)(.*)', lhs)
        if match:
            lhs, childs_lhs = match.group(1), match.group(2)
            membs_lhs = [(lhs, memb_id)]
            if childs_lhs != "":
                match = re.sub(r'\[([^\[\]]*)\](\d*)', "", childs_lhs)
                match2 = re.findall(r'\[([^\[\]]*)\](\d*)', childs_lhs)
                if match:
                    match = re.findall(r'\[([^\[\]]*)\](\d*)', match)
                else:
                    match = []

                aux = match + match2
                for i in range(len(aux)):
                    aux[i] = (aux[i][0], int(aux[i][1]))

                membs_lhs += aux

        # divide la parte derecha por membranas si hay una regla de multiple membrana ej. "P2P3b[P1ac[e]2[d]3]1"
        match = re.search(r'(?m)^((?:(?!\[).)*)(.*)', rhs)
        if match:
            rhs, childs_rhs = match.group(1), match.group(2)
            membs_rhs = [(rhs, memb_id)]
            
            if childs_rhs != "":
                match = re.sub(r'\[([^\[\]]*)\](\d*)', "", childs_rhs)
                match2 = re.findall(r'\[([^\[\]]*)\](\d*)', childs_rhs)
                if match:
                    match = re.findall(r'\[([^\[\]]*)\](\d*)', match)
                else:
                    match = []

                aux = match + match2
                for i in range(len(aux)):
                    aux[i] = (aux[i][0], int(aux[i][1]))

                membs_rhs += aux

        return sorted(membs_lhs, key=lambda x: x[1]), sorted(membs_rhs, key=lambda x: x[1])

    def evolve(self, feasible_rules, verbose=False):
        """Makes an iteration on the system choosing a random membrane to apply its rules.

        Args:
            feasible_rules (tuple): System's feasible rules | (memb_id:int, rules_set:list)
            verbose (bool, optional): if verbose = True, prints system's structure in each step. Default to False.
        """
        to_dissolve = set()
        # selección de una membrana aleatoria dentro de las posibles con reglas factibles
        for memb_id, f_rules in feasible_rules.items():
            for rule_id in f_rules:
                membs_lhs, membs_rhs = self._struct_rule(memb_id, rule_id)       
                # máximo numero de iteraciones posibles para la regla (minimo numero de objetos en la membrana a los que afecta la regla dividido el numero de ocurrencias en la parte izquierda de la regla)
                max_possible_i = self._max_possible_iter(membs_lhs)

                # printea membrana y regla
                if verbose: 
                    if memb_id == 0:

                        if type(rule_id) == int:
                            print(f"enviroment | n_times: {max_possible_i} -> rule '{rule_id}':  {self.membranes[memb_id].rules[rule_id]}")
                        else:
                            plasmid_id = re.findall(r'(P_[a-z0-9]+)_[0-9]+', rule_id)[0]
                            print(f"enviroment | n_times: {max_possible_i} -> rule '{rule_id}':  {self.plasmids[plasmid_id][rule_id]}")

                    else:
                        if type(rule_id) == int:
                            print(f"membrane: {memb_id} | n_times: {max_possible_i} -> rule '{rule_id}':  {self.membranes[memb_id].rules[rule_id]}")
                        else:
                            plasmid_id = re.findall(r'(P_[a-z0-9]+)_[0-9]+', rule_id)[0]
                            print(f"membrane: {memb_id} | n_times: {max_possible_i} -> rule '{rule_id}':  {self.plasmids[plasmid_id][rule_id]}")

                dissolve = self._apply_rule(membs_lhs, membs_rhs, max_possible_i)
                to_dissolve.update(dissolve)

        for memb_id in to_dissolve:
            self._dissolve(memb_id)

    def _dissolve(self, memb_id):
        """Apply the necessary transformations to dissolve membrane with id memb_id.

        Args:
            memb_id (int): Membrane's id
        """
        parent_id = self.membranes[memb_id].parent

        # si existe membrana padre  
        if parent_id != None:
            # añade los objetos de la membrana a disolver en la membrana padre
            for obj in self.alphabet:
                value = self.membranes[memb_id].objects[obj]
                self.membranes[parent_id].objects[obj] = self.membranes[parent_id].objects.get(obj, 0) + value
            # añade los plasmidos de la membrana a disolver en la membrana padre
            self.membranes[parent_id].plasmids.update(self.membranes[parent_id].plasmids)
        # eliminamos el hijo disuelto de la membrana padre
        self.membranes[parent_id].remove_child(memb_id)
        # como se ha disuelto la membrana, las membranas hijas de la disuelta pasan a ser hijas de la membrana padre
        for child in self.membranes[memb_id].childs:
            self.membranes[parent_id].add_child(child) 
        # eliminamos la entrada a la membrana disuelta
        self.membranes.pop(memb_id)

    def _max_possible_iter(self, membs_lhs):
        """Return the maximum number of possible interations for a given rule. It only needs the left hand side of the rule to check it.

        Args:
            membs_lhs (list): List of the parts of the lhs rule divided by membranes

        Returns:
            int: Maximum number of possible interations
        """
        max_iters = []

        for lhs_aux, memb_id in membs_lhs:
            match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", lhs_aux)
            if match != []:
                lhs_aux = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", lhs_aux)  # obtiene el string de objetos

            lhs = re.findall(r"([a-z]|[A-Z]\d+)", lhs_aux)

            aux = [int(obj/lhs.count(s)) for s, obj in self.membranes[memb_id].objects.items() if s in lhs]
            aux = min(aux) if aux != [] else 1
            max_iters.append(aux)

        return min(max_iters)

    def _apply_rule(self, membs_lhs, membs_rhs, max_possible_i):
        """Apply rule max_possible_i iterations.

        Args:
            membs_lhs: List of the parts of the lhs rule divided by membranes
            membs_rhs: List of the parts of the rhs rule divided by membranes
            max_possible_i (int): Maximum number of possible interations

        Returns:
            bool: returns if the rule dissolves the membrane
        """

        for lhs_aux, memb_id in membs_lhs:

            match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", lhs_aux)
            if match != []:
                lhs_aux = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", lhs_aux)  # obtiene el string de objetos
                plasmids_lhs = match # guarda en una lista los plasmidos
            else:
                plasmids_lhs = [] # si no habia plasmidos lista vacia

            # se quitan los plasmidos que antes estaban en la membrana
            if plasmids_lhs != []:
                self.membranes[memb_id].plasmids.difference_update(plasmids_lhs)

            lhs = re.findall(r"([a-z]|[A-Z]\d+)", lhs_aux)

            # recorremos la parte izquierda y se quitan los objetos recorridos del diccionario de objectos de la membrana
            for obj in lhs:
                if obj != ",":
                    self.membranes[memb_id].objects[obj] = self.membranes[memb_id].objects[obj] - max_possible_i

        dissolve = set()
        for rhs_aux, memb_id in membs_rhs:
            # de la membrana elegida sacamos el id de la membrana padre 
            parent_id = self.membranes[memb_id].parent
            
            # separa parte derecha en objetos objetos y plasmidos
            match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", rhs_aux)
            if match != []:
                rhs_aux = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", rhs_aux)  # obtiene el string de objetos
                plasmids_rhs = match # guarda en una lista los plasmidos
            else:
                plasmids_rhs = [] # si no habia plasmidos lista vacia

            if plasmids_rhs != []:
                # añadir a la membrana los plásmidos
                self.membranes[memb_id].plasmids.update(plasmids_rhs)

            # rhs = re.findall(r"([a-z])(\d+)", rhs_aux)
            rhs = re.findall(r"([a-z]|[A-Z]\d+|\.)(\d+)?", rhs_aux)

            # recorremos la parte derecharule_id de la regla      
            for obj, operation in rhs:
                # if operation == None:
                if operation == '':
                    # en el caso de que sea un punto disolvemos membrana
                    if obj == '.':   # disolver
                        dissolve.add(memb_id)
                    else:
                        self.membranes[memb_id].objects[obj] = self.membranes[memb_id].objects[obj] + max_possible_i
                # si es 0 -> out
                elif operation == '0':
                    # si tiene padre la membrana | si no tiene padre no se añade en ningún sitio
                    if parent_id != None:
                        # saca a la membrana padre el objeto
                        self.membranes[parent_id].objects[obj] = self.membranes[parent_id].objects[obj] + max_possible_i
                else:
                    # si se encuentra el id entre los id de las membranas hijas
                    if int(operation) in self.membranes[memb_id].childs:
                        # añade objeto a la membrana hija
                        self.membranes[int(operation)].objects[obj] = self.membranes[int(operation)].objects[obj] + max_possible_i
        
        return dissolve

    def get_feasible_rules(self):
        """Get feasible rules from all membranes in the system.

        Returns:
            list: List of membranes and their feasible rules
        """
        promising = collections.defaultdict(set)
        for memb_id in self.membranes.keys():
            promising[memb_id] = set(self._get_memb_promising_rules(memb_id))

        all_f_rules = list(self._solve_conflicts(promising))
        # print(all_f_rules)
        feasible = random.choice(all_f_rules) if all_f_rules != [] else {}

        for _, rules in feasible.items():
            if len(rules) > 0:
                return feasible
        return None

    def _get_memb_promising_rules(self, memb_id):
        """Get promising rules from membrane with id = memb_id

        Args:
            memb_id (int): Membrane's id

        Returns:
            list: List of promising rules from membrane with id = memb_id
        """
        if memb_id == 0:
            rules = self.membranes[memb_id].rules
        else:
            rules = self.membranes[memb_id].rules
            for pr in self.membranes[memb_id].plasmids:
                rules = rules | self.plasmids[pr]
        
        applicable_rules = [r for r in rules if self._is_applicable(memb_id, r)]   # recoge todas las reglas que se pueden aplicar
        promising = []
        for r in applicable_rules:
            # comprueba las prioridades de las reglas
            cond = True
            for r1, r2 in self.membranes[memb_id].p_rules:
                if r2 == r and self._is_applicable(memb_id, r1):
                    cond = False
            if cond: promising.append(r)

        return promising

    def _solve_conflicts(self, promising):
        """Solve the conflicts with the rules in a rules' list

        Args:
            promising (list): combination of a possible rules

        Yields:
            Each yield is a feasible combination of rules that can be applied all at once at least one time
            
        """
        conflictive = collections.defaultdict(set)
        feasible = copy.deepcopy(promising)

        for memb_id_1, rules1 in promising.items():
            for memb_id_2, rules2 in promising.items():
                for r1 in rules1:
                    for r2 in rules2:
                        if (memb_id_1, r1) != (memb_id_2, r2):
                            key, memb2 = self._conflict(memb_id_1, memb_id_2, r1, r2)
                            if key != None and memb2 != None:
                                conflictive[(key, memb2)].add((memb_id_1, r1))
                                conflictive[(key, memb2)].add((memb_id_2, r2))
                                if r1 in feasible[memb_id_1]: feasible[memb_id_1].remove(r1)
                                if r2 in feasible[memb_id_2]: feasible[memb_id_2].remove(r2)
                                break

        def is_promising(sol, memb_id_1, rule):
            for memb_id_2, rules in sol.items():
                for r in rules:
                    if self._conflict(memb_id_1, memb_id_2, rule, r): return False
            return True

        def backtracking(sol, cont):
            # if es completo
            if cont == len(conflictive.keys()):
                for key, rules in feasible.items():
                    sol[key].update(rules)
                yield sol
            else:
                # ramificar
                for key, rules in conflictive.items():
                    for memb_id, rule in rules:
                        # if prometedor
                        if is_promising(sol, memb_id, rule):
                            sol[memb_id].add(rule)
                            yield from backtracking(copy.deepcopy(sol), cont + 1)
                            sol[memb_id].remove(rule) 

        yield from backtracking(collections.defaultdict(set), 0)

    def _conflict(self, m_id_1, m_id_2, rule1, rule2):
        """Checks if two rules have conflicts like 'a'-> 'b' and 'ab' -> 'b', both need an 'a' to be apply

        Args:
            m_id_1 (int): Membrane's id of the first rule
            m_id_2 (int): Membrane's id of the second rule
            rule1 (int): first rule to compare
            rule2 (int): second rule to compare

        Returns:
            str: first alphabet element where is the conflict
            int: membrane's id where the character conflicts
        """
        membs_lhs1, membs_rhs1 = self._struct_rule(m_id_1, rule1)
        membs_lhs2, membs_rhs2 = self._struct_rule(m_id_2, rule2)

        for lhs1, memb_id_1 in membs_lhs1:
            for lhs2, memb_id_2 in membs_lhs2:
                if memb_id_1 == memb_id_2:

                    match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", lhs1)
                    if match != []:
                        lhs1 = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", lhs1)  # obtiene el string de objetos
                        plasmids_lhs1 = match # guarda en una lista los plasmidos
                    else:
                        plasmids_lhs1 = [] # si no habia plasmidos lista vacia

                    match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", lhs2)
                    if match != []:
                        lhs2 = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", lhs2)  # obtiene el string de objetos
                        plasmids_lhs2 = match # guarda en una lista los plasmidos
                    else:
                        plasmids_lhs2 = [] # si no habia plasmidos lista vacia

                    plasmids_min_len, plasmids_max_len = (plasmids_lhs1, plasmids_lhs2) if len(plasmids_lhs1) <= len(plasmids_lhs2) else (plasmids_lhs2, plasmids_lhs1)

                    for p in plasmids_min_len:
                        if p in plasmids_max_len:
                            return p, memb_id_1

                    lhs_min_len, lhs_max_len = (lhs1, lhs2) if len(lhs1) <= len(lhs2) else (lhs2, lhs1)

                    for a in lhs_min_len:
                        if a in lhs_max_len:
                            return a, memb_id_1

            
        return None, None

    def _is_applicable(self, memb_id, rule_id):
        """Checks if a rule can be applied

        Args:
            memb_id (int): Membrane's id  
            rule_id (int): rule to check

        Returns:
            boolean: if the can be applied to the system or not
        """
        membs_lhs, membs_rhs = self._struct_rule(memb_id, rule_id)

        for lhs_aux, memb_id in membs_lhs:

            match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", lhs_aux)
            if match != []:
                lhs_aux = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", lhs_aux)  # obtiene el string de objetos
                plasmids_lhs = match # guarda en una lista los plasmidos
            else:
                plasmids_lhs = [] # si no habia plasmidos lista vacia

            lhs = re.findall(r"([a-z]|[A-Z]\d+)", lhs_aux)

            # para cada plasmido en la regla comprueba si se encuentra en los plásmidos que pueden entrar a la membrana
            for p in plasmids_lhs:
                if p not in self.membranes[memb_id].plasmids:
                    return False
            
            # para cada objeto de la parte izquierda comprueba que tiene suficientes como para sustituirlos
            for obj in self.alphabet:
                if self.membranes[memb_id].objects[obj] < lhs.count(obj):
                    return False
                
        for rhs_aux, memb_id in membs_rhs:

            # separa parte derecha en objetos objetos y plasmidos
            match = re.findall(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", rhs_aux)
            if match != []:
                rhs_aux = re.sub(r"P_[a-z0-9]+(?=,)|P_[a-z0-9]+$", "", rhs_aux)  # obtiene el string de objetos
                plasmids_rhs = match # guarda en una lista los plasmidos
            else:
                plasmids_rhs = [] # si no habia plasmidos lista vacia

            for p in plasmids_rhs:
                aux = self.accessible_plasmids(memb_id)
                if p not in aux and p not in self.membranes[memb_id].plasmids:
                    return False

            rhs = re.findall(r"([a-z]|[A-Z]\d+)(\d+)?", rhs_aux)

            # para los objetos de la parte derecha comprueba que sean del alfabeto
            for obj, memb in rhs:
                if memb != '' and int(memb) not in self.membranes[memb_id].childs and memb != '0':
                    return False
                if obj not in self.membranes[memb_id].rhs_alphabet:
                    return False

        return True

    def accessible_plasmids(self, memb_id):
        """Return the plasmids that could go into the membrane with id = memb_id.

        Args:
            memb_id (int): Membrane's id  

        Returns:
            set: Set of the plasmids that could go into the membrane memb_id
        """
        parent_id = self.membranes[memb_id].parent
        if parent_id != None:
            accessible_plasmids = copy.deepcopy(self.membranes[parent_id].plasmids)
        else:
            accessible_plasmids = set()

        for child in self.membranes[memb_id].childs:
            accessible_plasmids.update(self.membranes[child].plasmids)

        return accessible_plasmids

    def print_system(self):
        """Print system's structure
        """
        print(self._struct_system())

    def _struct_system(self, struct='', memb_id=0):
        """Recursive function that returns system's structure.

        Args:
            struct (str, optional): Acumulative structure to do it in a recursive way. Defaults to ''.
            id (int, optional): Membrane's id . Defaults to 1.

        Returns:
            str: Generate a more visual form of the system
        """
        if self.plasmids != {}:
            if memb_id == 0:
                env_objects = ''
                env_plasmids = ''
                for obj, n in sorted(self.membranes[memb_id].objects.items()):
                    env_objects += obj*n
                for p in sorted(self.membranes[memb_id].plasmids):
                    env_plasmids += p

                struct = f" '{env_plasmids}' '{env_objects}' "

                struct += self._struct_system(struct, memb_id=1)
            else:
                objects = ''
                plasmids = ''
                for obj, n in sorted(self.membranes[memb_id].objects.items()):
                    objects += obj*n
                for p in sorted(self.membranes[memb_id].plasmids):
                    plasmids += p
                struct = f" [{memb_id} '{plasmids}' '{objects}' "
                if self.membranes[memb_id].childs != {}:
                    for id_child in self.membranes[memb_id].childs:
                        struct += self._struct_system(struct, id_child)
                struct += f']{memb_id}'
        else:
            if memb_id != 0:
                objects = ''
                for obj, n in self.membranes[memb_id].objects.items():
                    objects += obj*n
                struct = f"[{memb_id} '{objects}' "
                if self.membranes[memb_id].childs != {}:
                    for id_child in self.membranes[memb_id].childs:
                        struct += self._struct_system(struct, id_child)
                struct += f']{memb_id}'
            else:
                struct = self._struct_system(struct, 1)
        return struct
    
    def _memb_to_dict(self, memb_id):
        """Recursive function that returns P system structured in a dictionary

        Args:
            memb_id (int): Membrane's id

        Returns:
            dict: P system dict
        """
        memb_dict = {
            "objects": {},
            # "rules": self.membranes[memb_id].rules,
        }

        if self.membranes[memb_id].plasmids != set():
            memb_dict["plasmids"] = self.membranes[memb_id].plasmids

        for obj, n in self.membranes[memb_id].objects.items():
            if n > 0:
                # if memb_id == 1 and re.match(r"L\d+", obj):
                #     memb_dict['label'] = obj
                memb_dict['objects'][obj] = n
        
        if len(self.membranes[memb_id].childs) > 0:
            memb_dict['childs'] = {}
        for child in self.membranes[memb_id].childs:
            memb_dict["childs"][child] = self._memb_to_dict(child)

        return memb_dict

    def to_dict(self):
        """Returns P system structured in a dictionary

        Returns:
            dict: P system dict
        """
        return {'environment': self._memb_to_dict(0)}