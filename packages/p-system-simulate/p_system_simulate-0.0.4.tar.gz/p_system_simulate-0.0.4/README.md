
# PSystem python library

The PSystem library allows you to create P Systems and evolve them, enabling complex simulations of these computational models.## PSystem class and its functions

## PSystem Class and Its functions
### Creating a PSystem Object

To create a PSystem object:

```python
ps = PSystem(H, V, base_struct, m_objects, m_plasmids, m_rules, p_rules, i0)
```

| Parameter | Type     | Description                | Default  |
| :-------- | :------- | :------------------------- | :------- |
| `H` | `dict` | Plasmids' alphabet and its rules. | None |
| `V` | `list` | System's alphabet. | [ ] |
| `base_struct` | `str` | Initial system's structure. | "[1]1" |
| `m_objects` | `dict` | Membrane's objects. | { 0 : '' } |
| `m_plasmids` | `dict` | Membranes' plasmids. | None |
| `m_rules` | `dict` | Membrane's rules. | { 0 : { } } |
| `p_rules` | `dict` | Rules priority in each membrane. | { 0: [ ] }|
| `i0` | `int` | Output membrane. | 1 |

### PSystem Methods

* **ps.steps(n, verbose=False):** Evolve the system n steps. If verbose is True, prints the system's structure at each step. Returns the system dictionary after applying n steps.  

* **ps.while_evolve(verbose=False):** Evolve the system until all possible iterations are finished. If verbose is True, prints the system's structure at each step. Returns the system dictionary after applying all iterations.  

* **ps.evolve(feasible_rules, verbose=False):** Evolve the system by choosing a random membrane from feasible_rules list whose items are a tuple of membrane's id and their rules to apply. If verbose is True, prints the membrane where the rules are being applied, the rules applied, and the number of times each rule has been applied.  

* **ps.get_feasible_rules():** Get feasible rules from all the membranes in the current state.  

* **ps.get_memb_feasible_rules(memb_id):** Get a combination of rules that can be applied all at once in the membrane with id memb_id.
ps.accessible_plasmids(memb_id): Get the plasmids that could go into the membrane with id memb_id.  

* **ps.print_system():** Print the system's structure.  

* **ps.to_dict():** Returns the system structure in a dictionary.  

## Membrane Class and Its functions

### Creating a Membrane Object

```python
memb = Membrane(V, id, parent, objects, plasmids, rules, p_rules)
```

| Parameter | Type     | Description                | Default  |
| :-------- | :------- | :------------------------- | :------- |
| `V` | `list` | Membrane's alphabet (same as system's) | |
| `id` | `int` | Membrane's id | |
| `parent` | `int` | Parent Membrane's id. | None |
| `objects` | `str` | Membrane's objects. | '' |
| `plasmids` | `list` | Membrane's plasmids. | [ ] |
| `rules` | `dict` | Membrane's rules. | {} |
| `p_rules` | `dict` | Rules priority in membrane. | [ ] |

### Membrane Methods

* **memb.add_child(child_id):** Add child with id child_id to the membrane.  
* **memb.remove_child(child_id):** Remove child with id child_id from the membrane.  
* **memb.add_objects(objects):** Add all the objects in objects to the membrane.  

## Examples without plasmids

### _n_ squared

A **P** System generating _n²_, _n_ >= 1

