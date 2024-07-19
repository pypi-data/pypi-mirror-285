import ast
import logging
import os
import traceback

KNOWN_DYNAMIC_IMPORTS = {"gi", "dbus"}  # Add more as needed
SYSTEM_PACKAGES = {"dbus-python"}  # Add more as needed
REQUIREMENTS_IGNORE_LIST = {"PyGObject"}  # Add more packages as needed


def join(f):
    return os.path.join(os.path.dirname(__file__), f)


def get_all_imports(path, encoding=None, extra_ignore_dirs=None, follow_links=True):
    imports = set()
    raw_imports = set()
    candidates = []
    ignore_errors = False
    ignore_dirs = [".hg", ".svn", ".git", ".tox", "__pycache__", "env", "venv"]

    if extra_ignore_dirs:
        ignore_dirs_parsed = []
        for e in extra_ignore_dirs:
            print("ignoring dir:", e)
            ignore_dirs_parsed.append(os.path.basename(os.path.realpath(e)))
        ignore_dirs.extend(ignore_dirs_parsed)

    walk = os.walk(path, followlinks=follow_links)
    for root, dirs, files in walk:
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        candidates.append(os.path.basename(root))
        files = [fn for fn in files if os.path.splitext(fn)[1] == ".py"]

        candidates += [os.path.splitext(fn)[0] for fn in files]
        for file_name in files:
            file_name = os.path.join(root, file_name)
            print("checking imports: ", file_name)
            with open(file_name, "r", encoding=encoding) as f:
                contents = f.read()
            try:
                tree = ast.parse(contents)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for subnode in node.names:
                            raw_imports.add(subnode.name)
                    elif isinstance(node, ast.ImportFrom):
                        raw_imports.add(node.module)
            except Exception as exc:
                if ignore_errors:
                    traceback.print_exc(exc)
                    logging.warn("Failed on file: %s" % file_name)
                    continue
                else:
                    logging.error("Failed on file: %s" % file_name)
                    raise exc

    # Clean up imports
    for name in [n for n in raw_imports if n]:
        # Sanity check: Name could have been None if the import
        # statement was as ``from . import X``
        # Cleanup: We only want to first part of the import.
        # Ex: from django.conf --> django.conf. But we only want django
        # as an import.
        cleaned_name, _, _ = name.partition(".")
        imports.add(cleaned_name)

    packages = imports - (set(candidates) & imports)
    logging.debug("Found packages: {0}".format(packages))

    with open(join("stdlib"), "r") as f:
        data = {x.strip() for x in f}

    return list(packages - data)


def parse_requirements(file_):
    """Parse a requirements formatted file.

    Traverse a string until a delimiter is detected, then split at said
    delimiter, get module name by element index, create a dict consisting of
    module:version, and add dict to list of parsed modules.

    Args:
        file_: File to parse.

    Raises:
        OSerror: If there's any issues accessing the file.

    Returns:
        tuple: The contents of the file, excluding comments.
    """
    modules = []
    # For the dependency identifier specification, see
    # https://www.python.org/dev/peps/pep-0508/#complete-grammar
    delim = ["<", ">", "=", "!", "~", "@"]

    try:
        f = open(file_, "r")
    except OSError:
        logging.error("Failed on file: {}".format(file_))
        raise
    else:
        try:
            data = [x.strip() for x in f.readlines() if x != "\n"]
        finally:
            f.close()

    data = [x for x in data if x[0].isalpha()]

    for x in data:
        # Check for modules w/o a specifier.
        if not any([y in x for y in delim]):
            modules.append({"name": x, "version": None})
        for y in x:
            if y in delim:
                module = x.split(y)
                module_name = module[0]
                module_version = module[-1].replace("=", "")
                module = {"name": module_name, "version": module_version}

                if module not in modules:
                    modules.append(module)

                break

    return modules


def compare_lists(list1, list2):
    # Filter out ignored packages from the check against requirements.txt
    filtered_list2 = [item for item in list2 if item not in REQUIREMENTS_IGNORE_LIST]

    error_entries = [
        item
        for item in list1
        if item.lower()
        not in ([x.lower() for x in filtered_list2] + list(KNOWN_DYNAMIC_IMPORTS))
    ]
    warning_entries = [
        item
        for item in filtered_list2
        if item.lower() not in ([x.lower() for x in list1] + list(SYSTEM_PACKAGES))
    ]

    if not (warning_entries or  error_entries):
        print("::success:: All packages are used in requirements.txt")

    if warning_entries:
        print(
            f"::warning:: Package in requirements.txt file not used in any modules: {warning_entries}"
        )
    if error_entries:
        print(
            f"::error:: One or more packages are imported but not found in requirements.txt: {error_entries}"
        )
        exit(1)

