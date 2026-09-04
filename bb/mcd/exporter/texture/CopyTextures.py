"""Copy every texture used by the scene's materials into the Unity project.

Blender materials reference their images by absolute path (or hold them packed
inside the .blend). Neither survives an FBX export: the FBX records the path the
image had at export time, and Unity can only resolve a texture it can actually
find in the project. So materials arrive in Unity stripped down to a flat base
colour and look like they "didn't transfer".

This operator closes that gap. It walks every material's node tree, and for each
image texture it either unpacks the bytes already stored in the .blend or copies
the source file off disk, writing everything into one folder inside the Unity
project. Once the images are anywhere under Assets/, Unity's material-description
importer binds them to the imported materials by filename on the next reimport --
no material map entry needed.

Deliberately a separate operation rather than part of export: ExportOp.PostExport
can't be relied on (see the note there -- there's no callback after the modal file
browser), and copying textures is slow and rarely needs to happen on every export.
"""

import bpy
import os
import re
import shutil

from bpy.props import StringProperty, BoolProperty
from bpy.types import Operator


def _getUnityProjectRoot() -> str:
    """Read the configured Unity project root, importing prefs lazily.

    Deliberately not a module-level import. bb/__init__.py reloads modules in a
    fixed order and this module is pulled in by ExportBox, which reloads well
    before bb.mcd.prefs -- so at import time sys.modules still holds the *previous*
    version of the prefs module. A top-level `from ... import GetUnityProjectRoot`
    therefore explodes on the first reload after that symbol is added.
    Resolving at call time sidesteps the ordering entirely.
    """
    try:
        from bb.mcd.prefs.MelCustomDataUtilPreferences import GetUnityProjectRoot
        return GetUnityProjectRoot()
    except (ImportError, AttributeError):
        return ""


# Blender's file_format enum -> the extension we write. Only the formats worth
# handing to Unity; anything else falls back to the source file's own extension.
_FORMAT_EXTENSIONS = {
    'PNG': '.png',
    'JPEG': '.jpg',
    'JPEG2000': '.jp2',
    'TARGA': '.tga',
    'TARGA_RAW': '.tga',
    'TIFF': '.tif',
    'OPEN_EXR': '.exr',
    'OPEN_EXR_MULTILAYER': '.exr',
    'BMP': '.bmp',
    'HDR': '.hdr',
    'WEBP': '.webp',
}

_UNITY_READABLE = {'.png', '.jpg', '.jpeg', '.tga', '.tif', '.tiff',
                   '.exr', '.bmp', '.hdr', '.psd', '.gif', '.iff', '.pict'}


