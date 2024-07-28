# Copyright 2018-2021 The glTF-Blender-IO authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from pathlib import Path
import bpy

def find_draco_dll_in_module(library_name: str) -> Path:
    bpy_path = Path(bpy.__file__).resolve()
    bpy_dir = bpy_path.parents[4]
    lib_dir = bpy_dir / 'lib'
    
    draco_path = lib_dir / library_name
    if draco_path.exists():
        return draco_path

    return None
    
def dll_path() -> Path:
    """
    Get the DLL path depending on the underlying platform.
    :return: DLL path.
    """
    lib_name = 'extern_draco'
    blender_root = Path(bpy.app.binary_path).parent
    python_lib = Path(f'{bpy.app.version[0]}.{bpy.app.version[1]}/python/lib')
    python_version = f'python{sys.version_info[0]}.{sys.version_info[1]}'

    path = os.environ.get('BLENDER_EXTERN_DRACO_LIBRARY_PATH')
    if path is not None:
        return Path(path)

    library_name = {
        'win32': f'{lib_name}.dll',
        'linux': f'lib{lib_name}.so',
        'darwin': f'lib{lib_name}.dylib'
    }.get(sys.platform)

    path = find_draco_dll_in_module(library_name)
    if path is not None:
        return path

    path = {
        'win32': blender_root / python_lib / 'site-packages',
        'linux': blender_root / python_lib / python_version / 'site-packages',
        'darwin': blender_root.parent / 'Resources' / python_lib / python_version / 'site-packages'
    }.get(sys.platform)

    if path is None or library_name is None:
        print(f'WARNING: Unsupported platform {sys.platform}, Draco mesh compression is unavailable')
        return None

    return path / library_name


def dll_exists(quiet=False) -> bool:
    """
    Checks whether the DLL path exists.
    :return: True if the DLL exists.
    """
    path = dll_path()
    exists = path.exists() and path.is_file()
    if quiet is False:
        if exists:
            print('INFO', 'Draco mesh compression is available, use library at %s' % dll_path().absolute())
        else:
            print('ERROR', 'Draco mesh compression is not available because library could not be found at %s' % dll_path().absolute())
    return exists
