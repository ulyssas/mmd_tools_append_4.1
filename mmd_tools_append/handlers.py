# Copyright 2026 MMD Tools Append authors
# This file is part of MMD Tools Append.

import bpy

from .asset_search.actions import register_drop


class AppendHandlers:
    @staticmethod
    @bpy.app.handlers.persistent
    def depsgraph_update_handler(_scene, depsgraph: bpy.types.Depsgraph):

        register_drop(depsgraph)

    @staticmethod
    def register():
        bpy.app.handlers.depsgraph_update_post.append(AppendHandlers.depsgraph_update_handler)

    @staticmethod
    def unregister():
        bpy.app.handlers.depsgraph_update_post.remove(AppendHandlers.depsgraph_update_handler)
