# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Moritz's command set, shared by the Moritz MCP server (one tool per command), moritz-cli
(`moritz-cli command run <name>`) and its headless commands.

Each command runs inside Moritz and returns a JSON-able dict. Commands that change the scene go
through the same operators as the interface and end in one undo step, named after the command, so
Ctrl+Z takes back what an assistant did. Objects are named the way the Scene Explorer shows them.

This module imports `bpy` only inside the commands: the MCP server reads the command list (names,
descriptions, parameters) from this file without Moritz running.
"""

__all__ = (
    "COMMANDS",
    "describe",
    "run",
)

import contextlib
from collections.abc import Callable
from typing import Any

REQUIRED = object()

# JSON schema types of the parameters.
_TYPES = {"string", "integer", "number", "boolean", "array", "object"}

# name -> {"fn", "description", "params": [(name, type, default, description)], "read_only", "label"}
COMMANDS: dict[str, dict[str, Any]] = {}


def command(
        name: str,
        label: str,
        params: tuple[tuple[str, str, Any, str], ...] = (),
        read_only: bool = False,
) -> Callable[[Callable[..., dict[str, Any]]], Callable[..., dict[str, Any]]]:
    """Register a command. `label` names its undo step; the docstring is its description."""
    for param in params:
        assert param[1] in _TYPES, param

    def wrap(fn: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
        COMMANDS[name] = {
            "fn": fn,
            "label": label,
            "description": " ".join((fn.__doc__ or "").split()),
            "params": params,
            "read_only": read_only,
        }
        return fn
    return wrap


def describe() -> list[dict[str, Any]]:
    """Every command with a JSON schema of its parameters."""
    out = []
    for name, cmd in COMMANDS.items():
        properties = {}
        required = []
        for pname, ptype, default, pdesc in cmd["params"]:
            prop: dict[str, Any] = {"type": ptype, "description": pdesc}
            if default is REQUIRED:
                required.append(pname)
            else:
                prop["default"] = default
            properties[pname] = prop
        out.append({
            "name": name,
            "description": cmd["description"],
            "read_only": cmd["read_only"],
            "input_schema": {"type": "object", "properties": properties, "required": required},
        })
    return out


def run(name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run command `name` with `params`; the result dict has "status" 'ok' or 'error'."""
    cmd = COMMANDS.get(name)
    if cmd is None:
        return {"status": "error", "message": "Unknown command {!r}; see `command_list`".format(name)}
    params = dict(params or {})
    known = {p[0] for p in cmd["params"]}
    unknown = sorted(set(params) - known)
    if unknown:
        return {"status": "error", "message": "Unknown parameters for {:s}: {:s}".format(name, ", ".join(unknown))}
    for pname, _ptype, default, _pdesc in cmd["params"]:
        if pname not in params:
            if default is REQUIRED:
                return {"status": "error", "message": "{:s} needs the parameter {!r}".format(name, pname)}
            params[pname] = default
    try:
        result = cmd["fn"](**params)
    except CommandError as ex:
        return {"status": "error", "message": str(ex)}
    if not cmd["read_only"]:
        _undo_push(cmd["label"])
    out = {"status": "ok"}
    out.update(result or {})
    return out


class CommandError(Exception):
    """A clear message for the caller (a wrong name, a wrong mode), not a bug."""


# ------------------------------------------------------------------------------
# Helpers

def _ui() -> contextlib.AbstractContextManager[None]:
    """A context with a window and a 3D viewport, for operators that need one (none in background)."""
    import bpy

    wm = bpy.context.window_manager
    for window in getattr(wm, "windows", ()):
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                region = next((r for r in area.regions if r.type == 'WINDOW'), None)
                return bpy.context.temp_override(window=window, area=area, region=region)
        return bpy.context.temp_override(window=window)
    return contextlib.nullcontext()


def _undo_push(label: str) -> None:
    import bpy

    if bpy.app.background:
        return
    with _ui():
        try:
            bpy.ops.ed.undo_push(message=label)
        except RuntimeError:
            pass


def _object(name: str | None) -> Any:
    """The object `name`, or the active one when `name` is empty."""
    import bpy

    if not name:
        obj = bpy.context.view_layer.objects.active
        if obj is None:
            raise CommandError("No object is active; name one")
        return obj
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise CommandError("There is no object {!r}".format(name))
    return obj


def _objects(names: list[str] | None) -> list[Any]:
    """The objects `names`, or the selection when the list is empty."""
    import bpy

    if not names:
        objs = list(bpy.context.selected_objects)
        if not objs:
            raise CommandError("Nothing is selected; name the objects")
        return objs
    return [_object(n) for n in names]


def _object_mode() -> None:
    import bpy

    if bpy.context.mode != 'OBJECT' and bpy.context.view_layer.objects.active is not None:
        with _ui():
            bpy.ops.object.mode_set(mode='OBJECT')


def _select(objs: list[Any], active: Any = None) -> None:
    """Select `objs` only; `active` (default the first) becomes the active object."""
    import bpy

    view_layer = bpy.context.view_layer
    for obj in view_layer.objects:
        if obj.select_get():
            obj.select_set(False)
    for obj in objs:
        obj.select_set(True)
    view_layer.objects.active = active or (objs[0] if objs else None)


def _call(idname: str, **kwargs: Any) -> set[str]:
    """Run operator `idname` ("module.name") with the UI context; a failure is a CommandError."""
    import bpy

    module, name = idname.split(".")
    op = getattr(getattr(bpy.ops, module), name)
    with _ui():
        try:
            if not op.poll():
                raise CommandError("{:s} can't run here (wrong mode or selection)".format(idname))
            result = op('EXEC_DEFAULT', **kwargs)
        except (RuntimeError, TypeError) as ex:
            raise CommandError("{:s}: {:s}".format(idname, str(ex).strip())) from ex
    if 'FINISHED' not in result:
        raise CommandError("{:s} did not finish ({:s})".format(idname, ", ".join(sorted(result))))
    return result


