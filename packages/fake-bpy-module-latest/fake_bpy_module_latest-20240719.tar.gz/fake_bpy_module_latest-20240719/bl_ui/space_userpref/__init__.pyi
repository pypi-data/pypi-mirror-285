import typing
import collections.abc
import typing_extensions
import bl_ui.utils
import bpy.types
import bpy_types

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class AddOnPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class AnimationPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class CenterAlignMixIn:
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    def draw(self, context):
        """

        :param context:
        """
        ...

class EditingPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class ExperimentalPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any
    url_prefix: typing.Any

    @classmethod
    def poll(cls, _context):
        """

        :param _context:
        """
        ...

class ExtensionsPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class FilePathsPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class InputPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class InterfacePanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class KeymapPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class NavigationPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class PreferenceThemeSpacePanel:
    ui_delimiters: typing.Any

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, _context):
        """

        :param _context:
        """
        ...

class PreferenceThemeWidgetColorPanel:
    bl_parent_id: typing.Any

    def draw(self, context):
        """

        :param context:
        """
        ...

class PreferenceThemeWidgetShadePanel:
    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

class SaveLoadPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class StudioLightPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class StudioLightPanelMixin:
    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_light_list(self, layout, lights):
        """

        :param layout:
        :param lights:
        """
        ...

    def draw_studio_light(self, layout, studio_light):
        """

        :param layout:
        :param studio_light:
        """
        ...

    def get_error_message(self): ...

class SystemPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class ThemeGenericClassGenerator:
    @staticmethod
    def generate_panel_classes_for_wcols(): ...
    @staticmethod
    def generate_panel_classes_from_theme_areas(): ...
    @staticmethod
    def generate_theme_area_child_panel_classes(
        parent_id, rna_type, theme_area, datapath
    ):
        """

        :param parent_id:
        :param rna_type:
        :param theme_area:
        :param datapath:
        """
        ...

class ThemePanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class USERPREF_HT_header(bpy.types.Header, bpy_types._GenericUI):
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    @staticmethod
    def draw_buttons(layout, context):
        """

        :param layout:
        :param context:
        """
        ...