def _safeName(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def _collectImageNodes(node_tree, seen_trees):
    """Yield every TEX_IMAGE node in a tree, descending into node groups.

    Imported assets (PolyHaven, Sketchfab, USD) routinely bury their textures in
    nested groups, so a flat pass over mat.node_tree.nodes misses a lot of them.
    """
    if node_tree is None or node_tree in seen_trees:
        return
    seen_trees.add(node_tree)

    for node in node_tree.nodes:
        if node.type == 'TEX_IMAGE' and node.image is not None:
            yield node
        elif node.type == 'GROUP':
            for sub in _collectImageNodes(node.node_tree, seen_trees):
                yield sub


def _materialsInScene(scene):
    """Materials actually used by objects in this scene, plus world/nodes.

    Scoping to the scene keeps stale materials left over from earlier imports
    from dragging in textures nothing renders.
    """
    materials = []
    seen = set()
    for obj in scene.objects:
        for slot in obj.material_slots:
            mat = slot.material
            if mat is not None and mat.name not in seen:
                seen.add(mat.name)
                materials.append(mat)
    return materials


def _gatherImages(scene, all_materials: bool):
    """Return {image: [material names that use it]} for the relevant materials."""
    materials = list(bpy.data.materials) if all_materials else _materialsInScene(scene)

    usage = {}
    for mat in materials:
        if not mat.use_nodes:
            continue
        for node in _collectImageNodes(mat.node_tree, set()):
            usage.setdefault(node.image, []).append(mat.name)
    return usage


def _sourceExtension(image) -> str:
    """Best-guess extension for an image, preferring its original filename."""
    raw = image.filepath_raw or image.filepath or ""
    if not raw and image.packed_file is not None:
        raw = image.packed_file.filepath or ""
    ext = os.path.splitext(bpy.path.basename(raw))[1].lower()
    if ext in _UNITY_READABLE:
        return ext
    return _FORMAT_EXTENSIONS.get(image.file_format, '.png')


def _destinationName(image, taken: dict) -> str:
    """A collision-free filename for an image, preferring its original basename."""
    raw = image.filepath_raw or image.filepath or ""
    base = os.path.splitext(bpy.path.basename(raw))[0] if raw else ""
    if not base:
        base = os.path.splitext(image.name)[0]
    base = _safeName(base) or "texture"

    ext = _sourceExtension(image)
    candidate = base + ext

    # Two different images can share a basename (e.g. several assets each
    # shipping "material_baseColor.png"). Suffix rather than silently overwrite.
    if candidate.lower() in taken and taken[candidate.lower()] is not image:
        n = 1
        while True:
            candidate = f"{base}_{n}{ext}"
            if candidate.lower() not in taken:
                break
            n += 1

    taken[candidate.lower()] = image
    return candidate


def _writePacked(image, dest_path) -> bool:
    """Write an image's packed bytes straight to disk.

    Preferred over image.save() because it round-trips the original encoding
    exactly instead of re-compressing, and it needs no datablock mutation.
    """
    packed = image.packed_file
    if packed is None:
        return False
    data = packed.data
    if not data:
        return False
    with open(dest_path, 'wb') as f:
        f.write(data)
    return True


class CDU_OT_CopyTexturesToUnity(Operator):
    """Copy/unpack every texture used by this scene's materials into the Unity project"""
    bl_idname = "mel_export_scene.copy_textures_to_unity"
    bl_label = "Copy Textures To Unity"
    bl_options = {'REGISTER'}

    directory: StringProperty(subtype='DIR_PATH')

    all_materials: BoolProperty(
        name="All materials in file",
        description="Include materials not used by any object in this scene. \n Off by default so stale materials from earlier imports don't pull in textures nothing renders.",
        default=False)

    relink: BoolProperty(
        name="Relink images to copied files",
        description="Point this .blend's images at the copied files. \n Permanently repairs images whose original source path no longer exists, but modifies the .blend -- you must save for it to stick.",
        default=False)

    overwrite: BoolProperty(
        name="Overwrite existing",
        description="Re-copy textures that are already present in the destination folder",
        default=False)

    pack_urp_maps: BoolProperty(
        name="Pack URP metallic/smoothness maps",
        description="Also write one <base>_MetallicSmoothness.png per material set, \n combining roughness/metallic/AO into URP's layout (metallic=R, AO=G, smoothness=A). \n Roughness is inverted to smoothness. Source maps are still copied and are safe to delete afterwards.",
        default=False)

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        self.directory = self._defaultDirectory()
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "all_materials")
        layout.prop(self, "overwrite")
        layout.prop(self, "relink")
        layout.separator()
        layout.prop(self, "pack_urp_maps")

    def _defaultDirectory(self) -> str:
        """Guess a 'textures' folder beside the FBX for this .blend.

        The project convention is <room>/ble/<name>.blend next to <room>/fbx/,
        so a sibling <room>/textures/ keeps each room self-contained. Falls back
        to the Unity root, then to the .blend's own folder.
        """
        blend_path = bpy.data.filepath
        if blend_path:
            blend_dir = os.path.dirname(os.path.abspath(blend_path))
            # <room>/ble/foo.blend -> <room>/textures
            sibling = os.path.join(os.path.dirname(blend_dir), "textures")
            root = _getUnityProjectRoot()
            if not root or os.path.normcase(sibling).startswith(os.path.normcase(root)):
                return sibling + os.sep

        root = _getUnityProjectRoot()
        if root:
            return os.path.join(root, "Assets", "Art", "Textures") + os.sep
        return ""

    def execute(self, context):
        if not self.directory:
            self.report({'ERROR'}, "No destination folder chosen")
            return {'CANCELLED'}

        dest_dir = os.path.abspath(bpy.path.abspath(self.directory))

        usage = _gatherImages(context.scene, self.all_materials)
        if not usage:
            self.report({'WARNING'}, "No image textures found on the relevant materials")
            return {'CANCELLED'}

        try:
            os.makedirs(dest_dir, exist_ok=True)
        except OSError as e:
            self.report({'ERROR'}, f"Could not create '{dest_dir}': {e}")
            return {'CANCELLED'}

        copied = 0
        unpacked = 0
        skipped = 0
        missing = []
        failed = []
        taken = {}
        name_for_image = {}

        for image, users in usage.items():
            if image.source not in {'FILE', 'SEQUENCE'} and image.packed_file is None:
                # Generated/viewer/render-result images have no file to copy.
                continue

            filename = _destinationName(image, taken)
            # Recorded before any early-out below: packing reads pixels from the
            # Blender image, so it works even for textures we didn't need to copy.
            name_for_image[image] = filename
            dest_path = os.path.join(dest_dir, filename)

            if os.path.exists(dest_path) and not self.overwrite:
                skipped += 1
                if self.relink:
                    self._relink(image, dest_path)
                continue

            src_path = bpy.path.abspath(image.filepath) if image.filepath else ""
            src_path = os.path.normpath(src_path) if src_path else ""

            # Already living in the destination -- nothing to do.
            if src_path and os.path.normcase(src_path) == os.path.normcase(dest_path):
                skipped += 1
                continue

            try:
                if image.packed_file is not None and _writePacked(image, dest_path):
                    unpacked += 1
                elif src_path and os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    copied += 1
                else:
                    missing.append((image.name, image.filepath, users))
                    continue
            except (OSError, IOError) as e:
                failed.append((image.name, str(e)))
                continue

            if self.relink:
                self._relink(image, dest_path)

        packed_maps = None
        if self.pack_urp_maps:
            from bb.mcd.exporter.texture import PackUrpMaps
            packed_maps = PackUrpMaps.BuildPackedMaps(name_for_image, dest_dir, self.overwrite)

        self._report(dest_dir, copied, unpacked, skipped, missing, failed, packed_maps)
        return {'FINISHED'}

    def _relink(self, image, dest_path):
        """Repoint an image at the copied file and drop its packed copy."""
        try:
            if image.packed_file is not None:
                image.unpack(method='REMOVE')
        except RuntimeError:
            pass
        image.filepath = bpy.path.relpath(dest_path) if bpy.data.filepath else dest_path
        image.filepath_raw = image.filepath
        try:
            image.reload()
        except RuntimeError:
            pass

    def _report(self, dest_dir, copied, unpacked, skipped, missing, failed, packed_maps=None):
        # The console listing is the useful part -- a missing texture needs its
        # path and the materials affected, which won't fit in the status bar.
        if missing:
            print(f"\n[Argon] {len(missing)} texture(s) could not be found on disk and are not packed:")
            for name, path, users in missing:
                print(f"  - {name}  <-  {path or '(no path)'}")
                print(f"      used by: {', '.join(sorted(set(users)))}")
            print("  Fix: in Blender, File > External Data > Find Missing Files, or repack "
                  "(File > External Data > Pack Resources) on a machine where the files still exist.\n")

        if failed:
            print(f"\n[Argon] {len(failed)} texture(s) failed to write:")
            for name, err in failed:
                print(f"  - {name}: {err}")
            print()

        pack_errors = []
        if packed_maps is not None:
            results, pack_skipped, orphans, pack_errors = packed_maps
            print(f"\n[Argon] URP packing: wrote {len(results)} metallic/smoothness map(s)")
            for r in results:
                extras = []
                if r.has_metal:
                    extras.append("metallic")
                if r.has_ao:
                    extras.append("AO in G (assign to Occlusion too)")
                detail = (" + " + ", ".join(extras)) if extras else " (dielectric, metallic=0)"
                print(f"  - {r.filename}  {r.size[0]}x{r.size[1]}  smoothness{detail}")
            if pack_skipped:
                print(f"  {len(pack_skipped)} already present (enable Overwrite to rebuild)")
            if orphans:
                print(f"  {len(orphans)} set(s) had metallic/AO but no roughness to pair with -- not packed:")
                for base, roles in orphans:
                    print(f"    - {base}  ({', '.join(roles)})")
            if pack_errors:
                print(f"  {len(pack_errors)} FAILED:")
                for name, err in pack_errors:
                    print(f"    - {name}: {err}")
            print()

        parts = []
        if copied:
            parts.append(f"{copied} copied")
        if unpacked:
            parts.append(f"{unpacked} unpacked")
        if skipped:
            parts.append(f"{skipped} already present")
        if packed_maps is not None:
            parts.append(f"{len(packed_maps[0])} URP maps packed")
        if missing:
            parts.append(f"{len(missing)} MISSING")
        if failed or pack_errors:
            parts.append(f"{len(failed) + len(pack_errors)} FAILED")

        summary = ", ".join(parts) if parts else "nothing to do"
        level = {'ERROR'} if (failed or pack_errors) else ({'WARNING'} if missing else {'INFO'})
        detail = " (see System Console for details)" if (missing or failed or pack_errors) else ""
        self.report(level, f"Textures -> {dest_dir}: {summary}{detail}")


def register():
    bpy.utils.register_class(CDU_OT_CopyTexturesToUnity)


def unregister():
    bpy.utils.unregister_class(CDU_OT_CopyTexturesToUnity)