def _vec(v: Any) -> list[float]:
    return [round(float(x), 6) for x in v]


def _value(v: Any) -> Any:
    """A property value as JSON."""
    if isinstance(v, (bool, int, float, str)) or v is None:
        return v
    if hasattr(v, "name") and hasattr(v, "bl_rna"):
        return v.name
    try:
        return [_value(x) for x in v]
    except TypeError:
        return repr(v)


def _maximize(module: str) -> Any:
    """A module of Moritz's Max tools."""
    import importlib
    try:
        return importlib.import_module("maximize." + module)
    except ImportError as ex:
        raise CommandError("Moritz's Max tools are not loaded") from ex


# ------------------------------------------------------------------------------
# Scene and files

def _stack(obj: Any) -> list[dict[str, Any]]:
    """The modifier stack as Max shows it: top first, the base object last."""
    entries = []
    base_mod, base_label = None, None
    try:
        base_mod, base_label = _maximize("primitives").base_entry(obj)
    except CommandError:
        pass
    for mod in reversed(obj.modifiers):
        if mod == base_mod:
            continue
        entries.append({
            "name": mod.name,
            "type": mod.type,
            "enabled": mod.show_viewport,
            "active": obj.modifiers.active == mod,
        })
    if base_label:
        base = base_label
    elif obj.type == 'MESH':
        base = "Editable Poly"
    elif obj.type == 'CURVE':
        base = "Editable Spline"
    else:
        base = obj.type.title()
    entries.append({"name": base, "type": "BASE", "enabled": True, "active": obj.modifiers.active is None})
    return entries


def _parameters(obj: Any) -> dict[str, Any] | None:
    """An editable primitive's or shape's parameters by their UI names, or None."""
    try:
        primitives = _maximize("primitives")
        shapes = _maximize("shapes")
    except CommandError:
        return None
    kind = shapes.shape_kind(obj)
    if kind is not None:
        shape = obj.data.maximize_shape
        return {label: _value(getattr(shape, prop)) for label, prop in shapes.PARAMETERS.get(kind, ()) + shapes.COMMON}
    mod = primitives.primitive_modifier(obj)
    if mod is None:
        return None
    out = {}
    for item in mod.node_group.interface.items_tree:
        if item.item_type == 'SOCKET' and item.in_out == 'INPUT' and \
                item.socket_type not in {'NodeSocketGeometry', 'NodeSocketCollection'}:
            out[item.name] = _value(getattr(mod.properties.inputs, item.identifier).value)
    return out


def _object_info(obj: Any) -> dict[str, Any]:
    info = {
        "name": obj.name,
        "type": obj.type,
        "layer": obj.users_collection[0].name if obj.users_collection else None,
        "parent": obj.parent.name if obj.parent else None,
        "location": _vec(obj.matrix_world.translation),
        "rotation": _vec(obj.rotation_euler),
        "scale": _vec(obj.scale),
        "dimensions": _vec(obj.dimensions),
        "hidden": obj.hide_get(),
        "frozen": obj.hide_select,
        "selected": obj.select_get(),
        "stack": [e["name"] for e in _stack(obj)],
    }
    params = _parameters(obj)
    if params is not None:
        info["parameters"] = params
    if obj.type == 'MESH' and obj.data:
        import bpy
        # As the viewport shows it: with the stack (an editable primitive's mesh is all modifier).
        mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        info["vertices"] = len(mesh.vertices)
        info["polygons"] = len(mesh.polygons)
    return info


@command("info", "Info", read_only=True)
def info() -> dict[str, Any]:
    """The open scene: file, frame range, renderer, mode, every object (layer, transform, modifier
    stack top first, an editable primitive's parameters) and missing files."""
    import bpy

    scene = bpy.context.scene
    missing = []
    for image in bpy.data.images:
        if image.source == 'FILE' and image.filepath and not image.packed_file:
            path = bpy.path.abspath(image.filepath, library=image.library)
            import os
            if not os.path.exists(path):
                missing.append(image.filepath)
    for lib in bpy.data.libraries:
        import os
        if not os.path.exists(bpy.path.abspath(lib.filepath)):
            missing.append(lib.filepath)
    active = bpy.context.view_layer.objects.active
    return {
        "file": bpy.data.filepath,
        "unsaved_changes": bpy.data.is_dirty,
        "scene": scene.name,
        "frame_range": [scene.frame_start, scene.frame_end],
        "frame": scene.frame_current,
        "renderer": scene.render.engine,
        "resolution": [scene.render.resolution_x, scene.render.resolution_y],
        "camera": scene.camera.name if scene.camera else None,
        "mode": bpy.context.mode,
        "active_object": active.name if active else None,
        "objects": [_object_info(o) for o in scene.objects],
        "missing_files": missing,
        "moritz_version": getattr(bpy.app, "moritz_version_string", ""),
        "blender_version": bpy.app.version_string,
    }


