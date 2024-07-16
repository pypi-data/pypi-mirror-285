import argparse

import griddle
import noiftimer
import printbuddies
import younotyou

from .pathier import Pathier, Pathish, Pathy

__all__ = ["Pathier", "Pathy", "Pathish"]


@noiftimer.time_it()
def sizeup():
    """Print the sub-directories and their sizes of the current working directory."""
    parser = argparse.ArgumentParser("sizeup")
    parser.add_argument(
        "-i",
        "--ignore",
        nargs="*",
        default=[],
        type=str,
        help="Directory patterns to ignore.",
    )
    args = parser.parse_args()
    matcher = younotyou.Matcher(exclude_patterns=args.ignore)
    sizes: dict[str, int] = {}
    folders = [
        folder
        for folder in Pathier.cwd().iterdir()
        if folder.is_dir() and str(folder) in matcher
    ]
    print(f"Sizing up {len(folders)} directories...")
    for folder in printbuddies.track(folders, "Scanning directories"):
        try:
            sizes[folder.name] = folder.size
        except Exception as e:
            pass
    total_size = sum(sizes[folder] for folder in sizes)
    size_list = [
        (folder, Pathier.format_bytes(sizes[folder]))
        for folder in sorted(list(sizes.keys()), key=lambda f: sizes[f], reverse=True)
    ]
    print(griddle.griddy(size_list, ["Dir", "Size"]))
    print(f"Total size of '{Pathier.cwd()}': {Pathier.format_bytes(total_size)}")


__version__ = "1.5.4"
