# Copyright 2021 UuuNyaa <UuuNyaa@gmail.com>
# This file is part of MMD Tools Append.

import os

import bpy
from bpy.app.translations import pgettext as _

from ..utilities import get_preferences
from .assets import ASSETS, AssetUpdater
from .cache import CONTENT_CACHE


class ReloadAssetJsons(bpy.types.Operator):
    bl_idname = "mmd_tools_append.reload_asset_jsons"
    bl_label = "Reload Asset JSONs"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        ASSETS.reload()
        return {"FINISHED"}


class UpdateAssetJson(bpy.types.Operator):
    bl_idname = "mmd_tools_append.update_asset_json"
    bl_label = "Update Assets JSON"
    bl_options = {"INTERNAL"}

    repo: bpy.props.StringProperty(default=AssetUpdater.default_repo)
    query: bpy.props.StringProperty(default=AssetUpdater.default_query)
    output_json: bpy.props.StringProperty(default=AssetUpdater.default_assets_json)

    def execute(self, context):
        AssetUpdater.write_assets_json(AssetUpdater.fetch_assets_json_by_query(self.repo, self.query), self.output_json)
        return {"FINISHED"}


class UpdateDebugAssetJson(bpy.types.Operator):
    bl_idname = "mmd_tools_append.update_debug_asset_json"
    bl_label = "Update Debug Asset JSON"
    bl_options = {"INTERNAL"}

    repo: bpy.props.StringProperty(default=AssetUpdater.default_repo)
    issue_number: bpy.props.IntProperty()
    output_json: bpy.props.StringProperty(default="ZDEBUG.json")

    def execute(self, context):
        AssetUpdater.write_assets_json(AssetUpdater.fetch_assets_json_by_issue_number(self.repo, self.issue_number), self.output_json)
        return {"FINISHED"}


class DeleteDebugAssetJson(bpy.types.Operator):
    bl_idname = "mmd_tools_append.delete_debug_asset_json"
    bl_label = "Delete Debug Asset JSON"
    bl_options = {"INTERNAL"}

    delete_json: bpy.props.StringProperty(default="ZDEBUG.json")

    def execute(self, context):
        if not AssetUpdater.delete_assets_json(self.delete_json):
            self.report(type={"INFO"}, message=_("{delete_json} does not exist.").format(delete_json=self.delete_json))
            return {"CANCELLED"}

        return {"FINISHED"}


class DeleteCachedFiles(bpy.types.Operator):
    bl_idname = "mmd_tools_append.delete_cached_files"
    bl_label = "Delete Asset Cached Files"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        CONTENT_CACHE.delete_cache_folder()
        return {"FINISHED"}


class SyncAssetLibrary(bpy.types.Operator):
    bl_idname = "mmd_tools_append.sync_asset_library"
    bl_label = "Sync to Asset Library"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        ASSETS.reload()
        extracted_assets = [asset for asset in ASSETS.values() if ASSETS.is_extracted(asset.id)]

        if not extracted_assets:
            self.report(type={"WARNING"}, message="No extracted assets found to sync.")
            return {"CANCELLED"}

        # add Asset Library directory
        LIBRARY_NAME = "MMD Append Assets"
        major_version = f"asset_bl{bpy.app.version[0]}"

        addon_prefs = get_preferences()
        extract_root = addon_prefs.asset_extract_root_folder
        target_dir = os.path.join(extract_root, major_version)
        os.makedirs(target_dir, exist_ok=True)

        asset_libs = bpy.context.preferences.filepaths.asset_libraries
        lib = asset_libs.get(LIBRARY_NAME)
        if not lib:
            bpy.ops.preferences.asset_library_add(directory=target_dir)
            new_lib = asset_libs[-1]
            new_lib.name = LIBRARY_NAME
        else:
            if lib.path != target_dir:
                lib.path = target_dir

        obj_set = set()
        for asset_item in extracted_assets:
            asset = ASSETS[asset_item.id]
            thumbnail = CONTENT_CACHE.try_get_content(asset.thumbnail_url)

            obj = bpy.data.objects.new(f"{asset.id}.{asset.name}", None)
            obj["mmd_asset_id"] = asset.id
            obj.empty_display_size = 0.0
            obj.asset_mark()

            if thumbnail and thumbnail.filepath and os.path.exists(thumbnail.filepath):
                with context.temp_override(id=obj):
                    bpy.ops.ed.lib_id_load_custom_preview(filepath=thumbnail.filepath)

            obj_set.add(obj)

        if obj_set:
            bpy.data.libraries.write(
                filepath=f"{target_dir}/asset.blend",
                datablocks=obj_set,
            )
            for obj in obj_set:
                bpy.data.objects.remove(obj, do_unlink=True)

        self.report(type={"INFO"}, message="Finished syncing to Asset Library.")
        return {"FINISHED"}
