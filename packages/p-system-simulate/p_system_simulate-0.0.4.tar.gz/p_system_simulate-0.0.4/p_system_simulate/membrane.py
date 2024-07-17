import re
import collections

class Membrane:

    def __init__(self, V, id:int, parent:int=None, objects:str='', plasmids=[], rules={}, p_rules=[]):
        """Membrane class constructor.

        Args:
            V (list): Membrane's alphabet (same as system's)
            id (int): Membrane's id
            parent (int, optional): Parent Membrane's id. Defaults to None.
            objects (str, optional): Membrane's objects. Defaults to ''.
            plasmids (list, optional): Membrane's plasmids. Default to [].
            rules (dict, optional): Membrane's rules | key: rule_id, value:list = tuple (lhs, rhs). Defaults to {}.
            p_rules (dict, optional): Rules priority in membrane. Defaults to [].
        """
        self.alphabet = V               # membrane's alphabet
        self.id = id                    # membrane's id
        self.parent = parent            # parent's id
        self.childs = set()             # childs' ids set list
        self.rules = rules              # rules' dict
        self.p_rules = p_rules          # rules' priority list
        self.plasmids = set(plasmids)   # plasmids' set list
        self.objects = {}               # membrane object's dict
        self.rhs_alphabet = V.copy()    # rhs rules' alphabet

        self.rhs_alphabet.add('0')  # se añade al alfabeto de la parte derecha un 0 para sacar objeto
        self.rhs_alphabet.add('.')  # se añade al alfabeto de la parte derecha un . para disolver membrana

        # se añaden los objetos iniciales a la membrana
        self._add_objects(objects)


    def add_child(self, child:int):
        """Add child to the membrane.

        Args:
            child (int): child's id
        """
        self.childs.add(child)
        self.rhs_alphabet.add(str(child))


    def remove_child(self, child:int):
        """Remove a child from the membrane.

        Args:
            child (int): child's id
        """
        self.childs.remove(child)
        self.rhs_alphabet.remove(str(child))


    def _add_objects(self, objects:str):
        """Add objects to the membranes.

        Args:
            objects (str): objects to add in the membrane
        """
        objs = re.findall(r"([a-z]|[A-Z]\d+)", objects)
        # prev_objs = self.objects
        for obj in self.alphabet:
            self.objects[obj] = self.objects.get(obj, 0)

        for obj in objs:
            self.objects[obj] = self.objects.get(obj, 0) + 1