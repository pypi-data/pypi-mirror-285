import os
import pathlib

from pynwb import get_class, load_namespaces

try:
    from importlib.resources import files
except ImportError:
    # TODO: Remove when python 3.9 becomes the new minimum
    from importlib_resources import files

extension_name = "ndx-subjects"

# Get path to the namespace.yaml file with the expected location when installed not in editable mode
# __location_of_this_file = files(__name__)
__location_of_this_file = pathlib.Path(__file__)
__spec_path = __location_of_this_file.parent / "spec" / f"{extension_name}.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / f"{extension_name}.namespace.yaml"

load_namespaces(str(__spec_path))

CElegansSubject = get_class("CElegansSubject", extension_name)

__all__ = [
    "CElegansSubject",
]
