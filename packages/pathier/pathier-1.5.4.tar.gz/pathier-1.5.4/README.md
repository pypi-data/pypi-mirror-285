# pathier

Extends the standard library pathlib.Path class.

## Installation

Install with:

```console
pip install pathier
```

## Usage

Functions the same as pathlib.Path, but with added functions and some altered default arguments.  

#### Navigation

New paths can be obtained by:  

* naming the parent with moveup()
* subtracting a number of levels from the current path
* naming the parent of the path you actually want with move_under()
* separating a relative path at a named parent with separate()
* set current working directory to path

```python
>>> from pathier import Pathier
>>> path = Pathier("C:/some/directory/to/some/file/on/the/system")
>>> path.moveup("directory")
WindowsPath('C:/some/directory')
>>> path - 3
WindowsPath('C:/some/directory/to/some/file')
>>> path.move_under("directory")
WindowsPath('C:/some/directory/to')
>>> path.separate("file")
WindowsPath('on/the/system')
>>> path.separate("file", True)
WindowsPath('file/on/the/system')
>>> path.mkcwd()
>>> Pathier.cwd()
WindowsPath('C:/some/directory/to/some/file/on/the/system')
```

#### Environment PATH Variable

Pathier objects can be added and removed from sys.path:  
(The path will only be added if it isn't already in sys.path)

```python
>>> from pathier import Pathier
>>> path = Pathier.cwd()
>>> path.in_PATH
False
>>> path.add_to_PATH(0)
>>> path.in_PATH
True
>>> path.remove_from_PATH()
>>> path.in_PATH
False
>>> path.append_to_PATH()
>>> path.in_PATH
True
```

#### Read and Write

Can dump and load toml, json, and pickle files without needed to explicityly import and call functions from the respective libraries:

```python
from pathier import Pathier
path = Pathier("some_file.toml")
content = path.loads()
path.with_suffix(".json").dumps(content, indent=2)
```

`Pathier().mkdir()` creates parent directories and doesn't throw an error if the path already exists by default.  

`Pathier().write_text()` and `Pathier().write_bytes()` will create parent directories by default if they won't exist.  

`Pathier().write_text()` will also try to cast the data to be written to a string if a TypeError is thrown.  

`Pathier().delete()` will delete a file or directory, event if that directory isn't empty.  

`Pathier().copy()` will copy a file or a directory tree to a new destination and return a Pathier object for the new path  
By default, files in the destination will not be overwritten.  

`Pathier().backup()` will create a copy of the path with `_backup` appended to the stem.
If the optional parameter, `timestamp`, is `True`, a datetime string will be added after `_backup` to prevent overwriting previous backup files.  

`Pathier().replace_strings()` takes a list of string pairs and will read the file the instance points to, replace the first of each pair with the second of each pair, and then write it back to the file.  
Essentially just condenses reading the file, using str.replace(), and then writing the new content into one function call.  

`Pathier().execute()` wraps calling `os.system()` on the path pointed to be the `Pathier` instance.  
Optional strings that should come before and after the path string can be specified with the `command` and `args` params, respectively.  
`Pathier("file.py").execute("py", "--iterations 10")` is equivalent to `os.system("py file.py --iterations 10")`  

`Pathier().append()` will append the given string to the file pointed at by the instance.  

`Pathier().join(data)` is equivalent to calling `Pathier().write_text("\n".join(data))`.  
The joining string can be specified with the `sep` parameter.  

`Pathier().split()` is equivalent to calling `Pathier().read_text().splitlines()`.  
Optionally, line endings can be kept with `Pathier().split(keepends=True)`.  

#### Stats and Comparisons

```python
>>> from pathier import Pathier
>>> p = Pathier.cwd() / "pathier.py"
>>> i = p.parent / "__init__.py"
>>> p.dob
datetime.datetime(2023, 3, 31, 18, 43, 12, 360000)
>>> p.age
8846.024934
>>> p.mod_date
datetime.datetime(2023, 3, 31, 21, 7, 30)
>>> p.mod_delta
207.488857
>>> p.size
10744
>>> p.format_bytes(p.size)
'10.74 kb'
>>> p.formatted_size
'10.74 kb'
>>> p.is_larger(i)
True
>>> p.is_older(i)
False
>>> p.modified_more_recently(i)
True
```

#### CLI Scripts

Execute `sizeup` from a terminal to get a grid of sub-directories and their sizes.

```console
P:\python\projects\pathier>sizeup
Sizing up 7 directories...
Scanning 'dist' [____________________________________________________________________________________________________________________________________________]-100.00%
+---------------+-----------+
| Dir           | Size      |
+===============+===========+
| docs          | 362.74 kb |
+---------------+-----------+
| tests         | 63.69 kb  |
+---------------+-----------+
| dist          | 61.78 kb  |
+---------------+-----------+
| src           | 50.91 kb  |
+---------------+-----------+
| .git          | 24.25 kb  |
+---------------+-----------+
| .pytest_cache | 540 bytes |
+---------------+-----------+
| .vscode       | 197 bytes |
+---------------+-----------+
Total size of 'P:\python\projects\pathier': 564.11 kb
sizeup average execution time: 37ms 895us
```