class USERPREF_MT_editor_menus(bpy.types.Menu, bpy_types._GenericUI):
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

    def draw(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_MT_extensions_active_repo(bpy.types.Menu, bpy_types._GenericUI):
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

class USERPREF_MT_extensions_active_repo_remove(bpy.types.Menu, bpy_types._GenericUI):
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

class USERPREF_MT_interface_theme_presets(bpy.types.Menu, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any
    preset_operator: typing.Any
    preset_subdir: typing.Any
    preset_type: typing.Any
    preset_xml_map: typing.Any
    preset_xml_secure_types: typing.Any

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

    @staticmethod
    def post_cb(context, filepath):
        """

        :param context:
        :param filepath:
        """
        ...

    @staticmethod
    def reset_cb(_context, _filepath):
        """

        :param _context:
        :param _filepath:
        """
        ...

class USERPREF_MT_keyconfigs(bpy.types.Menu, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any
    preset_operator: typing.Any
    preset_subdir: typing.Any

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

class USERPREF_MT_save_load(bpy.types.Menu, bpy_types._GenericUI):
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

class USERPREF_MT_view(bpy.types.Menu, bpy_types._GenericUI):
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

    def draw(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_addons(bpy.types.Panel, AddOnPanel, bpy_types._GenericUI):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    @staticmethod
    def draw_addon_preferences(layout, context, addon_preferences):
        """

        :param layout:
        :param context:
        :param addon_preferences:
        """
        ...

    @staticmethod
    def draw_error(layout, message):
        """

        :param layout:
        :param message:
        """
        ...

    @staticmethod
    def is_user_addon(mod, user_addon_paths):
        """

        :param mod:
        :param user_addon_paths:
        """
        ...

class USERPREF_PT_addons_filter(bpy.types.Panel, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    bl_ui_units_x: typing.Any
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

class USERPREF_PT_animation_fcurves(
    bpy.types.Panel, AnimationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_animation_keyframes(
    bpy.types.Panel, AnimationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_animation_timeline(
    bpy.types.Panel, AnimationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_annotations(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_cursor(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_gpencil(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_misc(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_node_editor(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_objects(bpy.types.Panel, EditingPanel, bpy_types._GenericUI):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_edit_objects_duplicate_data(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_objects_new(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_sequence_editor(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_text_editor(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_edit_weight_paint(
    bpy.types.Panel, EditingPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_experimental_debugging(
    bpy.types.Panel, ExperimentalPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    url_prefix: typing.Any

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

    @classmethod
    def poll(cls, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_experimental_new_features(
    bpy.types.Panel, ExperimentalPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    url_prefix: typing.Any

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

class USERPREF_PT_experimental_prototypes(
    bpy.types.Panel, ExperimentalPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    url_prefix: typing.Any

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

class USERPREF_PT_extensions(bpy.types.Panel, ExtensionsPanel, bpy_types._GenericUI):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_extensions_repos(bpy.types.Panel, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    bl_ui_units_x: typing.Any
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

class USERPREF_PT_file_paths_applications(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_file_paths_asset_libraries(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_file_paths_data(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_file_paths_development(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_file_paths_render(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_file_paths_script_directories(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_input_keyboard(
    bpy.types.Panel, InputPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_input_mouse(
    bpy.types.Panel, InputPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_input_ndof(
    bpy.types.Panel, InputPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_input_tablet(
    bpy.types.Panel, InputPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_input_touchpad(
    bpy.types.Panel, InputPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_interface_display(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_interface_editors(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_interface_menus(
    bpy.types.Panel, InterfacePanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_interface_menus_mouse_over(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_interface_menus_pie(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_interface_statusbar(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_interface_temporary_windows(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_interface_text(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_interface_translation(
    bpy.types.Panel, InterfacePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    bl_translation_context: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    @classmethod
    def poll(cls, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_keymap(bpy.types.Panel, KeymapPanel, bpy_types._GenericUI):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_navigation_bar(bpy.types.Panel, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_navigation_fly_walk(
    bpy.types.Panel, NavigationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_navigation_fly_walk_gravity(
    bpy.types.Panel, NavigationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_header(self, context):
        """

        :param context:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_navigation_fly_walk_navigation(
    bpy.types.Panel, NavigationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_navigation_orbit(
    bpy.types.Panel, NavigationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_navigation_zoom(
    bpy.types.Panel, NavigationPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_ndof_settings(bpy.types.Panel, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    bl_ui_units_x: typing.Any
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

    @staticmethod
    def draw_settings(layout, props, show_3dview_settings=True):
        """

        :param layout:
        :param props:
        :param show_3dview_settings:
        """
        ...

class USERPREF_PT_save_preferences(bpy.types.Panel, bpy_types._GenericUI):
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_saveload_autorun(
    bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_header(self, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_saveload_blend(
    bpy.types.Panel, SaveLoadPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_saveload_file_browser(
    bpy.types.Panel, SaveLoadPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_studiolight_light_editor(
    bpy.types.Panel, StudioLightPanel, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    @staticmethod
    def opengl_light_buttons(layout, light):
        """

        :param layout:
        :param light:
        """
        ...

class USERPREF_PT_studiolight_lights(
    bpy.types.Panel, StudioLightPanel, StudioLightPanelMixin, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    sl_type: typing.Any

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

    def draw_header_preset(self, _context):
        """

        :param _context:
        """
        ...

    def get_error_message(self): ...

class USERPREF_PT_studiolight_matcaps(
    bpy.types.Panel, StudioLightPanel, StudioLightPanelMixin, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    sl_type: typing.Any

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

    def draw_header_preset(self, _context):
        """

        :param _context:
        """
        ...

    def get_error_message(self): ...

class USERPREF_PT_studiolight_world(
    bpy.types.Panel, StudioLightPanel, StudioLightPanelMixin, bpy_types._GenericUI
):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    sl_type: typing.Any

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

    def draw_header_preset(self, _context):
        """

        :param _context:
        """
        ...

    def get_error_message(self): ...

class USERPREF_PT_system_cycles_devices(
    bpy.types.Panel, SystemPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_system_memory(
    bpy.types.Panel, SystemPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_system_network(
    bpy.types.Panel, SystemPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_system_os_settings(
    bpy.types.Panel, SystemPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    @classmethod
    def poll(cls, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_system_sound(
    bpy.types.Panel, SystemPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_system_video_sequencer(
    bpy.types.Panel, SystemPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_text_editor(bpy.types.Panel, FilePathsPanel, bpy_types._GenericUI):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_header_preset(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_text_editor_presets(
    bpy.types.Panel, bl_ui.utils.PresetPanel, bpy_types._GenericUI
):
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
    id_data: typing.Any
    preset_add_operator: typing.Any
    preset_operator: typing.Any
    preset_subdir: typing.Any

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

class USERPREF_PT_theme(bpy.types.Panel, ThemePanel, bpy_types._GenericUI):
    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

class USERPREF_PT_theme_bone_color_sets(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_header(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_theme_collection_colors(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_header(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_theme_interface_gizmos(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_theme_interface_icons(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_theme_interface_state(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_theme_interface_styles(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_theme_interface_transparent_checker(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_parent_id: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_theme_strip_colors(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_header(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_theme_text_style(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    def draw_header(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_theme_user_interface(
    bpy.types.Panel, ThemePanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_header(self, _context):
        """

        :param _context:
        """
        ...

class USERPREF_PT_viewport_display(
    bpy.types.Panel, ViewportPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_viewport_quality(
    bpy.types.Panel, ViewportPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_viewport_selection(
    bpy.types.Panel, ViewportPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_PT_viewport_subdivision(
    bpy.types.Panel, ViewportPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class USERPREF_PT_viewport_textures(
    bpy.types.Panel, ViewportPanel, CenterAlignMixIn, bpy_types._GenericUI
):
    """Base class for panels to center align contents with some horizontal margin.
    Deriving classes need to implement a draw_centered(context, layout) function.
    """

    bl_context: typing.Any
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_rna: typing.Any
    bl_space_type: typing.Any
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

    def draw_centered(self, context, layout):
        """

        :param context:
        :param layout:
        """
        ...

class USERPREF_UL_asset_libraries(bpy.types.UIList, bpy_types._GenericUI):
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

    def draw_item(
        self,
        _context,
        layout,
        _data,
        item,
        icon,
        _active_data,
        _active_propname,
        _index,
    ):
        """

        :param _context:
        :param layout:
        :param _data:
        :param item:
        :param icon:
        :param _active_data:
        :param _active_propname:
        :param _index:
        """
        ...

class USERPREF_UL_extension_repos(bpy.types.UIList, bpy_types._GenericUI):
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

    def draw_item(
        self,
        _context,
        layout,
        _data,
        item,
        icon,
        _active_data,
        _active_propname,
        _index,
    ):
        """

        :param _context:
        :param layout:
        :param _data:
        :param item:
        :param icon:
        :param _active_data:
        :param _active_propname:
        :param _index:
        """
        ...

    def filter_items(self, _context, data, propname):
        """

        :param _context:
        :param data:
        :param propname:
        """
        ...

class ViewportPanel:
    bl_context: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any
