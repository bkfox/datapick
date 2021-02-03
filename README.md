# datapick
Retrieve and manipulate data based on YAML description file. Data can be loaded
from external source (http, file, ...).

Datapick provides multiple function used to handle data control flow, and
evaluate document values and functions.

Example:

```yaml
emma:
    name: goldman
    age: 23
    friends:
    - !property 0.alexander.name
    - johann
alexander:
    name: berkman
    friends: !property
      - !property 0.emma.friends.1
      - !re.replace ["johann", "johann betrayed"]
shadow: !property 0.emma
```

Will be evaluated as:

```yaml
emma:
    name: goldman
    age: 23
    friends:
    - berkman
    - johann
alexander:
    name: berkman
    friends: johann betrayed
shadow:
    name: goldman
    age: 23
    friends:
    - berkman
    - johann
```

# Features
Regarding to builtin library, there still is a lot of functions to be provided.
Since its boring to implement it, it will be on-need based -> use PR.

** Main features **
- async evaluation of function and properties, with calling arguments.
- resolve object by path (WIP: dynamic selectors).
- properties cache results

**Functions:**
- `!eval`: evaluate another document object by path with calling arguments.
- `!filters`: filter data over multiple functions.
- `!property`: dynamic value with optional filters, with cached results.
- `!python`: evaluates a python expression

**Sources:**
- `!file`: load file data.
- `!include`: another datapick yaml file (WIP).
- `!http`: load data from http resource.

**Filters:**
- `!iter.join`: join multiple iterables to data.
- `!iter.map`: call filter to dict or iterable values.
- `!iter.schema`: return dict build from data based on provided fields' filter.
- `!re.search`: regexp search.
- `!re.replace`: regexp replace.
- `!parse.json`: parse JSON document.
- `!parse.yaml`: parse YAML document (from untrusted source, disabling datapick's
  functionalities).
- `!parse.xml!`: parse XML document returning root or objects by XPath.


Note: infinite recursion is not handled yet.

# Goals
**Application:**
- load, save, run commands
- generate documentation
- plugins
- interactive command line interface

**Library:**
- well featured for data manipulation
- save data to file
- file manipulation and synchronization (using rsync)

**Sources:**
- multiple resources from one Source
- external process pipe

