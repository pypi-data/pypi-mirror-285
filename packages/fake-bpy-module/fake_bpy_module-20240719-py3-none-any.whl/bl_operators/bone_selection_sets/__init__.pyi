import typing
import collections.abc
import typing_extensions
import bpy.types

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class POSE_OT_selection_set_add(_PoseModeOnlyMixin, bpy.types.Operator):
    """Operator only available for objects of type armature in pose mode."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_add_and_assign(_PoseModeOnlyMixin, bpy.types.Operator):
    """Operator only available for objects of type armature in pose mode."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_assign(_PoseModeOnlyMixin, bpy.types.Operator):
    """Operator only available for objects of type armature in pose mode."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

    def invoke(self, context, event):
        """

        :param context:
        :param event:
        """
        ...

class POSE_OT_selection_set_copy(
    _PoseModeOnlyMixin, _NeedSelSetMixin, bpy.types.Operator
):
    """Operator only available if the armature has a selected selection set."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_delete_all(_PoseModeOnlyMixin, bpy.types.Operator):
    """Operator only available for objects of type armature in pose mode."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_deselect(
    _PoseModeOnlyMixin, _NeedSelSetMixin, bpy.types.Operator
):
    """Operator only available if the armature has a selected selection set."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_move(
    _PoseModeOnlyMixin, _NeedSelSetMixin, bpy.types.Operator
):
    """Operator only available if the armature has a selected selection set."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
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

class POSE_OT_selection_set_paste(_PoseModeOnlyMixin, bpy.types.Operator):
    """Operator only available for objects of type armature in pose mode."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_remove(
    _PoseModeOnlyMixin, _NeedSelSetMixin, bpy.types.Operator
):
    """Operator only available if the armature has a selected selection set."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_remove_bones(_PoseModeOnlyMixin, bpy.types.Operator):
    """Operator only available for objects of type armature in pose mode."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_select(
    _PoseModeOnlyMixin, _NeedSelSetMixin, bpy.types.Operator
):
    """Operator only available if the armature has a selected selection set."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class POSE_OT_selection_set_unassign(
    _PoseModeOnlyMixin, _NeedSelSetMixin, bpy.types.Operator
):
    """Operator only available if the armature has a selected selection set."""

    bl_description: typing.Any
    bl_idname: typing.Any
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

    def execute(self, context):
        """

        :param context:
        """
        ...

class SelectionEntry(bpy.types.PropertyGroup):
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

class SelectionSet(bpy.types.PropertyGroup):
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

class _PoseModeOnlyMixin:
    """Operator only available for objects of type armature in pose mode."""

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

class _NeedSelSetMixin(_PoseModeOnlyMixin):
    """Operator only available if the armature has a selected selection set."""

    @classmethod
    def poll(cls, context):
        """

        :param context:
        """
        ...

def register(): ...
def unregister(): ...
