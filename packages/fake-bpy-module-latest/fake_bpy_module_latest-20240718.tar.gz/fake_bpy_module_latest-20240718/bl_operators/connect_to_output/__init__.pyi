import typing
import collections.abc
import typing_extensions
import bl_operators.node_editor.node_functions
import bpy.types

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class NODE_OT_connect_to_output(bl_operators.node_editor.node_functions.NodeEditorBase):
    bl_description: typing.Any
    bl_idname: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any

    def as_keywords(self, *, ignore=()):
        """Return a copy of the properties as a dictionary

        :param ignore:
        """
        ...

    def as_pointer(self) -> int:
        """Returns the memory address which holds a pointer to Blender's internal data

        :return: int (memory address).
        :rtype: int
        """
        ...

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

    def cleanup(self): ...
    def create_links(self, path, node, active_node_socket_id, socket_type):
        """Create links at each step in the node group path.

        :param path:
        :param node:
        :param active_node_socket_id:
        :param socket_type:
        """
        ...

    def driver_add(self) -> bpy.types.FCurve:
        """Adds driver(s) to the given property

        :return: The driver(s) added.
        :rtype: bpy.types.FCurve
        """
        ...

    def driver_remove(self) -> bool:
        """Remove driver(s) from the given property

        :return: Success of driver removal.
        :rtype: bool
        """
        ...

    @staticmethod
    def ensure_group_output(node_tree):
        """Check if a group output node exists, otherwise create it

        :param node_tree:
        """
        ...

    def ensure_viewer_socket(self, node_tree, socket_type, connect_socket=None):
        """Check if a viewer output already exists in a node group, otherwise create it

        :param node_tree:
        :param socket_type:
        :param connect_socket:
        """
        ...

    def get(self):
        """Returns the value of the custom property assigned to key or default
        when not found (matches Python's dictionary function of the same name).

        """
        ...

    def get_output_index(
        self, node, output_node, is_base_node_tree, socket_type, check_type=False
    ):
        """Get the next available output socket in the active node

        :param node:
        :param output_node:
        :param is_base_node_tree:
        :param socket_type:
        :param check_type:
        """
        ...

    @staticmethod
    def get_output_sockets(node_tree):
        """

        :param node_tree:
        """
        ...

    def has_socket_other_users(self, socket):
        """List the other users for this socket (other materials or geometry nodes groups)

        :param socket:
        """
        ...

    def id_properties_clear(self):
        """

        :return: Remove the parent group for an RNA struct's custom IDProperties.
        """
        ...

    def id_properties_ensure(self):
        """

        :return: the parent group for an RNA struct's custom IDProperties.
        """
        ...

    def id_properties_ui(self):
        """

        :return: Return an object used to manage an IDProperty's UI data.
        """
        ...

    def init_shader_variables(self, space, shader_type):
        """Get correct output node in shader editor

        :param space:
        :param shader_type:
        """
        ...

    def invoke(self, context, event):
        """

        :param context:
        :param event:
        """
        ...

    def is_property_hidden(self) -> bool:
        """Check if a property is hidden.

        :return: True when the property is hidden.
        :rtype: bool
        """
        ...

    def is_property_overridable_library(self) -> bool:
        """Check if a property is overridable.

        :return: True when the property is overridable.
        :rtype: bool
        """
        ...

    def is_property_readonly(self) -> bool:
        """Check if a property is readonly.

        :return: True when the property is readonly (not writable).
        :rtype: bool
        """
        ...

    def is_property_set(self) -> bool:
        """Check if a property is set, use for testing operator properties.

        :return: True when the property has been set.
        :rtype: bool
        """
        ...

    def is_socket_used_active_tree(self, socket):
        """Ensure used sockets in active node tree is calculated and check given socket

        :param socket:
        """
        ...

    def items(self):
        """Returns the items of this objects custom properties (matches Python's
        dictionary function of the same name).

                :return: custom property key, value pairs.
        """
        ...

    def keyframe_delete(self) -> bool:
        """Remove a keyframe from this properties fcurve.

        :return: Success of keyframe deletion.
        :rtype: bool
        """
        ...

    def keyframe_insert(self) -> bool:
        """Insert a keyframe on the property given, adding fcurves and animation data when necessary.

        :return: Success of keyframe insertion.
        :rtype: bool
        """
        ...

    def keys(self):
        """Returns the keys of this objects custom properties (matches Python's
        dictionary function of the same name).

                :return: custom property keys.
        """
        ...

    def link_leads_to_used_socket(self, link):
        """Return True if link leads to a socket that is already used in this node

        :param link:
        """
        ...

    def path_from_id(self) -> str:
        """Returns the data path from the ID to this object (string).

                :return: The path from `bpy.types.bpy_struct.id_data`
        to this struct and property (when given).
                :rtype: str
        """
        ...

    def path_resolve(self):
        """Returns the property from the path, raise an exception when not found."""
        ...

    @classmethod
    def poll(cls, context):
        """Already implemented natively for compositing nodes.

        :param context:
        """
        ...

    def poll_message_set(self):
        """Set the message to show in the tool-tip when poll fails.When message is callable, additional user defined positional arguments are passed to the message function."""
        ...

    def pop(self):
        """Remove and return the value of the custom property assigned to key or default
        when not found (matches Python's dictionary function of the same name).

        """
        ...

    def property_overridable_library_set(self) -> bool:
        """Define a property as overridable or not (only for custom properties!).

        :return: True when the overridable status of the property was successfully set.
        :rtype: bool
        """
        ...

    def property_unset(self):
        """Unset a property, will use default value afterward."""
        ...

    @staticmethod
    def remove_socket(tree, socket):
        """

        :param tree:
        :param socket:
        """
        ...

    @classmethod
    def search_connected_viewer_sockets(cls, output_node, r_sockets, index=None):
        """From an output node, recursively scan node tree for connected viewer sockets

        :param output_node:
        :param r_sockets:
        :param index:
        """
        ...

    @classmethod
    def search_viewer_sockets_in_tree(cls, tree, r_sockets):
        """Recursively get all viewer sockets in a node tree

        :param tree:
        :param r_sockets:
        """
        ...

    def type_recast(self):
        """Return a new instance, this is needed because types
        such as textures can be changed at runtime.

                :return: a new instance of this object with the type initialized again.
        """
        ...

    def values(self):
        """Returns the values of this objects custom properties (matches Python's
        dictionary function of the same name).

                :return: custom property values.
        """
        ...
