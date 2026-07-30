# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD Tools Append.

# MMD Tools Append is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# MMD Tools Append is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import traceback

from . import auto_load

bl_info = {
    "name": "mmd_tools_append",
    "description": "Utility tools for MMD model & scene editing by Uuu(/>ω<)/Nyaa!.",
    "author": "UuuNyaa",
    "version": (4, 5, 12),
    "blender": (4, 0, 0),
    "warning": "",
    "location": "View3D > Sidebar > MMD Tools Panel",
    "wiki_url": "https://github.com/MMD-Blender/blender_mmd_tools_append/wiki",
    "tracker_url": "https://github.com/MMD-Blender/blender_mmd_tools_append/issues",
    "support": "COMMUNITY",
    "category": "Object",
}

PACKAGE_PATH = os.path.dirname(__file__)
PACKAGE_NAME = __package__

MAX_SUPPORTED_VERSION = (4, 1, 99)

REGISTER_HOOKS = []
UNREGISTER_HOOKS = []

auto_load.init(PACKAGE_NAME)


def register():
    import bpy

    if bpy.app.version > MAX_SUPPORTED_VERSION:
        raise RuntimeError(f"This addon only supports up to Blender 4.1.x. Your Blender version ({bpy.app.version_string}) is too new.")

    auto_load.register()

    # pylint: disable=import-outside-toplevel
    from .m17n import translations_dict

    bpy.app.translations.register(PACKAGE_NAME, translations_dict)

    for hook in REGISTER_HOOKS:
        try:
            hook()
        except:  # noqa: E722
            traceback.print_exc()


def unregister():
    import bpy

    for hook in UNREGISTER_HOOKS:
        try:
            hook()
        except:  # noqa: E722
            traceback.print_exc()

    bpy.app.translations.unregister(PACKAGE_NAME)

    auto_load.unregister()