![A **P** System generating n², n >= 1](https://github.com/pablogl2002/docs_p_system_simulate/blob/main/assets/PSystem_n_squared.png?raw=true)

```python
from p_system_simulate import *

alphabet = ['a','b','x','c','f']
struct = '[1[2[3]3[4]4]2]1'
m_objects = {
    3:'af',
}

r_2 = {
    1:('x','b'),
    2:('b','bc4'),
    3:('ff','f'),
    4:('f','a.')
}

r_3 = {
    1:('a','ax'),
    2:('a','x.'),
    3:('f','ff')
}

m_rules = {
    2:r_2,
    3:r_3,
}

p_rules = {
    2:[(3,4)],
}

i0 = 4

ps = PSystem(V=alphabet, base_struct=struct, m_objects=m_objects, m_rules=m_rules, p_rules=p_rules, i0=i0)

print(ps.while_evolve(verbose=True))
```

#### Output
```terminal

[1 '' [2 '' [3 'fa' ]3[4 '' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 3 | n_times: 1 -> rule '1':  ('a', 'ax')
membrane: 3 | n_times: 1 -> rule '3':  ('f', 'ff')
[1 '' [2 '' [3 'ffxa' ]3[4 '' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 3 | n_times: 1 -> rule '1':  ('a', 'ax')
membrane: 3 | n_times: 2 -> rule '3':  ('f', 'ff')
[1 '' [2 '' [3 'ffffxxa' ]3[4 '' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 3 | n_times: 1 -> rule '1':  ('a', 'ax')
membrane: 3 | n_times: 4 -> rule '3':  ('f', 'ff')
[1 '' [2 '' [3 'ffffffffxxxa' ]3[4 '' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 3 | n_times: 1 -> rule '2':  ('a', 'x.')
membrane: 3 | n_times: 8 -> rule '3':  ('f', 'ff')
[1 '' [2 'ffffffffffffffffxxxx' [4 '' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '1':  ('x', 'b')
membrane: 2 | n_times: 8 -> rule '3':  ('ff', 'f')
[1 '' [2 'ffffffffbbbb' [4 '' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '2':  ('b', 'bc4')
membrane: 2 | n_times: 4 -> rule '3':  ('ff', 'f')
[1 '' [2 'ffffbbbb' [4 'cccc' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '2':  ('b', 'bc4')
membrane: 2 | n_times: 2 -> rule '3':  ('ff', 'f')
[1 '' [2 'ffbbbb' [4 'cccccccc' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '2':  ('b', 'bc4')
membrane: 2 | n_times: 1 -> rule '3':  ('ff', 'f')
[1 '' [2 'fbbbb' [4 'cccccccccccc' ]4]2]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '2':  ('b', 'bc4')
membrane: 2 | n_times: 1 -> rule '4':  ('f', 'a.')
[1 'abbbb' [4 'cccccccccccccccc' ]4]1

============================================================================================

{'environment': {'childs': {1: {'childs': {4: {'objects': {'c': 16}}},
                                'objects': {'a': 1, 'b': 4}}},
                 'objects': {}}}
```

### k divides n

A **P** system that checks if a number _n_ is divisible by another number _k_. 


![A **P** system deciding whether k divides n](https://github.com/pablogl2002/docs_p_system_simulate/blob/main/assets/PSystem_k_divides_n.png?raw=true)

In this case _k_ = 3 divides _n_ = 15 .

```python
from p_system_simulate import *

n = 15
k = 3

alphabet = ['a','c','x','d']
struct = '[1[2]2[3]3]1'
m_objects = {
    2:'a'*n+'c'*k+'d',
    3:'a'
}

r_1 = {
    1:('dcx','a3')
}

r_2 = {
    1:('ac','x'),
    2:('ax','c'),
    3:('d','d.')
}

m_rules = {
    1:r_1,
    2:r_2,
}

p_rules = {
    2 : [(1,3),(2,3)],
}

i0 = 3
ps = PSystem(V=alphabet, base_struct=struct, m_objects=m_objects, m_rules=m_rules, p_rules=p_rules, i0=i0)

print(ps.while_evolve(verbose=True))
```
#### Output
```terminal

[1 '' [2 'cccdaaaaaaaaaaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 3 -> rule '1':  ('ac', 'x')
[1 '' [2 'xxxdaaaaaaaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 3 -> rule '2':  ('ax', 'c')
[1 '' [2 'cccdaaaaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 3 -> rule '1':  ('ac', 'x')
[1 '' [2 'xxxdaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 3 -> rule '2':  ('ax', 'c')
[1 '' [2 'cccdaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 3 -> rule '1':  ('ac', 'x')
[1 '' [2 'xxxd' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 1 -> rule '3':  ('d', 'd.')
[1 'xxxd' [3 'a' ]3]1

============================================================================================

{'environment': {'childs': {1: {'childs': {3: {'objects': {'a': 1}}},
                                'objects': {'d': 1, 'x': 3}}},
                 'objects': {}}}
```

In this other case _k_ = 4 not divides _n_ = 15.

```terminal

[1 '' [2 'ccccdaaaaaaaaaaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '1':  ('ac', 'x')
[1 '' [2 'xxxxdaaaaaaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '2':  ('ax', 'c')
[1 '' [2 'ccccdaaaaaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule '1':  ('ac', 'x')
[1 '' [2 'xxxxdaaa' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 3 -> rule '2':  ('ax', 'c')
[1 '' [2 'cccxd' ]2[3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 1 -> rule '3':  ('d', 'd.')
[1 'cccxd' [3 'a' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '1':  ('dcx', 'a3')
[1 'cc' [3 'aa' ]3]1

============================================================================================

{'environment': {'childs': {1: {'childs': {3: {'objects': {'a': 2}}},
                                'objects': {'c': 2}}},
                 'objects': {}}}
```

## Examples with plasmids

### Arithmetical substraction. *m* - *n*

A **P** System that makes an arithmetic substraction operation between *m* and *n*.

![A **P** System doing *m* - *n*](https://github.com/pablogl2002/docs_p_system_simulate/blob/main/assets/PSystem_arithmetic_substraction.png?raw=true)

```python
from p_system_simulate import *

n = 4
m = 10

alphabet = ['a','b','c','p','q']
plasmids = {
    "P_1":{"P_1_1":('a','a0')},
    "P_2":{"P_2_1":('ab','c0')}
}
struct = '[1[2]2[3]3]1'
m_objects = {
    1:'pq',
    2:'a'*n,
    3:'b'*m
}

m_plasmids = {
    0: set(['P_1','P_2'])
}

r_0 = {
    1:("P_1[p]1","p[P_1]1"),
    2:("P_2[q]1","q[P_2]1"),
}

r_1 = {
    1:("P_1[]2","[P_1]2"),
    2:("P_2[]3","[P_2]3"),
    3:("a","a3"),
}

m_rules = {
    0:r_0,
    1:r_1,
}

i0 = 3
ps = PSystem(H=plasmids, V=alphabet, base_struct=struct, m_objects=m_objects, m_plasmids=m_plasmids, m_rules=m_rules, i0=i0)

print(ps.while_evolve(verbose=True))
```
#### Output
```terminal

 'P_1P_2' ''  [1 '' 'pq'  [2 '' 'aaaa' ]2 [3 '' 'bbbbbbbbbb' ]3]1

--------------------------------------------------------------------------------------------

enviroment | n_times: 1 -> rule '1':  ('P_1[p]1', 'p[P_1]1')
enviroment | n_times: 1 -> rule '2':  ('P_2[q]1', 'q[P_2]1')
 '' 'pq'  [1 'P_1P_2' ''  [2 '' 'aaaa' ]2 [3 '' 'bbbbbbbbbb' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '1':  ('P_1[]2', '[P_1]2')
membrane: 1 | n_times: 1 -> rule '2':  ('P_2[]3', '[P_2]3')
 '' 'pq'  [1 '' ''  [2 'P_1' 'aaaa' ]2 [3 'P_2' 'bbbbbbbbbb' ]3]1

--------------------------------------------------------------------------------------------

membrane: 2 | n_times: 4 -> rule 'P_1_1':  ('a', 'a0')
 '' 'pq'  [1 '' 'aaaa'  [2 'P_1' '' ]2 [3 'P_2' 'bbbbbbbbbb' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 4 -> rule '3':  ('a', 'a3')
 '' 'pq'  [1 '' ''  [2 'P_1' '' ]2 [3 'P_2' 'aaaabbbbbbbbbb' ]3]1

--------------------------------------------------------------------------------------------

membrane: 3 | n_times: 4 -> rule 'P_2_1':  ('ab', 'c0')
 '' 'pq'  [1 '' 'cccc'  [2 'P_1' '' ]2 [3 'P_2' 'bbbbbb' ]3]1

============================================================================================

{'environment': {'childs': {1: {'childs': {2: {'objects': {},
                                               'plasmids': {'P_1'}},
                                           3: {'objects': {'b': 6},
                                               'plasmids': {'P_2'}}},
                                'objects': {'c': 4}}},
                 'objects': {'p': 1, 'q': 1}}}
```
### Mathematical product. *m* * *n*

A **P** System that makes product operation between *m* and *n*.

![A **P** System doing *m* * *n*](https://github.com/pablogl2002/docs_p_system_simulate/blob/main/assets/PSystem_mathematic_product.png?raw=true)


```python
from p_system_simulate import *

n = 4
m = 5

alphabet = ['a','b','p','x','q','r','t','s']
plasmids = {
    "P_1":{"P_1_1":('ba','b')},
    "P_2":{"P_2_1":('a',"ab0")},
}
struct = '[1[2]2[3]3]1'
m_objects = {
    1:'p',
    2:'b' + 'a'*n,
    3:'b' + 'a'*m,
}

m_plasmids = {
    0: set(['P_1','P_2']),
}

r_0 = {
    1:("P_1[p]1","[P_1,x]1"),
    2:("P_2[x]1","[P_2,q]1"),
}

r_1 = {
    1:("P_1,q[a]2","r[P_1,a]2"),
    2:("r[P_1]2","P_1,s[]2"),
    3:("P_2,s[]3","t[P_2]3"),
    4:("t[P_2]3","P_2,q[]3"),
}

m_rules = {
    0:r_0,
    1:r_1,
}

i0 = 1
ps = PSystem(H=plasmids, V=alphabet, base_struct=struct, m_objects=m_objects, m_plasmids=m_plasmids, m_rules=m_rules, i0=i0)

print(ps.while_evolve(verbose=True))
```

#### Output
```terminal

 'P_1P_2' ''  [1 '' 'p'  [2 '' 'aaaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

enviroment | n_times: 1 -> rule '1':  ('P_1[p]1', '[P_1,x]1')
 'P_2' ''  [1 'P_1' 'x'  [2 '' 'aaaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

enviroment | n_times: 1 -> rule '2':  ('P_2[x]1', '[P_2,q]1')
 '' ''  [1 'P_1P_2' 'q'  [2 '' 'aaaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '1':  ('P_1,q[a]2', 'r[P_1,a]2')
 '' ''  [1 'P_2' 'r'  [2 'P_1' 'aaaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '2':  ('r[P_1]2', 'P_1,s[]2')
membrane: 2 | n_times: 1 -> rule 'P_1_1':  ('ba', 'b')
 '' ''  [1 'P_1P_2' 's'  [2 '' 'aaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '3':  ('P_2,s[]3', 't[P_2]3')
 '' ''  [1 'P_1' 't'  [2 '' 'aaab' ]2 [3 'P_2' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '4':  ('t[P_2]3', 'P_2,q[]3')
membrane: 3 | n_times: 5 -> rule 'P_2_1':  ('a', 'ab0')
 '' ''  [1 'P_1P_2' 'bbbbbq'  [2 '' 'aaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '1':  ('P_1,q[a]2', 'r[P_1,a]2')
 '' ''  [1 'P_2' 'bbbbbr'  [2 'P_1' 'aaab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '2':  ('r[P_1]2', 'P_1,s[]2')
membrane: 2 | n_times: 1 -> rule 'P_1_1':  ('ba', 'b')
 '' ''  [1 'P_1P_2' 'bbbbbs'  [2 '' 'aab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '3':  ('P_2,s[]3', 't[P_2]3')
 '' ''  [1 'P_1' 'bbbbbt'  [2 '' 'aab' ]2 [3 'P_2' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '4':  ('t[P_2]3', 'P_2,q[]3')
membrane: 3 | n_times: 5 -> rule 'P_2_1':  ('a', 'ab0')
 '' ''  [1 'P_1P_2' 'bbbbbbbbbbq'  [2 '' 'aab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '1':  ('P_1,q[a]2', 'r[P_1,a]2')
 '' ''  [1 'P_2' 'bbbbbbbbbbr'  [2 'P_1' 'aab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '2':  ('r[P_1]2', 'P_1,s[]2')
membrane: 2 | n_times: 1 -> rule 'P_1_1':  ('ba', 'b')
 '' ''  [1 'P_1P_2' 'bbbbbbbbbbs'  [2 '' 'ab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '3':  ('P_2,s[]3', 't[P_2]3')
 '' ''  [1 'P_1' 'bbbbbbbbbbt'  [2 '' 'ab' ]2 [3 'P_2' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '4':  ('t[P_2]3', 'P_2,q[]3')
membrane: 3 | n_times: 5 -> rule 'P_2_1':  ('a', 'ab0')
 '' ''  [1 'P_1P_2' 'bbbbbbbbbbbbbbbq'  [2 '' 'ab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '1':  ('P_1,q[a]2', 'r[P_1,a]2')
 '' ''  [1 'P_2' 'bbbbbbbbbbbbbbbr'  [2 'P_1' 'ab' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '2':  ('r[P_1]2', 'P_1,s[]2')
membrane: 2 | n_times: 1 -> rule 'P_1_1':  ('ba', 'b')
 '' ''  [1 'P_1P_2' 'bbbbbbbbbbbbbbbs'  [2 '' 'b' ]2 [3 '' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '3':  ('P_2,s[]3', 't[P_2]3')
 '' ''  [1 'P_1' 'bbbbbbbbbbbbbbbt'  [2 '' 'b' ]2 [3 'P_2' 'aaaaab' ]3]1

--------------------------------------------------------------------------------------------

membrane: 1 | n_times: 1 -> rule '4':  ('t[P_2]3', 'P_2,q[]3')
membrane: 3 | n_times: 5 -> rule 'P_2_1':  ('a', 'ab0')
 '' ''  [1 'P_1P_2' 'bbbbbbbbbbbbbbbbbbbbq'  [2 '' 'b' ]2 [3 '' 'aaaaab' ]3]1

============================================================================================

{'environment': {'childs': {1: {'childs': {2: {'objects': {'b': 1}},
                                           3: {'objects': {'a': 5, 'b': 1}}},
                                'objects': {'b': 20, 'q': 1},
                                'plasmids': {'P_2', 'P_1'}}},
                 'objects': {}}}
```

## Notation

### Parameters

Using as example a **P** system deciding whether _k_ divides _n_, which was used as example of use before:

![A **P** system deciding whether k divides n](https://github.com/pablogl2002/docs_p_system_simulate/blob/main/assets/PSystem_k_divides_n.png?raw=true)

<table>
    <thead>
        <tr>
            <th>Object</th>
            <th>Parameter</th>
            <th>In code</th>
            <th>In traditional notation</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center">PSystem <br> All membs</td>
            <td align="center">alphabet</td>
            <td align="center">['a','c','x','d']</td>
            <td align="center">{ a, c, x, d }</td>
        </tr>
        <tr>
            <td align="center">PSystem</td>
            <td align="center">struct</td>
            <td align="center">'[1[2]2[3]3]1'</td>
            <td align="center">[<sub>1</sub> [<sub>2</sub> ]<sub>2</sub> [<sub>3</sub> ]<sub>3</sub> ]<sub>1</sub></td>
        </tr>
        <tr>
            <td align="center">memb1</td>
            <td align="center">objects</td>
            <td align="center">''</td>
            <td align="center">&lambda;</td>
        </tr>
        <tr>
            <td align="center">memb2</td>
            <td align="center">objects</td>
            <td align="center">'a'*n+'c'*k+'d'</td>
            <td align="center">a<sup>n</sup>c<sup>k</sup>d</td>
        </tr>
        <tr>
            <td align="center">memb3</td>
            <td align="center">objects</td>
            <td align="center">'a'</td>
            <td align="center">a</td>
        </tr>
        <tr>
            <td align="center">memb1</td>
            <td align="center">rules</td>
            <td align="center">{ 1: ( 'dcx', 'a3' )}</td>
            <td align="center">dcx &rarr; (a, in<sub>3</sub>)</td>
        </tr>
        <tr>
            <td align="center">memb2</td>
            <td align="center">rules</td>
            <td align="center">{ 1: ( 'ac', 'x' ),<br>2: ( 'ax', 'c' ),<br>3: ( 'd', 'd.' ) }</td>
            <td align="center">r1: ac &rarr; x,<br>r2: ax &rarr; c,<br>r3: d &rarr; d&delta;</td>
        </tr>
        <tr>
            <td align="center">memb3</td>
            <td align="center">rules</td>
            <td align="center">{ }</td>
            <td align="center">&Oslash;</td>
        </tr>
        <tr>
            <td align="center">memb1</td>
            <td align="center">p_rules</td>
            <td align="center">[ ]</td>
            <td align="center">&Oslash;</td>
        </tr>
        <tr>
            <td align="center">memb2</td>
            <td align="center">p_rules</td>
            <td align="center">[ ( 1, 3 ), ( 2, 3 ) ]</td>
            <td align="center">{ r1 > r3, r2 > r3 }</td>
        </tr>
        <tr>
            <td align="center">memb3</td>
            <td align="center">p_rules</td>
            <td align="center">[ ]</td>
            <td align="center">&Oslash;</td>
        </tr>
        <tr>
            <td align="center">PSystem</td>
            <td align="center">m_rules</td>
            <td align="center">{ 1 : memb1.rules,<br>2 : memb2.rules,<br>3 : memb3.rules }</td>
            <td align="center">R<sub>1</sub>, R<sub>2</sub>, R<sub>3</sub></td>
        </tr>
        <tr>
            <td align="center">PSystem</td>
            <td align="center">p_rules</td>
            <td align="center">{ 1 : memb1.p_rules,<br>2 : memb2.p_rules,<br>3 : memb3.p_rules }</td>
            <td align="center">&rho;<sub>1</sub>, &rho;<sub>2</sub>, &rho;<sub>3</sub></td>
        </tr>
    </tbody>
</table>

### Rules

<table>
    <thead>
        <tr>
            <th>Description</th>
            <th>In code</th>
            <th>In traditional notation</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Add an object to a membrane</td>
            <td align="center">Using 2 to enter to memb2 <br> ( 'a', 'ab2' )</td>
            <td align="center">Using in<sub>2</sub> to enter to memb2 <br>a &rarr; a ( b, in<sub>2</sub> )</td>
        </tr>
        <tr>
            <td>An object will exit the membrane</td>
            <td align="center">Using 0 to exit the membrane<br>( 'a', 'a0' )</td>
            <td align="center">Using out to exit the membrane<br>a &rarr; ( a, out )</td>
        </tr>
        <tr>
            <td>Remove a membrane (dissolve)</td>
            <td align="center">Using '.' to dissolve<br>( 'b', '.' )</td>
            <td align="center">Using &delta; to dissolve <br> b &rarr; &delta;</td>
        </tr>
        <tr><td colspan=3 align="center"><b>Priority</b></td></tr>
        <tr>
            <th>Description</th>
            <th>In code</th>
            <th>In traditional notation</th>
        </tr>
        <tr>
            <td>rule1 more priority than rule2</td>
            <td align="center">( 1, 2 )</td>
            <td align="center">r1 > r2</td>
        </tr>
    </tbody>
</table>


#### Plasmids
When using plasmids in rules, they must be listed before the objects. For example, ("P_1a", "P_1a0") indicates that if the plasmid 'P_1' and an object 'a' are present in the membrane, the plasmid 'P_1' will be retained, and the object 'a' will be removed. Interactions between plasmids across different membranes are not handled in the same way as objects. However, it is possible to interact with objects in the same way as with plasmids.

#### Alternative Rule Representation with Plasmids and Multiple Membranes
This format allows for operations involving plasmids across different membranes and also supports checking across multiple membranes. To achieve this, the structure of the membranes is defined, along with the objects/plasmids within each membrane.

The structure is defined by specifying the elements in the membrane that the rule applies to, followed by opening square brackets to represent a child membrane. Inside the brackets, list the elements of the child membrane, then close the square bracket and indicate the child membrane ID.

For example:

* ("P_1q[a]2", "r[P_1a]2") means that if plasmid 'P_1' and object 'q' are in the parent membrane, and object 'a' is in child membrane 2, then object 'q' is replaced with 'r' in the parent membrane, and 'a' is removed from child membrane 2, while retaining plasmid 'P_1'.  
* A more complex example: ("P_1P_2ac[P_3b[d]2[e]3]1", "P_2P_3b[P_1ac[e]2[d]3]1").  


The best way to understand this is through an example, such as the Mathematical Product P System mentioned earlier.

![A **P** System doing *m* * *n*](https://github.com/pablogl2002/docs_p_system_simulate/blob/main/assets/PSystem_mathematic_product.png?raw=true)

<table>
    <thead>
        <tr>
            <th>Object</th>
            <th>Parameter</th>
            <th>In code</th>
            <th>In traditional notation</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td align="center">PSystem <br> All membs</td>
            <td align="center">alphabet</td>
            <td align="center">['a','b','p','x','q','r','t','s']</td>
            <td align="center">{ a, b, p, x, q, r, t, s }</td>
        </tr>
        <tr>
            <td align="center">PSystem</td>
            <td align="center">plasmids & its rules</td>
            <td align="center">{ "P_1" : { "P_1_1" : ( 'ba', 'b' ) },<br>"P_2" : { "P_2_1" : ( 'a', "ab0" ) } }</td>
            <td align="center">P_1: { ba &rarr; b } <br>P_2: { a &rarr; a, ( b, out ) } </td>
        </tr>
        <tr>
            <td align="center">PSystem</td>
            <td align="center">struct</td>
            <td align="center">'[1[2]2[3]3]1'</td>
            <td align="center">[<sub>1</sub> [<sub>2</sub> ]<sub>2</sub> [<sub>3</sub> ]<sub>3</sub> ]<sub>1</sub></td>
        </tr>
        <tr>
            <td align="center">enviroment</td>
            <td align="center">plasmids</td>
            <td align="center">[ 'P_1', 'P_2' ]</td>
            <td align="center">P_1, P_2</td>
        </tr>
        <tr>
            <td align="center">memb1</td>
            <td align="center">objects</td>
            <td align="center">'p'</td>
            <td align="center">p</td>
        </tr>
        <tr>
            <td align="center">memb2</td>
            <td align="center">objects</td>
            <td align="center">b + 'a'*n</td>
            <td align="center">b a<sup>n</sup></td>
        </tr>
        <tr>
            <td align="center">memb3</td>
            <td align="center">objects</td>
            <td align="center">b + 'a'*m</td>
            <td align="center">b a<sup>m</sup></td>
        </tr>
        <tr>
            <td align="center">enviroment</td>
            <td align="center">rules</td>
            <td align="center">{ 1 : ( "P_1[p]1", "[P_1x]1" ),<br>2 : ( "P_2[x]1", "[P_2q]1" ) }</td>
            <td align="center">P_1 [<sub>1</sub> p ]<sub>1</sub> &rarr; [<sub>1</sub> P_1x ]<sub>1</sub><br>P_2 [<sub>1</sub> x ]<sub>1</sub> &rarr; [<sub>1</sub> P_2q ]<sub>1</sub></td>
        </tr>
        <tr>
            <td align="center">memb1</td>
            <td align="center">rules</td>
            <td align="center">{ 1 : ( "P_1q[a]2", "r[P_1a]2" ),<br>2 : ( "r[P_1]2", "P_1s[]2" ),<br>3 : ( "P_2s[]3", "t[P_2]3" ),<br>4 : ( "t[P_2]3", "P_2q[]3" ) }</td>
            <td align="center">P_1q [<sub>2</sub> a ]<sub>2</sub> &rarr; r [<sub>2</sub> P_1a ]<sub>2</sub> <br>r [<sub>2</sub> P_1 ]<sub>2</sub> &rarr; P_1s [<sub>2</sub> ]<sub>2</sub><br>P_2s [<sub>3</sub> ]<sub>3</sub> &rarr; t [<sub>3</sub> P_2 ]<sub>3</sub><br>t [<sub>3</sub>P_2 ]<sub>3</sub> &rarr; P_2q [<sub>3</sub> ]<sub>3</sub></td>
        </tr>
        <tr>
            <td align="center">memb2</td>
            <td align="center">rules</td>
            <td align="center">{ }</td>
            <td align="center">&Oslash;</td>
        </tr>
        <tr>
            <td align="center">memb3</td>
            <td align="center">rules</td>
            <td align="center">{ }</td>
            <td align="center">&Oslash;</td>
        </tr>
        <tr>
            <td align="center">PSystem</td>
            <td align="center">m_rules</td>
            <td align="center">{ 0 : enviroment.rules,<br>1 : memb1.rules,<br>2 : memb2.rules,<br>3 : memb3.rules }</td>
            <td align="center">R<sub>1</sub>, R<sub>2</sub>, R<sub>3</sub></td>
        </tr>
    </tbody>
</table>

## Authors

- [Pablo García López](https://github.com/pablogl2002)