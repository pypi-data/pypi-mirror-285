import typing
import collections.abc
import typing_extensions
import bpy.types
import bpy_extras.io_utils
import bpy_extras.object_utils

GenericType1 = typing.TypeVar("GenericType1")
GenericType2 = typing.TypeVar("GenericType2")

class IMAGE_OT_convert_to_mesh_plane(TextureProperties_MixIn, MaterialProperties_MixIn):
    """Convert selected reference images to textured mesh plane"""

    bl_idname: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any
    t: typing.Any

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

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_material_config(self, context):
        """

        :param context:
        """
        ...

    def draw_texture_config(self, context):
        """

        :param context:
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

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """Returns the value of the custom property assigned to key or default
        when not found (matches Python's dictionary function of the same name).

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

    def invoke(self, context, _event):
        """

        :param context:
        :param _event:
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
        """

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

class IMAGE_OT_import_as_mesh_planes(
    TextureProperties_MixIn,
    bpy_extras.io_utils.ImportHelper,
    bpy_extras.object_utils.AddObjectHelper,
    MaterialProperties_MixIn,
):
    """Create mesh plane(s) from image files with the appropriate aspect ratio"""

    AXIS_MODES: typing.Any
    axis_id_to_vector: typing.Any
    bl_idname: typing.Any
    bl_label: typing.Any
    bl_options: typing.Any
    bl_rna: typing.Any
    id_data: typing.Any
    t: typing.Any

    def align_plane(self, context, plane):
        """Pick an axis and align the plane to it

        :param context:
        :param plane:
        """
        ...

    def align_update_callback(self, _context):
        """

        :param _context:
        """
        ...

    def apply_image_options(self, image):
        """

        :param image:
        """
        ...

    def apply_material_options(self, material, slot):
        """

        :param material:
        :param slot:
        """
        ...

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

    def check(self, _context):
        """

        :param _context:
        """
        ...

    def compute_plane_size(self, context, img_spec):
        """Given the image size in pixels and location, determine size of plane

        :param context:
        :param img_spec:
        """
        ...

    def create_image_plane(self, context, name, img_spec):
        """

        :param context:
        :param name:
        :param img_spec:
        """
        ...

    def draw(self, context):
        """

        :param context:
        """
        ...

    def draw_import_config(self, _context):
        """

        :param _context:
        """
        ...

    def draw_material_config(self, context):
        """

        :param context:
        """
        ...

    def draw_spatial_config(self, _context):
        """

        :param _context:
        """
        ...

    def draw_texture_config(self, context):
        """

        :param context:
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

    def execute(self, context):
        """

        :param context:
        """
        ...

    def get(self):
        """Returns the value of the custom property assigned to key or default
        when not found (matches Python's dictionary function of the same name).

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

    def import_images(self, context):
        """

        :param context:
        """
        ...

    def invoke(self, context, _event):
        """

        :param context:
        :param _event:
        """
        ...

    def invoke_popup(self, context, confirm_text=""):
        """

        :param context:
        :param confirm_text:
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

    def poll(self, context):
        """

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

    def single_image_spec_to_plane(self, context, img_spec):
        """

        :param context:
        :param img_spec:
        """
        ...

    def type_recast(self):
        """Return a new instance, this is needed because types
        such as textures can be changed at runtime.

                :return: a new instance of this object with the type initialized again.
        """
        ...

    def update_size_mode(self, _context):
        """If sizing relative to the camera, always face the camera

        :param _context:
        """
        ...

    def values(self):
        """Returns the values of this objects custom properties (matches Python's
        dictionary function of the same name).

                :return: custom property values.
        """
        ...

class ImageSpec:
    """ImageSpec(image, size, frame_start, frame_offset, frame_duration)"""

    frame_duration: typing.Any
    frame_offset: typing.Any
    frame_start: typing.Any
    image: typing.Any
    size: typing.Any

    def count(self, value):
        """Return number of occurrences of value.

        :param value:
        """
        ...

    def index(self, value, start=0, stop=9223372036854775807):
        """Return first index of value.Raises ValueError if the value is not present.

        :param value:
        :param start:
        :param stop:
        """
        ...

class MaterialProperties_MixIn:
    def draw_material_config(self, context):
        """

        :param context:
        """
        ...

class TextureProperties_MixIn:
    t: typing.Any

    def draw_texture_config(self, context):
        """

        :param context:
        """
        ...

def apply_texture_options(self_, texture, img_spec): ...
def auto_align_nodes(node_tree):
    """Given a shader node tree, arrange nodes neatly relative to the output node."""

    ...

def center_in_camera(camera, ob, axis=(1, 1)):
    """Center object along specified axis of the camera"""

    ...

def clean_node_tree(node_tree):
    """Clear all nodes in a shader node tree except the output.Returns the output node"""

    ...

def compute_camera_size(context, center, fill_mode, aspect):
    """Determine how large an object needs to be to fit or fill the camera's field of view."""

    ...

def create_cycles_material(self_, context, img_spec, name): ...
def create_cycles_texnode(self_, node_tree, img_spec): ...
def find_image_sequences(files):
    """From a group of files, detect image sequences.This returns a generator of tuples, which contain the filename,
    start frame, and length of the detected sequence

    """

    ...

def get_input_nodes(node, links):
    """Get nodes that are a inputs to the given node"""

    ...

def get_ref_object_space_coord(ob): ...
def get_shadeless_node(dest_node_tree):
    """Return a "shadeless" cycles/EEVEE node, creating a node group if nonexistent"""

    ...

def load_images(
    filenames, directory, force_reload=False, frame_start=1, find_sequences=False
):
    """Wrapper for bpy_extras.image_utils.load_image.Loads a set of images, movies, or even image sequences
    Returns a generator of ImageSpec wrapper objects later used for texture setup

    """

    ...

def offset_planes(planes, gap, axis):
    """Offset planes from each other by gap amount along a _local_ vector axisFor example, offset_planes([obj1, obj2], 0.5, Vector(0, 0, 1)) will place
    obj2 0.5 blender units away from obj1 along the local positive Z axis.This is in local space, not world space, so all planes should share
    a common scale and rotation.

    """

    ...
