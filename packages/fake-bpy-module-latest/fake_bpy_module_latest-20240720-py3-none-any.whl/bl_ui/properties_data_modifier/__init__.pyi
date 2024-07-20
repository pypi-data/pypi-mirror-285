import typing
import collections.abc
import typing_extensions
import bpy.types
import bpy_types

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class AddModifierMenu(bpy.types.Operator):
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

    def invoke(self, context, event):
        """

        :param context:
        :param event:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class DATA_PT_gpencil_modifiers(
    bpy.types.Panel, ModifierButtonsPanel, bpy_types._GenericUI
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

    def draw(self, _context):
        """

        :param _context:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class DATA_PT_modifiers(bpy.types.Panel, ModifierButtonsPanel, bpy_types._GenericUI):
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

    def draw(self, _context):
        """

        :param _context:
        """
        ...

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class ModifierAddMenu:
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any

    @classmethod
    def operator_modifier_add(cls, layout, mod_type):
        """

        :param layout:
        :param mod_type:
        """
        ...

class ModifierButtonsPanel:
    bl_context: typing.Any
    bl_options: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

class OBJECT_MT_modifier_add(bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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

class OBJECT_MT_modifier_add_color(
    bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI
):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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

class OBJECT_MT_modifier_add_deform(
    bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI
):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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

class OBJECT_MT_modifier_add_edit(
    bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI
):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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

class OBJECT_MT_modifier_add_generate(
    bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI
):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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

class OBJECT_MT_modifier_add_normals(
    bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI
):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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

class OBJECT_MT_modifier_add_physics(
    bpy.types.Menu, ModifierAddMenu, bpy_types._GenericUI
):
    MODIFIER_TYPES_I18N_CONTEXT: typing.Any
    MODIFIER_TYPES_TO_ICONS: typing.Any
    MODIFIER_TYPES_TO_LABELS: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
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
