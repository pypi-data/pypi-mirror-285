import typing
import collections.abc
import typing_extensions
import bpy.types
import bpy_types

from . import anim
from . import asset_shelf
from . import generic_ui_list
from . import node_add_menu
from . import node_add_menu_compositor
from . import node_add_menu_geometry
from . import node_add_menu_shader
from . import node_add_menu_texture
from . import properties_animviz
from . import properties_collection
from . import properties_constraint
from . import properties_data_armature
from . import properties_data_bone
from . import properties_data_camera
from . import properties_data_curve
from . import properties_data_curves
from . import properties_data_empty
from . import properties_data_gpencil
from . import properties_data_grease_pencil
from . import properties_data_lattice
from . import properties_data_light
from . import properties_data_lightprobe
from . import properties_data_mesh
from . import properties_data_metaball
from . import properties_data_modifier
from . import properties_data_pointcloud
from . import properties_data_shaderfx
from . import properties_data_speaker
from . import properties_data_volume
from . import properties_freestyle
from . import properties_grease_pencil_common
from . import properties_mask_common
from . import properties_material
from . import properties_material_gpencil
from . import properties_object
from . import properties_output
from . import properties_paint_common
from . import properties_particle
from . import properties_physics_cloth
from . import properties_physics_common
from . import properties_physics_dynamicpaint
from . import properties_physics_field
from . import properties_physics_fluid
from . import properties_physics_geometry_nodes
from . import properties_physics_rigidbody
from . import properties_physics_rigidbody_constraint
from . import properties_physics_softbody
from . import properties_render
from . import properties_scene
from . import properties_texture
from . import properties_view_layer
from . import properties_workspace
from . import properties_world
from . import space_clip
from . import space_console
from . import space_dopesheet
from . import space_filebrowser
from . import space_graph
from . import space_image
from . import space_info
from . import space_nla
from . import space_node
from . import space_outliner
from . import space_properties
from . import space_sequencer
from . import space_spreadsheet
from . import space_statusbar
from . import space_text
from . import space_time
from . import space_toolsystem_common
from . import space_toolsystem_toolbar
from . import space_topbar
from . import space_userpref
from . import space_view3d
from . import space_view3d_toolbar
from . import temp_anim_layers
from . import utils

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class UI_MT_button_context_menu(bpy.types.Menu, bpy_types._GenericUI):
    """UI button context menu definition. Scripts can append/prepend this to
    add own operators to the context menu. They must check context though, so
    their items only draw in a valid context and for the correct buttons.
    """

    bl_idname: typing.Any
    bl_label: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any

    def bl_rna_get_subclass(self) -> bpy.types.Struct:
        """

        :return: The RNA type or default when not found.
        :rtype: bpy.types.Struct
        """
        ...

    def bl_rna_get_subclass_py(self) -> typing.Any:
        """

        :return: The class or default when not found.
        :rtype: typing.Any
        """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

class UI_MT_list_item_context_menu(bpy.types.Menu, bpy_types._GenericUI):
    """UI List item context menu definition. Scripts can append/prepend this to
    add own operators to the context menu. They must check context though, so
    their items only draw in a valid context and for the correct UI list.
    """

    bl_idname: typing.Any
    bl_label: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any

    def bl_rna_get_subclass(self) -> bpy.types.Struct:
        """

        :return: The RNA type or default when not found.
        :rtype: bpy.types.Struct
        """
        ...

    def bl_rna_get_subclass_py(self) -> typing.Any:
        """

        :return: The class or default when not found.
        :rtype: typing.Any
        """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

class UI_UL_list(bpy.types.UIList, bpy_types._GenericUI):
    bl_rna: typing.Any
    id_data: typing.Any

    def bl_rna_get_subclass(self): ...
    def bl_rna_get_subclass_py(self): ...
    @staticmethod
    def filter_items_by_name(
        pattern, bitflag, items, propname="name", flags=None, reverse=False
    ):
        """

        :param pattern:
        :param bitflag:
        :param items:
        :param propname:
        :param flags:
        :param reverse:
        """
        ...

    @classmethod
    def sort_items_by_name(cls, items, propname="name"):
        """

        :param items:
        :param propname:
        """
        ...

    @staticmethod
    def sort_items_helper(sort_data, key, reverse=False):
        """

        :param sort_data:
        :param key:
        :param reverse:
        """
        ...

def register(): ...
def translation_update(_): ...
def unregister(): ...