@command("object_info", "Object Info", (
    ("object", "string", "", "Object name; empty for the active object"),
), read_only=True)
def object_info(object: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """One object: transform, layer, modifier stack (top first) and an editable primitive's parameters."""
    return {"object": _object_info(_object(object))}


@command("open", "Open", (
    ("path", "string", REQUIRED, "The .blend file"),
))
def open_file(path: str) -> dict[str, Any]:
    """Open a .blend file. Unsaved changes in the open scene are lost."""
    import bpy

    with _ui():
        bpy.ops.wm.open_mainfile(filepath=path)
    return {"file": bpy.data.filepath}


@command("save", "Save", (
    ("path", "string", "", "Where to save; empty saves to the open file"),
    ("copy", "boolean", False, "Save a copy and keep working on the open file"),
))
def save(path: str, copy: bool) -> dict[str, Any]:
    """Save the scene as a .blend file."""
    import bpy

    if not path and not bpy.data.filepath:
        raise CommandError("The scene has never been saved; give a path")
    with _ui():
        bpy.ops.wm.save_as_mainfile(filepath=path or bpy.data.filepath, copy=copy)
    return {"file": path or bpy.data.filepath}


# Export and import operators by file extension.
_EXPORTERS = {
    ".fbx": ("export_scene.fbx", {"use_selection": "use_selection"}),
    ".obj": ("wm.obj_export", {"use_selection": "export_selected_objects"}),
    ".glb": ("export_scene.gltf", {"use_selection": "use_selection"}),
    ".gltf": ("export_scene.gltf", {"use_selection": "use_selection"}),
    ".usd": ("wm.usd_export", {"use_selection": "selected_objects_only"}),
    ".usda": ("wm.usd_export", {"use_selection": "selected_objects_only"}),
    ".usdc": ("wm.usd_export", {"use_selection": "selected_objects_only"}),
    ".usdz": ("wm.usd_export", {"use_selection": "selected_objects_only"}),
    ".abc": ("wm.alembic_export", {"use_selection": "selected"}),
    ".stl": ("wm.stl_export", {"use_selection": "export_selected_objects"}),
    ".ply": ("wm.ply_export", {"use_selection": "export_selected_objects"}),
}
_IMPORTERS = {
    ".fbx": "import_scene.fbx",
    ".obj": "wm.obj_import",
    ".glb": "import_scene.gltf",
    ".gltf": "import_scene.gltf",
    ".usd": "wm.usd_import",
    ".usda": "wm.usd_import",
    ".usdc": "wm.usd_import",
    ".usdz": "wm.usd_import",
    ".abc": "wm.alembic_import",
    ".stl": "wm.stl_import",
    ".ply": "wm.ply_import",
    ".max": "import_scene.max",
    ".mxscene": "maximize.import_mxscene",
}


@command("export", "Export", (
    ("path", "string", REQUIRED, "Output file; the extension picks the format: " + ", ".join(_EXPORTERS)
     + ", .blend"),
    ("selected_only", "boolean", False, "Export only the selected objects"),
))
def export(path: str, selected_only: bool) -> dict[str, Any]:
    """Export the scene (or the selection) to FBX, OBJ, glTF, USD, Alembic, STL or PLY, or save a
    copy as .blend."""
    import os

    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        return save(path, True)
    if ext not in _EXPORTERS:
        raise CommandError("Can't export {:s}; use one of {:s}".format(ext or "a file without extension",
                                                                      ", ".join(_EXPORTERS)))
    _object_mode()
    idname, props = _EXPORTERS[ext]
    kwargs: dict[str, Any] = {"filepath": path}
    if selected_only:
        kwargs[props["use_selection"]] = True
    if idname == "export_scene.gltf":
        kwargs["export_format"] = 'GLB' if ext == ".glb" else 'GLTF_SEPARATE'
    _call(idname, **kwargs)
    return {"file": path}


@command("import", "Import", (
    ("path", "string", REQUIRED, "File to import; the extension picks the format: " + ", ".join(_IMPORTERS)),
))
def import_file(path: str) -> dict[str, Any]:
    """Import FBX, OBJ, glTF, USD, Alembic, STL, PLY, a 3ds Max file (.max: meshes with their materials
    and textures), or a 3ds Max scene saved with the Moritz exporter script (.mxscene)."""
    import os
    import bpy

    ext = os.path.splitext(path)[1].lower()
    if ext not in _IMPORTERS:
        raise CommandError("Can't import {:s}; use one of {:s}".format(ext, ", ".join(_IMPORTERS)))
    if not os.path.isfile(path):
        raise CommandError("There is no file {:s}".format(path))
    _object_mode()
    before = set(bpy.data.objects)
    _call(_IMPORTERS[ext], filepath=path)
    return {"objects": sorted(o.name for o in set(bpy.data.objects) - before)}


@command("render", "Render", (
    ("path", "string", REQUIRED, "Output file for a still, or a path with #### for the frames of an animation"),
    ("frame", "integer", -1, "Frame to render; -1 for the current one"),
    ("end_frame", "integer", -1, "Last frame: renders an animation from `frame` to here"),
    ("camera", "string", "", "Camera to render from; empty for the scene camera"),
))
def render(path: str, frame: int, end_frame: int, camera: str) -> dict[str, Any]:
    """Render a still or an animation with the scene's renderer and settings. Moritz is busy until
    it is done."""
    import bpy

    scene = bpy.context.scene
    if camera:
        scene.camera = _object(camera)
    if scene.camera is None:
        raise CommandError("The scene has no camera")
    keep = (scene.render.filepath, scene.frame_start, scene.frame_end, scene.frame_current)
    try:
        scene.render.filepath = path
        if end_frame >= 0:
            scene.frame_start = frame if frame >= 0 else scene.frame_current
            scene.frame_end = end_frame
            with _ui():
                bpy.ops.render.render(animation=True)
            return {"frames": [scene.frame_start, scene.frame_end], "path": path}
        if frame >= 0:
            scene.frame_set(frame)
        with _ui():
            bpy.ops.render.render(write_still=True)
        return {"file": bpy.path.abspath(scene.render.frame_path(frame=scene.frame_current)) if "#" in path
                else bpy.path.abspath(path)}
    finally:
        scene.render.filepath, scene.frame_start, scene.frame_end = keep[:3]
        if scene.frame_current != keep[3]:
            scene.frame_set(keep[3])


# ------------------------------------------------------------------------------
# Create

def _kinds() -> dict[str, str]:
    """Create-tab object types: Max name (lower case, no spaces) -> kind."""
    primitives = _maximize("primitives")
    out = {}
    for ident, label, *_rest in primitives.KINDS:
        out[label.lower().replace(" ", "")] = ident
    return out


@command("create_list", "Create List", read_only=True)
def create_list() -> dict[str, Any]:
    """The object types `create` makes, by their Create-tab names: standard and extended primitives,
    Suzanne, compound objects and shapes (splines)."""
    primitives = _maximize("primitives")
    shapes = _maximize("shapes")
    label = {k[0]: k[1] for k in primitives.KINDS}
    return {
        "standard_primitives": [label[k] for k in primitives.STANDARD_PRIMITIVES] + ["Suzanne"],
        "extended_primitives": [label[k] for k in primitives.EXTENDED_PRIMITIVES],
        "compound_objects": [k[1] for k in _maximize("compound").COMPOUND_KINDS],
        "shapes": [k[1] for k in shapes.SHAPE_KINDS],
        "note": "Parameters use the names the Modify tab shows (Length, Width, Height, Radius, Segments ...); "
                "object_info lists them after creation.",
    }


def _set_parameters(obj: Any, parameters: dict[str, Any]) -> None:
    primitives = _maximize("primitives")
    if not primitives.is_parametric(obj):
        raise CommandError("{:s} has no parameters (it is not an editable primitive or shape)".format(obj.name))
    for name, value in parameters.items():
        try:
            primitives.parameter(obj, name).value = value
        except KeyError as ex:
            raise CommandError("{:s} has no parameter {!r}; it has {:s}".format(
                obj.name, name, ", ".join(_parameters(obj) or ()))) from ex
        except (TypeError, ValueError) as ex:
            raise CommandError("{:s}: {:s}".format(name, str(ex))) from ex
    obj.update_tag()


@command("create", "Create", (
    ("type", "string", REQUIRED, "Create-tab name: Box, Sphere, Cylinder, Teapot, Suzanne, TorusKnot, "
     "ChamferBox, Plane, Circle, Rectangle, Star, Helix ... (see create_list)"),
    ("position", "array", [0.0, 0.0, 0.0], "Pivot position [x, y, z]"),
    ("parameters", "object", {}, "Parameters by name, e.g. {\"Length\": 2, \"Width\": 1, \"Height\": 0.5}"),
    ("name", "string", "", "Object name; empty for Max's naming (Box001, Box002 ...)"),
))
def create(type: str, position: list[float], parameters: dict[str, Any], name: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """Create an object from the Create tab, with its Max parameters. Primitives and shapes stay
    editable (their parameters can change later with set_parameters) until they are collapsed."""
    import bpy

    _object_mode()
    key = type.lower().replace(" ", "").replace("-", "")
    if key == "suzanne":
        _call("maximize.add_suzanne")
    else:
        kind = _kinds().get(key)
        if kind is None:
            raise CommandError("Unknown type {!r}; see create_list".format(type))
        _call("maximize.add_primitive", kind=kind)
    obj = bpy.context.view_layer.objects.active
    obj.location = position
    if parameters:
        _set_parameters(obj, parameters)
    if name:
        obj.name = name
    bpy.context.view_layer.update()
    return {"object": _object_info(obj)}


@command("set_parameters", "Set Parameters", (
    ("object", "string", "", "Object name; empty for the active object"),
    ("parameters", "object", REQUIRED, "Parameters by name, e.g. {\"Radius\": 0.5, \"Segments\": 24}"),
))
def set_parameters(object: str, parameters: dict[str, Any]) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """Change an editable primitive's or shape's parameters, as in the Modify tab's Parameters rollout."""
    obj = _object(object)
    _set_parameters(obj, parameters)
    return {"parameters": _parameters(obj)}


# ------------------------------------------------------------------------------
# Modify

@command("stack", "Stack", (
    ("object", "string", "", "Object name; empty for the active object"),
), read_only=True)
def stack(object: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """The modifier stack as the Modify tab shows it: top first, the base object (Box, Editable Poly ...) last."""
    return {"stack": _stack(_object(object))}


def _entries(obj: Any) -> list[tuple[str, str, str]]:
    """(key, Max or Blender label, other name) of every entry of the modifier list for `obj`."""
    from bl_operators import moritz_modifier_list as mlist

    out = []
    seen = set()
    for scheme in ('MAX', 'BLENDER'):
        for key, label, other, _words in mlist.entries(obj, scheme):
            if (key, label) not in seen:
                seen.add((key, label))
                out.append((key, label, other))
    return out


@command("modifier_list", "Modifier List", (
    ("object", "string", "", "Object name; empty for the active object"),
), read_only=True)
def modifier_list(object: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """The modifiers that can go on this object, by Max name with the Blender name beside it
    (Bend is Simple Deform, Shell is Solidify ...)."""
    obj = _object(object)
    return {"modifiers": [{"name": label, "also": other} for _key, label, other in _entries(obj)]}


def _modifier(obj: Any, name: str) -> Any:
    mod = obj.modifiers.get(name)
    if mod is None:
        raise CommandError("{:s} has no modifier {!r}; it has {:s}".format(
            obj.name, name, ", ".join(m.name for m in obj.modifiers) or "none"))
    return mod


def _set_props(target: Any, settings: dict[str, Any]) -> None:
    for prop, value in settings.items():
        if prop not in target.bl_rna.properties:
            raise CommandError("{:s} has no setting {!r}".format(target.name, prop))
        try:
            setattr(target, prop, value)
        except (TypeError, ValueError, AttributeError) as ex:
            raise CommandError("{:s}: {:s}".format(prop, str(ex))) from ex


@command("add_modifier", "Add Modifier", (
    ("object", "string", "", "Object name; empty for the active object"),
    ("modifier", "string", REQUIRED, "Max or Blender name: Bend, TurboSmooth, Shell, Edit Poly, Symmetry, "
     "Simple Deform, Solidify ... (see modifier_list)"),
    ("settings", "object", {}, "Modifier settings by Python property name, e.g. {\"angle\": 1.57}"),
))
def add_modifier(object: str, modifier: str, settings: dict[str, Any]) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """Add a modifier on top of the stack, from the same list as the Modify tab's Modifier List."""
    obj = _object(object)
    _object_mode()
    _select([obj])
    want = modifier.lower()
    match = next(((k, label) for k, label, other in _entries(obj) if label.lower() == want), None) or \
        next(((k, label) for k, label, other in _entries(obj) if want in [o.strip().lower() for o in other.split(",")]),
             None)
    if match is None:
        raise CommandError("No modifier {!r} for a {:s}; see modifier_list".format(modifier, obj.type.lower()))
    before = set(obj.modifiers)
    _call("object.moritz_modifier_add_entry", key=match[0], label=match[1])
    new = [m for m in obj.modifiers if m not in before]
    if new and settings:
        _set_props(new[0], settings)
    return {"modifier": new[0].name if new else match[1], "stack": [e["name"] for e in _stack(obj)]}


@command("set_modifier", "Set Modifier", (
    ("object", "string", "", "Object name; empty for the active object"),
    ("modifier", "string", REQUIRED, "The modifier's name in the stack"),
    ("settings", "object", {}, "Settings by Python property name, e.g. {\"levels\": 2}"),
    ("enabled", "boolean", True, "On or off in the viewport and render (the light bulb)"),
    ("make_active", "boolean", False, "Select it in the stack (the level Edit Poly works on)"),
))
def set_modifier(object: str, modifier: str, settings: dict[str, Any], enabled: bool,  # pylint: disable=redefined-builtin
                 make_active: bool) -> dict[str, Any]:
    """Change a modifier's settings, turn it on or off, or select it in the stack."""
    obj = _object(object)
    mod = _modifier(obj, modifier)
    _set_props(mod, settings)
    mod.show_viewport = mod.show_render = enabled
    if make_active:
        obj.modifiers.active = mod
    return {"settings": {p.identifier: _value(getattr(mod, p.identifier)) for p in mod.bl_rna.properties
                         if not p.is_readonly and p.identifier not in {"rna_type"}}}


@command("remove_modifier", "Remove Modifier", (
    ("object", "string", "", "Object name; empty for the active object"),
    ("modifier", "string", REQUIRED, "The modifier's name in the stack"),
))
def remove_modifier(object: str, modifier: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """Delete a modifier from the stack."""
    obj = _object(object)
    _modifier(obj, modifier)
    _object_mode()
    _select([obj])
    _call("object.modifier_remove", modifier=modifier)
    return {"stack": [e["name"] for e in _stack(obj)]}


@command("collapse", "Collapse", (
    ("object", "string", "", "Object name; empty for the active object"),
    ("modifier", "string", "", "Collapse To this modifier (it and everything below); empty collapses all"),
))
def collapse(object: str, modifier: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """Collapse the stack into an Editable Poly: all of it, or Collapse To one modifier. An editable
    primitive loses its parameters."""
    obj = _object(object)
    _object_mode()
    _select([obj])
    if modifier:
        obj.modifiers.active = _modifier(obj, modifier)
        _call("maximize.collapse_to")
    else:
        _call("maximize.collapse_all")
    return {"stack": [e["name"] for e in _stack(obj)]}


# ------------------------------------------------------------------------------
# Edit Poly

_LEVELS = {0: 'OBJECT', 1: 'VERTEX', 2: 'EDGE', 3: 'BORDER', 4: 'POLYGON', 5: 'ELEMENT'}


@command("edit_poly_level", "Sub-Object Level", (
    ("object", "string", "", "Object name; empty for the active object"),
    ("level", "string", REQUIRED, "Object, Vertex, Edge, Border, Polygon or Element (or 0-5, as the keys 1-5)"),
))
def edit_poly_level(object: str, level: str) -> dict[str, Any]:  # pylint: disable=redefined-builtin
    """Go to a sub-object level of the Editable Poly, or of the active Edit Poly modifier
    (set_modifier make_active picks it). Object (0) leaves it."""
    import bpy

    obj = _object(object)
    key = level.strip().upper()
    if key.isdigit():
        key = _LEVELS.get(int(key), key)
    if key not in _LEVELS.values():
        raise CommandError("Unknown level {!r}: use Object, Vertex, Edge, Border, Polygon or Element".format(level))
    if bpy.context.view_layer.objects.active != obj:
        _object_mode()
        _select([obj])
    _call("maximize.subobject", level=key)
    return {"mode": bpy.context.mode, "level": key}


def _edit_mesh() -> tuple[Any, Any]:
    import bmesh
    import bpy

    obj = bpy.context.edit_object
    if obj is None or obj.type != 'MESH':
        raise CommandError("Not at a sub-object level; use edit_poly_level first")
    return obj, bmesh.from_edit_mesh(obj.data)


@command("edit_poly_select", "Select", (
    ("indices", "array", [], "Vertex, edge or polygon indices at the current level"),
    ("mode", "string", "SET", "SET, ADD, REMOVE, ALL, NONE, INVERT, GROW, SHRINK, LOOP or RING"),
))
def edit_poly_select(indices: list[int], mode: str) -> dict[str, Any]:
    """Select sub-objects at the current level by index, or all / none / invert / grow / shrink /
    loop / ring, as the Selection rollout does."""
    import bmesh

    obj, bm = _edit_mesh()
    mode = mode.upper()
    simple = {"ALL": ("mesh.select_all", {"action": 'SELECT'}), "NONE": ("mesh.select_all", {"action": 'DESELECT'}),
              "INVERT": ("mesh.select_all", {"action": 'INVERT'}), "GROW": ("mesh.select_more", {}),
              "SHRINK": ("mesh.select_less", {}), "LOOP": ("mesh.loop_multi_select", {"ring": False}),
              "RING": ("mesh.loop_multi_select", {"ring": True})}
    if mode in simple:
        _call(simple[mode][0], **simple[mode][1])
        obj, bm = _edit_mesh()
    elif mode in {"SET", "ADD", "REMOVE"}:
        seq = bm.verts if 'VERT' in bm.select_mode else bm.edges if 'EDGE' in bm.select_mode else bm.faces
        seq.ensure_lookup_table()
        if mode == "SET":
            for elem in (bm.verts, bm.edges, bm.faces):
                for e in elem:
                    e.select_set(False)
        for i in indices:
            if not 0 <= i < len(seq):
                raise CommandError("Index {:d} is out of range (0-{:d})".format(i, len(seq) - 1))
            seq[i].select_set(mode != "REMOVE")
        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)
    else:
        raise CommandError("Unknown mode {!r}".format(mode))
    return _selection(bm)


def _selection(bm: Any) -> dict[str, Any]:
    return {
        "selected_vertices": [v.index for v in bm.verts if v.select],
        "selected_edges": [e.index for e in bm.edges if e.select],
        "selected_polygons": [f.index for f in bm.faces if f.select],
    }


@command("edit_poly_selection", "Selection", read_only=True)
def edit_poly_selection() -> dict[str, Any]:
    """The selected vertices, edges and polygons (indices) at the current sub-object level."""
    _obj, bm = _edit_mesh()
    return _selection(bm)


# Max name -> (operator, fixed arguments, {setting: operator argument}).
_TOOLS: dict[str, tuple[str, dict[str, Any], dict[str, str]]] = {
    "smart extrude": ("maximize.smart_extrude", {}, {"distance": "distance"}),
    "extrude": ("maximize.extrude_max", {}, {"height": "height", "width": "width"}),
    "chamfer": ("mesh.bevel", {}, {"amount": "offset", "segments": "segments"}),
    "weld": ("mesh.remove_doubles", {}, {"threshold": "threshold"}),
    "bridge": ("mesh.bridge_edge_loops", {}, {"segments": "number_cuts"}),
    "cap": ("maximize.cap", {}, {"mode": "mode", "ring": "ring"}),
    "connect": ("maximize.connect", {}, {"segments": "segments"}),
    "inset": ("mesh.inset", {}, {"amount": "thickness", "depth": "depth"}),
    "remove": ("mesh.dissolve_mode", {}, {}),
    "detach": ("mesh.separate", {"type": 'SELECTED'}, {}),
    "make planar": ("maximize.make_planar_axis", {}, {"axis": "axis"}),
    "create shape": ("maximize.create_shape", {}, {"smooth": "smooth"}),
    "flip": ("mesh.flip_normals", {}, {}),
    "tessellate": ("mesh.subdivide", {}, {"segments": "number_cuts"}),
    "collapse": ("mesh.merge", {"type": 'COLLAPSE'}, {}),
    "slice": ("mesh.bisect", {}, {"plane_co": "plane_co", "plane_no": "plane_no"}),
}


@command("edit_poly_tool", "Edit Poly", (
    ("tool", "string", REQUIRED, "Max name: " + ", ".join(t.title() for t in _TOOLS) + ", Delete"),
    ("settings", "object", {}, "The tool's settings, e.g. {\"amount\": 0.1, \"segments\": 2} for Chamfer, "
     "{\"distance\": 0.5} for Smart Extrude, {\"height\": 0.2, \"width\": 0.05} for Extrude"),
))
def edit_poly_tool(tool: str, settings: dict[str, Any]) -> dict[str, Any]:
    """Run an Edit Poly tool on the current sub-object selection, as its button in the Edit
    Geometry or Edit Polygons rollout would (with the settings its caddy shows)."""
    import bpy

    obj, _bm = _edit_mesh()
    name = tool.strip().lower()
    if name == "delete":
        mode = bpy.context.tool_settings.mesh_select_mode
        _call("mesh.delete", type='VERT' if mode[0] else 'EDGE' if mode[1] else 'FACE')
    else:
        entry = _TOOLS.get(name)
        if entry is None:
            raise CommandError("Unknown tool {!r}; use one of {:s}, Delete".format(
                tool, ", ".join(t.title() for t in _TOOLS)))
        idname, fixed, names = entry
        kwargs = dict(fixed)
        for key, value in settings.items():
            if key not in names:
                raise CommandError("{:s} has no setting {!r}; it has {:s}".format(
                    tool, key, ", ".join(names) or "none"))
            kwargs[names[key]] = value
        _call(idname, **kwargs)
    obj, bm = _edit_mesh()
    return {"vertices": len(bm.verts), "polygons": len(bm.faces), **_selection(bm)}


# ------------------------------------------------------------------------------
# Utilities and transforms

@command("transform", "Transform Type-In", (
    ("objects", "array", [], "Object names; empty for the selection"),
    ("mode", "string", "MOVE", "MOVE, ROTATE (degrees) or SCALE (percent)"),
    ("absolute", "array", [], "Absolute: World [x, y, z]; the active object's value"),
    ("offset", "array", [], "Offset: World [x, y, z], added to each object"),
))
def transform(objects: list[str], mode: str, absolute: list[float], offset: list[float]) -> dict[str, Any]:
    """Transform Type-In: move, rotate or scale to absolute values or by an offset. In Edit Mode it
    moves the sub-object selection."""
    import bpy

    mode = mode.upper()
    if bool(absolute) == bool(offset):
        raise CommandError("Give either absolute or offset")
    if bpy.context.mode == 'OBJECT':
        objs = _objects(objects)
        _select(objs)
    kwargs: dict[str, Any] = {"mode": mode}
    if absolute:
        kwargs["absolute"] = absolute
    else:
        kwargs["offset"] = offset
    _call("maximize.transform_typein", **kwargs)
    if bpy.context.mode == 'OBJECT':
        bpy.context.view_layer.update()
        return {"objects": [_object_info(o) for o in objs]}
    return {}


@command("align", "Align", (
    ("objects", "array", [], "Objects to move; empty for the selection"),
    ("target", "string", REQUIRED, "Target object"),
    ("position", "array", [True, True, True], "Align X, Y, Z position"),
    ("current_point", "string", "CENTER", "MIN, CENTER, PIVOT or MAX of the objects"),
    ("target_point", "string", "CENTER", "MIN, CENTER, PIVOT or MAX of the target"),
    ("orientation", "array", [False, False, False], "Align the local X, Y, Z axes"),
    ("match_scale", "array", [False, False, False], "Match the X, Y, Z scale"),
))
def align(objects: list[str], target: str, position: list[bool], current_point: str, target_point: str,
          orientation: list[bool], match_scale: list[bool]) -> dict[str, Any]:
    """Align objects to a target, as Max's Align dialog."""
    import bpy

    _object_mode()
    tgt = _object(target)
    objs = [o for o in _objects(objects) if o != tgt]
    _select(objs + [tgt], active=tgt)
    _call("maximize.align_apply", target=tgt.name, position=position, current_point=current_point.upper(),
          target_point=target_point.upper(), orientation=orientation, match_scale=match_scale)
    bpy.context.view_layer.update()
    return {"objects": [_object_info(o) for o in objs]}


@command("array", "Array", (
    ("objects", "array", [], "Objects to clone; empty for the selection"),
    ("move", "array", [1.0, 0.0, 0.0], "Incremental move per copy [x, y, z]"),
    ("rotate", "array", [0.0, 0.0, 0.0], "Incremental rotation per copy, degrees"),
    ("scale", "array", [100.0, 100.0, 100.0], "Incremental scale per copy, percent"),
    ("count", "integer", 10, "Copies in the first dimension (the original counts)"),
    ("count_2d", "integer", 1, "Rows in the second dimension"),
    ("offset_2d", "array", [0.0, 1.0, 0.0], "Row offset of the second dimension"),
    ("count_3d", "integer", 1, "Layers in the third dimension"),
    ("offset_3d", "array", [0.0, 0.0, 1.0], "Layer offset of the third dimension"),
    ("clone_type", "string", "COPY", "COPY, INSTANCE or REFERENCE"),
))
def array(objects: list[str], move: list[float], rotate: list[float], scale: list[float], count: int,
          count_2d: int, offset_2d: list[float], count_3d: int, offset_3d: list[float],
          clone_type: str) -> dict[str, Any]:
    """Max's Array tool: clone objects in 1D, 2D or 3D with incremental move, rotate and scale."""
    import math
    import bpy

    _object_mode()
    objs = _objects(objects)
    _select(objs)
    before = set(bpy.data.objects)
    dimension = '3D' if count_3d > 1 else '2D' if count_2d > 1 else '1D'
    _call("maximize.array", move=move, rotate=[math.radians(a) for a in rotate], scale=scale,
          dimension=dimension, count_1d=count, count_2d=count_2d, offset_2d=offset_2d, count_3d=count_3d,
          offset_3d=offset_3d, clone_type=clone_type.upper())
    return {"created": sorted(o.name for o in set(bpy.data.objects) - before)}


@command("spacing", "Spacing Tool", (
    ("objects", "array", REQUIRED, "Objects to distribute"),
    ("path", "string", REQUIRED, "The spline (curve object) to follow"),
    ("count", "integer", 10, "Number of copies"),
    ("spacing", "number", 0.0, "Distance between copies; 0 spreads Count evenly"),
    ("follow", "boolean", False, "Turn each copy's X axis along the path"),
    ("clone_type", "string", "INSTANCE", "COPY, INSTANCE or REFERENCE"),
))
def spacing(objects: list[str], path: str, count: int, spacing: float, follow: bool,  # pylint: disable=redefined-outer-name
            clone_type: str) -> dict[str, Any]:
    """Max's Spacing Tool: distribute clones of objects along a spline."""
    import bpy

    _object_mode()
    curve = _object(path)
    objs = _objects(objects)
    _select(objs + [curve], active=curve)
    before = set(bpy.data.objects)
    kwargs: dict[str, Any] = {"count": count, "follow": follow, "clone_type": clone_type.upper()}
    if spacing > 0.0:
        kwargs["mode"] = 'SPACING'
        kwargs["spacing"] = spacing
    _call("maximize.spacing", **kwargs)
    return {"created": sorted(o.name for o in set(bpy.data.objects) - before)}


# ------------------------------------------------------------------------------
# Scene Explorer

@command("scene_explorer", "Scene Explorer", read_only=True)
def scene_explorer() -> dict[str, Any]:
    """Layers (collections) with their objects, and which objects are hidden, frozen or selected."""
    import bpy

    def layer(lc: Any) -> dict[str, Any]:
        return {
            "name": lc.collection.name,
            "visible": not lc.exclude and not lc.hide_viewport,
            "frozen": lc.collection.hide_select,
            "objects": [{"name": o.name, "type": o.type, "hidden": o.hide_get(), "frozen": o.hide_select,
                         "selected": o.select_get()} for o in lc.collection.objects],
            "layers": [layer(c) for c in lc.children],
        }
    return {"layers": layer(bpy.context.view_layer.layer_collection)}


@command("select", "Select", (
    ("objects", "array", [], "Object names"),
    ("mode", "string", "SET", "SET, ADD, REMOVE, ALL or NONE"),
))
def select(objects: list[str], mode: str) -> dict[str, Any]:
    """Select objects by name."""
    import bpy

    _object_mode()
    mode = mode.upper()
    view_layer = bpy.context.view_layer
    if mode in {"ALL", "NONE"}:
        for obj in view_layer.objects:
            if obj.visible_get() and not obj.hide_select:
                obj.select_set(mode == "ALL")
    else:
        objs = [_object(n) for n in objects]
        if mode == "SET":
            _select(objs)
        else:
            for obj in objs:
                obj.select_set(mode == "ADD")
            if mode == "ADD" and objs:
                view_layer.objects.active = objs[0]
    return {"selected": sorted(o.name for o in bpy.context.selected_objects)}


@command("hide", "Hide", (
    ("objects", "array", [], "Object names; empty for the selection"),
    ("hidden", "boolean", True, "Hide (true) or unhide (false)"),
))
def hide(objects: list[str], hidden: bool) -> dict[str, Any]:
    """Hide or unhide objects."""
    objs = _objects(objects)
    for obj in objs:
        obj.hide_set(hidden)
    return {"objects": [o.name for o in objs]}


@command("freeze", "Freeze", (
    ("objects", "array", [], "Object names; empty for the selection"),
    ("frozen", "boolean", True, "Freeze (true) or unfreeze (false)"),
))
def freeze(objects: list[str], frozen: bool) -> dict[str, Any]:
    """Freeze objects (they can't be selected and draw in gray) or unfreeze them."""
    objs = _objects(objects)
    for obj in objs:
        obj.hide_select = frozen
        if frozen:
            obj.select_set(False)
    return {"objects": [o.name for o in objs]}


@command("move_to_layer", "Move to Layer", (
    ("objects", "array", [], "Object names; empty for the selection"),
    ("layer", "string", REQUIRED, "Layer (collection) name; made if it does not exist"),
))
def move_to_layer(objects: list[str], layer: str) -> dict[str, Any]:
    """Move objects to a layer, creating the layer when needed."""
    import bpy

    objs = _objects(objects)
    coll = bpy.data.collections.get(layer)
    if coll is None:
        coll = bpy.data.collections.new(layer)
        bpy.context.scene.collection.children.link(coll)
    for obj in objs:
        for other in list(obj.users_collection):
            if other != coll:
                other.objects.unlink(obj)
        if obj.name not in coll.objects:
            coll.objects.link(obj)
    return {"layer": coll.name, "objects": [o.name for o in objs]}


@command("selection_sets", "Selection Sets", read_only=True)
def selection_sets() -> dict[str, Any]:
    """The named selection sets and their objects."""
    import bpy

    sets = getattr(bpy.context.scene, "maximize_sets", ())
    return {"sets": {s.name: [i.object.name for i in s.objects if i.object] for s in sets}}


@command("selection_set_create", "Create Selection Set", (
    ("name", "string", REQUIRED, "Set name; an existing set is replaced"),
    ("objects", "array", [], "Object names; empty for the selection"),
))
def selection_set_create(name: str, objects: list[str]) -> dict[str, Any]:
    """Store objects as a named selection set."""
    _object_mode()
    _select(_objects(objects))
    _call("maximize.selset_create", name=name)
    return selection_sets()


@command("selection_set_select", "Select Set", (
    ("name", "string", REQUIRED, "Set name"),
    ("extend", "boolean", False, "Add to the current selection"),
))
def selection_set_select(name: str, extend: bool) -> dict[str, Any]:
    """Select the objects of a named selection set."""
    import bpy

    _object_mode()
    _call("maximize.selset_select", name=name, extend=extend)
    return {"selected": sorted(o.name for o in bpy.context.selected_objects)}


@command("hold", "Hold", read_only=True)
def hold() -> dict[str, Any]:
    """Hold: keep a copy of the scene to come back to with fetch."""
    _call("maximize.hold")
    return {}


@command("fetch", "Fetch")
def fetch() -> dict[str, Any]:
    """Fetch: go back to the scene kept with hold. Changes since then are lost."""
    _call("maximize.fetch")
    return {}


# ------------------------------------------------------------------------------
# Settings and screenshots

@command("settings", "Settings", read_only=True)
def settings() -> dict[str, Any]:
    """The keymap and name scheme in use."""
    import bpy

    prefs = _maximize("preferences").get_prefs()
    return {
        "keymap": bpy.context.preferences.keymap.active_keyconfig,
        "name_scheme": prefs.name_scheme if prefs else None,
        "names_in_use": _maximize("vocabulary").name_scheme(),
        "keymaps": [k[0] for k in _maximize("preferences").KEYMAPS],
        "name_schemes": ["AUTO", "BLENDER", "MAX", "MORITZ"],
    }


@command("set_settings", "Settings", (
    ("keymap", "string", "", "Moritz, Max, Blender or Industry_Compatible; empty keeps it"),
    ("name_scheme", "string", "", "AUTO (follow the keymap), BLENDER, MAX or MORITZ; empty keeps it"),
))
def set_settings(keymap: str, name_scheme: str) -> dict[str, Any]:
    """Switch the keymap or the name scheme, as in Preferences > Keymap."""
    import bpy

    if keymap:
        _call("maximize.keymap_set", keymap=keymap)
    if name_scheme:
        prefs = _maximize("preferences").get_prefs()
        prefs.name_scheme = name_scheme.upper()
    bpy.context.preferences.is_dirty = True
    return settings()


@command("screenshot", "Screenshot", (
    ("path", "string", REQUIRED, "PNG file to write"),
    ("area", "string", "WINDOW", "WINDOW for the whole window, VIEW_3D for the biggest viewport"),
), read_only=True)
def screenshot(path: str, area: str) -> dict[str, Any]:
    """Save a screenshot of the Moritz window or of its biggest 3D viewport."""
    import bpy

    if bpy.app.background:
        raise CommandError("There is no window in background mode")
    window = bpy.context.window_manager.windows[0]
    if area.upper() == "WINDOW":
        with bpy.context.temp_override(window=window):
            bpy.ops.screen.screenshot(filepath=path)
    else:
        areas = [a for a in window.screen.areas if a.type == area.upper()]
        if not areas:
            raise CommandError("No {:s} area is open".format(area))
        big = max(areas, key=lambda a: a.width * a.height)
        with bpy.context.temp_override(window=window, area=big):
            bpy.ops.screen.screenshot_area(filepath=path)
    return {"file": path}


@command("run_python", "Run Python", (
    ("code", "string", "", "Python to run; assign a dict to `result` to return data"),
    ("path", "string", "", "A .py file to run instead of `code`"),
))
def run_python(code: str, path: str) -> dict[str, Any]:
    """Run Python in Moritz with full access to bpy (as Blender's Python API)."""
    if path:
        with open(path, encoding="utf-8") as fh:
            code = fh.read()
    namespace: dict[str, Any] = {"__name__": "__main__", "__file__": path or "<moritz-cli>", "result": {}}
    exec(compile(code, path or "<moritz-cli>", "exec"), namespace)  # pylint: disable=exec-used
    result = namespace.get("result")
    return {"result": _value(result) if not isinstance(result, dict) else result}
