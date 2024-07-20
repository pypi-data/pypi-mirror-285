import typing
import collections.abc
import typing_extensions

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class PresetPanel:
    bl_label: typing.Any
    bl_region_type: typing.Any
    bl_space_type: typing.Any

    def draw(self, context):
        """

        :param context:
        """
        ...

    @classmethod
    def draw_menu(cls, layout, text=None):
        """

        :param layout:
        :param text:
        """
        ...

    @classmethod
    def draw_panel_header(cls, layout):
        """

        :param layout:
        """
        ...
