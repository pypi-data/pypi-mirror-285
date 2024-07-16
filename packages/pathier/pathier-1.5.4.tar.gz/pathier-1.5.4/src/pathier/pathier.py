import datetime
import functools
import json
import os
import pathlib
import pickle
import shutil
import sys
import time
from typing import Any

import tomlkit
from typing_extensions import IO, Buffer, Callable, Self, Sequence


class Pathier(pathlib.Path):
    """Subclasses the standard library pathlib.Path class."""

    def __new__(
        cls,
        *args: Self | str | pathlib.Path,
        **kwargs: Any,
    ) -> Self:
        if cls is Pathier:
            cls = WindowsPath if os.name == "nt" else PosixPath
        self = cls._from_parts(args)  # type: ignore
        if not self._flavour.is_supported:  # type: ignore
            raise NotImplementedError(
                "cannot instantiate %r on your system" % (cls.__name__,)
            )
        if "convert_backslashes" in kwargs:
            self.convert_backslashes = kwargs["convert_backslashes"]
        else:
            self.convert_backslashes = True
        return self  # type: ignore

    @property
    def convert_backslashes(self) -> bool:
        """If True, when `self.__str__()`/`str(self)` is called, string representations will have double backslashes converted to a forward slash.

        Only affects Windows paths."""
        try:
            return self._convert_backslashes
        except Exception as e:
            return True

    @convert_backslashes.setter
    def convert_backslashes(self, should_convert: bool):
        self._convert_backslashes = should_convert

    def __str__(self) -> str:
        path = super().__new__(pathlib.Path, self).__str__()  # type: ignore
        if self.convert_backslashes:
            path = path.replace("\\", "/")
        return path

    # ===============================================stats===============================================
    @property
    def dob(self) -> datetime.datetime | None:
        """Returns the creation date of this file or directory as a `dateime.datetime` object."""
        return (
            datetime.datetime.fromtimestamp(self.stat().st_ctime)
            if self.exists()
            else None
        )

    @property
    def age(self) -> float | None:
        """Returns the age in seconds of this file or directory."""
        return (
            (datetime.datetime.now() - self.dob).total_seconds() if self.dob else None
        )

    @property
    def mod_date(self) -> datetime.datetime | None:
        """Returns the modification date of this file or directory as a `datetime.datetime` object."""
        return (
            datetime.datetime.fromtimestamp(self.stat().st_mtime)
            if self.exists()
            else None
        )

    @property
    def mod_delta(self) -> float | None:
        """Returns how long ago in seconds this file or directory was modified."""
        return (
            (datetime.datetime.now() - self.mod_date).total_seconds()
            if self.mod_date
            else None
        )

    @property
    def last_read_time(self) -> datetime.datetime | None:
        """Returns the last time this object made a call to `self.read_text()`, `self.read_bytes()`, or `self.open(mode="r"|"rb")`.
        Returns `None` if the file hasn't been read from.

        Note: This property is only relative to the lifetime of this `Pathier` instance, not the file itself.
        i.e. This property will reset if you create a new `Pathier` object pointing to the same file.
        """
        return (
            datetime.datetime.fromtimestamp(self._last_read_time)
            if self._last_read_time
            else None
        )

    @property
    def modified_since_last_read(self) -> bool:
        """Returns `True` if this file hasn't been read from or has been modified since the last time this object
        made a call to `self.read_text()`, `self.read_bytes()`, or `self.open(mode="r"|"rb")`.

        Note: This property is only relative to the lifetime of this `Pathier` instance, not the file itself.
        i.e. This property will reset if you create a new `Pathier` object pointing to the same file.

        #### Caveat:
        May not be accurate if the file was modified within a couple of seconds of checking this property.
        (For instance, on my machine `self.mod_date` is consistently 1-1.5s in the future from when `self.write_text()` was called according to `time.time()`.)
        """
        return (
            False
            if not self.mod_date
            or not self.last_read_time
            or self.mod_date < self.last_read_time
            else True
        )

    @property
    def size(self) -> int:
        """Returns the size in bytes of this file or directory.

        If this path doesn't exist, `0` will be returned."""
        if not self.exists():
            return 0
        elif self.is_file():
            return self.stat().st_size
        elif self.is_dir():
            return sum(file.stat().st_size for file in self.rglob("*.*"))
        return 0

    @property
    def formatted_size(self) -> str:
        """The size of this file or directory formatted with `self.format_bytes()`."""
        return self.format_bytes(self.size)

    @staticmethod
    def format_bytes(size: int) -> str:
        """Format `size` with common file size abbreviations and rounded to two decimal places.
        >>> 1234 -> "1.23 kb" """
        unit = "bytes"
        for unit in ["bytes", "kb", "mb", "gb", "tb", "pb"]:
            if unit != "bytes":
                size *= 0.001  # type: ignore
            if size < 1000 or unit == "pb":
                break
        return f"{round(size, 2)} {unit}"

    def is_larger(self, path: Self) -> bool:
        """Returns whether this file or folder is larger than the one pointed to by `path`."""
        return self.size > path.size

    def is_older(self, path: Self) -> bool | None:
        """Returns whether this file or folder is older than the one pointed to by `path`.

        Returns `None` if one or both paths don't exist."""
        return self.dob < path.dob if self.dob and path.dob else None

    def modified_more_recently(self, path: Self) -> bool | None:
        """Returns whether this file or folder was modified more recently than the one pointed to by `path`.

        Returns `None` if one or both paths don't exist."""
        return (
            self.mod_date > path.mod_date if self.mod_date and path.mod_date else None
        )

    # ===============================================navigation===============================================
    def mkcwd(self):
        """Make this path your current working directory."""
        os.chdir(self)

    @property
    def in_PATH(self) -> bool:
        """Return `True` if this path is in `sys.path`."""
        return str(self) in sys.path

    def add_to_PATH(self, index: int = 0):
        """Insert this path into `sys.path` if it isn't already there.

        #### :params:

        `index`: The index of `sys.path` to insert this path at."""
        path = str(self)
        if not self.in_PATH:
            sys.path.insert(index, path)

    def append_to_PATH(self):
        """Append this path to `sys.path` if it isn't already there."""
        path = str(self)
        if not self.in_PATH:
            sys.path.append(path)

    def remove_from_PATH(self):
        """Remove this path from `sys.path` if it's in `sys.path`."""
        if self.in_PATH:
            sys.path.remove(str(self))

    def _get_path_part_rindex(self, name: str) -> int | None:
        """Returns the index value for the last occurrence of `name` if it is in this path instance."""
        if name not in self.parts:
            raise Exception(f"{name} is not a parent of {self}")
        lastdex = len(self.parts) - 1
        rev_parts = self.parts[::-1]
        return lastdex - rev_parts.index(name)

    def moveup(self, name: str) -> Self:
        """Return a new `Pathier` object that is a parent of this instance.

        `name` is case-sensitive and raises an exception if it isn't in `self.parts`.
        >>> p = Pathier("C:/some/directory/in/your/system")
        >>> print(p.moveup("directory"))
        >>> "C:/some/directory"
        >>> print(p.moveup("yeet"))
        >>> "Exception: yeet is not a parent of C:/some/directory/in/your/system" """
        index = self._get_path_part_rindex(name)
        if index is None:
            raise Exception(f"{name} is not a parent of {self}")
        return self - (len(self.parts) - index - 1)
        return self.__class__(*(self.parts[: index + 1]))

    def __sub__(self, levels: int) -> Self:
        """Return a new `Pathier` object moved up `levels` number of parents from the current path.
        >>> p = Pathier("C:/some/directory/in/your/system")
        >>> new_p = p - 3
        >>> print(new_p)
        >>> "C:/some/directory" """
        path = self
        for _ in range(levels):
            path = path.parent
        return path

    def move_under(self, name: str) -> Self:
        """Return a new `Pathier` object such that the stem is one level below the given folder `name`.

        `name` is case-sensitive and raises an exception if it isn't in `self.parts`.
        >>> p = Pathier("a/b/c/d/e/f/g")
        >>> print(p.move_under("c"))
        >>> 'a/b/c/d'"""
        index = self._get_path_part_rindex(name)
        if index is None:
            raise Exception(f"{name} is not a parent of {self}")
        return self - (len(self.parts) - index - 2)

    def separate(self, name: str, keep_name: bool = False) -> Self:
        """Return a new `Pathier` object that is the relative child path after `name`.

        `name` is case-sensitive and raises an exception if it isn't in `self.parts`.

        #### :params:

        `keep_name`: If `True`, the returned path will start with `name`.
        >>> p = Pathier("a/b/c/d/e/f/g")
        >>> print(p.separate("c"))
        >>> 'd/e/f/g'
        >>> print(p.separate("c", True))
        >>> 'c/d/e/f/g'"""
        if name not in self.parts:
            raise Exception(f"{name} is not a parent of {self}")
        if keep_name:
            return self.__class__(*self.parts[self.parts.index(name) :])
        return self.__class__(*self.parts[self.parts.index(name) + 1 :])

    # ============================================write and read============================================
    def mkdir(self, mode: int = 511, parents: bool = True, exist_ok: bool = True):
        """Create this directory.

        Same as `Path().mkdir()` except `parents` and `exist_ok` default to `True` instead of `False`.
        """
        super().mkdir(mode, parents, exist_ok)

    def touch(self, mode: int = 438, exist_ok: bool = True):
        """Create file (and parents if necessary)."""
        self.parent.mkdir()
        super().touch(mode, exist_ok)

    def open(  # type: ignore
        self,
        mode: str = "r",
        buffering: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> IO[Any]:
        """
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        stream = super().open(mode, buffering, encoding, errors, newline)
        if "r" in mode:
            self._last_read_time = time.time()
        return stream

    def write_text(
        self,
        data: Any,
        encoding: Any | None = None,
        errors: Any | None = None,
        newline: Any | None = None,
        parents: bool = True,
    ) -> int:
        """Write data to file.

        If a `TypeError` is raised, the function  will attempt to cast `data` to a `str` and try the write again.

        If a `FileNotFoundError` is raised and `parents = True`, `self.parent` will be created.
        """
        write = functools.partial(
            super().write_text,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )
        try:
            return write(data)
        except TypeError:
            data = str(data)
            return write(data)
        except FileNotFoundError:
            if parents:
                self.parent.mkdir(parents=True)
                return write(data)
            else:
                raise
        except Exception as e:
            raise

    def write_bytes(self, data: Buffer, parents: bool = True) -> int:
        """Write bytes to file.

        #### :params:

        `parents`: If `True` and the write operation fails with a `FileNotFoundError`,
        make the parent directory and retry the write."""
        try:
            return super().write_bytes(data)
        except FileNotFoundError:
            if parents:
                self.parent.mkdir(parents=True)
                return super().write_bytes(data)
            else:
                raise
        except Exception as e:
            raise

    def append(self, data: str, new_line: bool = True, encoding: Any | None = None):
        """Append `data` to the file pointed to by this `Pathier` object.

        #### :params:

        `new_line`: If `True`, add `\\n` to `data`.

        `encoding`: The file encoding to use."""
        if new_line:
            data += "\n"
        with self.open("a", encoding=encoding) as file:
            file.write(data)

    def replace_strings(
        self,
        substitutions: Sequence[tuple[str, str]],
        count: int = -1,
        encoding: Any | None = None,
    ):
        """For each pair in `substitutions`, replace the first string with the second string.

        #### :params:

        `count`: Only replace this many occurences of each pair.
        By default (`-1`), all occurences are replaced.

        `encoding`: The file encoding to use.

        e.g.
        >>> path = Pathier("somefile.txt")
        >>>
        >>> path.replace([("hello", "yeet"), ("goodbye", "yeehaw")])
        equivalent to
        >>> path.write_text(path.read_text().replace("hello", "yeet").replace("goodbye", "yeehaw"))
        """
        text = self.read_text(encoding)
        for sub in substitutions:
            text = text.replace(sub[0], sub[1], count)
        self.write_text(text, encoding=encoding)

    def join(self, data: Sequence[str], encoding: Any | None = None, sep: str = "\n"):
        """Write a list of strings, joined by `sep`, to the file pointed at by this instance.

        Equivalent to `Pathier("somefile.txt").write_text(sep.join(data), encoding=encoding)`

        #### :params:

        `encoding`: The file encoding to use.

        `sep`: The separator to use when joining `data`."""
        self.write_text(sep.join(data), encoding=encoding)

    def split(self, encoding: Any | None = None, keepends: bool = False) -> list[str]:
        """Returns the content of the pointed at file as a list of strings, splitting at new line characters.

        Equivalent to `Pathier("somefile.txt").read_text(encoding=encoding).splitlines()`

        #### :params:

        `encoding`: The file encoding to use.

        `keepend`: If `True`, line breaks will be included in returned strings."""
        return self.read_text(encoding=encoding).splitlines(keepends)

    def json_loads(self, encoding: Any | None = None, errors: Any | None = None) -> Any:
        """Load json file."""
        return json.loads(self.read_text(encoding, errors))

    def json_dumps(
        self,
        data: Any,
        encoding: Any | None = None,
        errors: Any | None = None,
        newline: Any | None = None,
        sort_keys: bool = False,
        indent: Any | None = 2,
        default: Any | None = str,
        parents: bool = True,
    ) -> Any:
        """Dump `data` to json file."""
        self.write_text(
            json.dumps(data, indent=indent, default=default, sort_keys=sort_keys),
            encoding,
            errors,
            newline,
            parents,
        )

    def pickle_loads(self) -> Any:
        """Load pickle file."""
        return pickle.loads(self.read_bytes())

    def pickle_dumps(self, data: Any):
        """Dump `data` to pickle file."""
        self.write_bytes(pickle.dumps(data))

    def toml_loads(self, encoding: Any | None = None, errors: Any | None = None) -> Any:
        """Load toml file."""
        return tomlkit.loads(self.read_text(encoding, errors)).unwrap()

    def toml_dumps(
        self,
        data: Any,
        toml_encoders: Sequence[Callable[[Any], Any]] = [str],
        encoding: Any | None = None,
        errors: Any | None = None,
        newline: Any | None = None,
        sort_keys: bool = False,
        parents: bool = True,
    ):
        """Dump `data` to toml file.

        `toml_encoders` can be a list of functions to call when a value in `data` doesn't map to `tomlkit`'s built in types.
        By default, anything that `tomlkit` can't convert will be cast to a string. Encoder order matters.
        e.g. By default any `Pathier` object in `data` will be converted to a string."""
        encoders: list[Callable[[Any], Any]] = []
        for toml_encoder in toml_encoders:
            encoder: Callable[[Any], Any] = lambda x: tomlkit.item(  # type:ignore
                toml_encoder(x)
            )
            encoders.append(encoder)
            tomlkit.register_encoder(encoder)
        try:
            self.write_text(
                tomlkit.dumps(data, sort_keys),  # type:ignore
                encoding,
                errors,
                newline,
                parents,
            )
        except Exception as e:
            raise e
        finally:
            for encoder in encoders:
                tomlkit.unregister_encoder(encoder)

    def loads(self, encoding: Any | None = None, errors: Any | None = None) -> Any:
        """Load a json, toml, or pickle file based off this path's suffix."""
        match self.suffix:
            case ".json":
                return self.json_loads(encoding, errors)
            case ".toml":
                return self.toml_loads(encoding, errors)
            case ".pickle" | ".pkl":
                return self.pickle_loads()
            case _:
                raise ValueError(
                    f"No load function exists for file type `{self.suffix}`."
                )

    def dumps(
        self,
        data: Any,
        encoding: Any | None = None,
        errors: Any | None = None,
        newline: Any | None = None,
        sort_keys: bool = False,
        indent: Any | None = None,
        default: Any | None = str,
        toml_encoders: Sequence[Callable[[Any], Any]] = [str],
        parents: bool = True,
    ):
        """Dump `data` to a json or toml file based off this instance's suffix.

        For toml files:
        `toml_encoders` can be a list of functions to call when a value in `data` doesn't map to `tomlkit`'s built in types.
        By default, anything that `tomlkit` can't convert will be cast to a string. Encoder order matters.
        e.g. By default any `Pathier` object in `data` will be converted to a string."""
        match self.suffix:
            case ".json":
                self.json_dumps(
                    data, encoding, errors, newline, sort_keys, indent, default, parents
                )
            case ".toml":
                self.toml_dumps(
                    data, toml_encoders, encoding, errors, newline, sort_keys, parents
                )
            case ".pickle" | ".pkl":
                self.pickle_dumps(data)
            case _:
                raise ValueError(
                    f"No dump function exists for file type `{self.suffix}`."
                )

    def delete(self, missing_ok: bool = True):
        """Delete the file or folder pointed to by this instance.

        Uses `self.unlink()` if a file and uses `shutil.rmtree()` if a directory."""
        if self.is_file():
            self.unlink(missing_ok)
        elif self.is_dir():
            shutil.rmtree(self)

    def copy(
        self, new_path: Self | pathlib.Path | str, overwrite: bool = False
    ) -> Self:
        """Copy the path pointed to by this instance
        to the instance pointed to by `new_path` using `shutil.copyfile`
        or `shutil.copytree`.

        Returns the new path.

        #### :params:

        `new_path`: The copy destination.

        `overwrite`: If `True`, files already existing in `new_path` will be overwritten.
        If `False`, only files that don't exist in `new_path` will be copied."""
        dst = self.__class__(new_path)
        if self.is_dir():
            if overwrite or not dst.exists():
                dst.mkdir()
                shutil.copytree(self, dst, dirs_exist_ok=True)
            else:
                files = self.rglob("*.*")
                for file in files:
                    dst = dst.with_name(file.name)
                    if not dst.exists():
                        shutil.copyfile(file, dst)
        elif self.is_file():
            if overwrite or not dst.exists():
                shutil.copyfile(self, dst)
        return dst

    def backup(self, timestamp: bool = False) -> Self | None:
        """Create a copy of this file or directory with `_backup` appended to the path stem.
        If the path to be backed up doesn't exist, `None` is returned.
        Otherwise a `Pathier` object for the backup is returned.

        #### :params:

        `timestamp`: Add a timestamp to the backup name to prevent overriding previous backups.

        >>> path = Pathier("some_file.txt")
        >>> path.backup()
        >>> list(path.iterdir())
        >>> ['some_file.txt', 'some_file_backup.txt']
        >>> path.backup(True)
        >>> list(path.iterdir())
        >>> ['some_file.txt', 'some_file_backup.txt', 'some_file_backup_04-28-2023-06_25_52_PM.txt']
        """
        if not self.exists():
            return None
        backup_stem = f"{self.stem}_backup"
        if timestamp:
            backup_stem = f"{backup_stem}_{datetime.datetime.now().strftime('%m-%d-%Y-%I_%M_%S_%p')}"
        backup_path = self.with_stem(backup_stem)
        self.copy(backup_path, True)
        return backup_path

    def execute(self, command: str = "", args: str = "") -> int:
        """Make a call to `os.system` using the path pointed to by this Pathier object.

        #### :params:

        `command`: Program/command to precede the path with.

        `args`: Any arguments that should come after the path.

        :returns: The integer output of `os.system`.

        e.g.
        >>> path = Pathier("mydirectory") / "myscript.py"
        then
        >>> path.execute("py", "--iterations 10")
        equivalent to
        >>> os.system(f"py {path} --iterations 10")"""
        return os.system(f"{command} {self} {args}")


Pathy = Pathier | pathlib.Path
Pathish = Pathier | pathlib.Path | str


class PosixPath(Pathier, pathlib.PurePosixPath):
    __slots__ = ()
    _last_read_time = None


class WindowsPath(Pathier, pathlib.PureWindowsPath):
    __slots__ = ()
    _last_read_time = None
