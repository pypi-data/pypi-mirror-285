import typing
import collections.abc
import typing_extensions
import nodeitems_utils

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class CompositorNodeCategory(SortedNodeCategory, nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class ShaderNodeCategory(SortedNodeCategory, nodeitems_utils.NodeCategory):
    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class SortedNodeCategory(nodeitems_utils.NodeCategory):
    def poll(self, _context):
        """

        :param _context:
        """
        ...

def group_input_output_item_poll(context): ...
def group_tools_draw(_self, layout, _context): ...
def node_group_items(context): ...
def register(): ...
def unregister(): ...
