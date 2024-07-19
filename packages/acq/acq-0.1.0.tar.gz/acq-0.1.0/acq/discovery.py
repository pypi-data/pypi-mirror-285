import importlib
import typing
import types


def import_module_safe(module_name: str) -> typing.Optional[types.ModuleType]:
    """ Wrapper for importlib.import_module that ignores ImportError

    """

    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


def discover(
    *module_names: str,
    package_names: typing.Sequence[str] = [],
) -> typing.List[types.ModuleType]:
    """ Allows discovery of entire packages or specific modules within them """

    if not package_names:
        return list(filter(None, map(import_module_safe, module_names)))

    if not module_names:
        return discover(*package_names)

    all_module_names = []

    for package_name in package_names:
        for module_name in module_names:
            all_module_names.append(package_name + '.' + module_name)

    return discover(*all_module_names)
