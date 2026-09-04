"""Repack PBR channel maps into the single texture URP's Lit shader expects.

Every source this project pulls from lays its channels out differently, and none
of them match URP:

    AmbientCG       separate files: <base>_Roughness.jpg, <base>_Metalness.jpg,
                    <base>_AmbientOcclusion.jpg
    PolyHaven       one "arm" file:  AO=R  roughness=G  metallic=B
    glTF/Sketchfab  one "metallicRoughness" file: roughness=G  metallic=B
                    (Blender's glTF importer often re-splits this into
                     <base>_metallicRoughness_rough / _metal)

URP Lit reads metallic from R and *smoothness* from A of a single
_MetallicGlossMap (SampleMetallicSpecGloss in URP's LitInput.hlsl), and reads
occlusion from the GREEN channel of _OcclusionMap -- so AO can ride along in G
and the same texture can be assigned to both slots.

Output, which also matches HDRP's mask-map convention:

    R = metallic          (0 when there is no metal source -- correct for a dielectric)
    G = ambient occlusion (1 = unoccluded when there is no AO source)
    B = unused
    A = smoothness        (1 - roughness; NOT inverted when the source was gloss)

Written as PNG because the payload lives in the alpha channel and JPEG has none.
"""

import bpy
import json
import os

try:
    import numpy as np
except ImportError:  # Blender ships numpy; degrade to a clear message rather than a crash
    np = None


PACKED_SUFFIX = "_MetallicSmoothness"

# Sidecar the Unity importer reads to decide what to bind. Without it Unity
# can't tell a real AO channel from the constant 1.0 we write when there was no
# AO source, and would bind _OcclusionMap for nothing.
MANIFEST_NAME = "ArgonPackedMaps.json"
MANIFEST_VERSION = 1

# Tokens that identify what a map holds, checked longest-first within a role so
# "ambientocclusion" wins over "ao".
_ROLE_MARKERS = (
    ("packed_arm", ("arm", "orm", "rma")),                   # AO=R rough=G metal=B
    ("packed_mr", ("metallicroughness", "metalroughness")),  # rough=G metal=B
    ("smoothness", ("smoothness", "gloss")),                 # already smoothness
    ("roughness", ("roughness", "rough")),
    ("metallic", ("metalness", "metallic", "metalic", "metal")),
    ("occlusion", ("ambientocclusion", "occlusion", "ao")),
)

# Packed-map names that also appear as a middle token when an importer re-splits
# the map, e.g. "lambert1_metallicRoughness_rough". Stripping them from the base
# merges the split pair and the original packed file into one group.
_PACKED_TOKENS = ("metallicroughness", "metalroughness", "arm", "orm", "rma")

_NOISE_TOKENS = {"scale0", "scale1"}


def _isNoise(token: str) -> bool:
    """Resolution tags ("1k", "2048"), bare numbers, and known filler."""
    if token in _NOISE_TOKENS:
        return True
    body = token[:-1] if token.endswith("k") else token
    return len(body) > 0 and body.isdigit()


def ClassifyFilename(filename: str):
    """Return (base_name, role) for a texture filename, or (None, None).

    Drops meaningless tails ("_1k", "_scale0"), matches the trailing token
    against a channel marker, then strips a trailing packed-map token from the
    base so all three naming conventions collapse onto the same base:

        Wood053_2K-JPG_Roughness            -> ("wood053_2k_jpg", "roughness")
        Sofa_01_arm_1k                      -> ("sofa_01",        "packed_arm")
        lambert1_metallicRoughness          -> ("lambert1",       "packed_mr")
        lambert1_metallicRoughness_rough    -> ("lambert1",       "roughness")
    """
    stem = os.path.splitext(filename)[0]
    tokens = [t for t in stem.lower().replace("-", "_").replace(" ", "_").split("_") if t]

    end = len(tokens)
    while end > 0 and _isNoise(tokens[end - 1]):
        end -= 1
    if end == 0:
        return None, None
    meaningful = tokens[:end]

    for take in (2, 1):  # "nor_gl"-style two-token suffixes, then single tokens
        if len(meaningful) < take:
            continue
        tail = "".join(meaningful[-take:])
        for role, markers in _ROLE_MARKERS:
            if tail not in markers:
                continue
            base_tokens = meaningful[:-take]
            # "lambert1_metallicroughness" + role roughness -> base "lambert1"
            while base_tokens and base_tokens[-1] in _PACKED_TOKENS:
                base_tokens = base_tokens[:-1]
            return ("_".join(base_tokens) or stem.lower()), role

    return None, None


def _pixelCount(image) -> int:
    return image.size[0] * image.size[1]


def GroupByBase(name_for_image: dict):
    """Bucket {image: destination_filename} into {base: {role: image}}.

    When two images claim the same base and role -- e.g. an "_arm_1k" and an
    "_arm_2k" of the same material -- keep the higher resolution one.
    """
    groups = {}
    for image, filename in name_for_image.items():
        base, role = ClassifyFilename(filename)
        if base is None:
            continue
        roles = groups.setdefault(base, {})
        existing = roles.get(role)
        if existing is None or _pixelCount(image) > _pixelCount(existing):
            roles[role] = image
    return groups


def _readChannels(image):
    """Read an image as an (h, w, 4) float32 array of RAW stored values.

    Blender converts pixels to scene-linear on read according to the image's
    colorspace. Roughness/metallic/AO are data rather than colour, so force
    Non-Color for the read to get the values actually stored in the file.
    """
    if image.size[0] == 0 or image.size[1] == 0:
        return None

    previous = image.colorspace_settings.name
    restore = False
    if previous != "Non-Color":
        try:
            image.colorspace_settings.name = "Non-Color"
            restore = True
        except (TypeError, AttributeError):
            pass

    try:
        w, h = image.size
        buf = np.empty(w * h * 4, dtype=np.float32)
        image.pixels.foreach_get(buf)
        return buf.reshape(h, w, 4)
    finally:
        if restore:
            image.colorspace_settings.name = previous


def _readChannelsAt(image, width, height):
    """Read an image resampled to a size, without disturbing the original."""
    if image.size[0] == width and image.size[1] == height:
        return _readChannels(image)

    copy = image.copy()
    try:
        copy.scale(width, height)
        return _readChannels(copy)
    finally:
        bpy.data.images.remove(copy)


def _writeImage(name, arr, dest_path) -> None:
    """Write an (h, w, 4) array to a straight RGBA PNG.

    CHANNEL_PACKED matters: under straight or premultiplied alpha Blender applies
    alpha maths to RGB on save, which would corrupt the metallic channel
    everywhere smoothness is low.
    """
    h, w, _ = arr.shape
    img = bpy.data.images.new(name, width=w, height=h, alpha=True, float_buffer=False)
    try:
        img.colorspace_settings.name = "Non-Color"
        img.alpha_mode = "CHANNEL_PACKED"
        img.pixels.foreach_set(np.ascontiguousarray(arr, dtype=np.float32).reshape(-1))
        img.file_format = "PNG"
        img.filepath_raw = dest_path
        img.save()
    finally:
        # Don't leave a datablock behind in the user's .blend.
        bpy.data.images.remove(img)


class PackResult:
    def __init__(self, base, filename, sources, has_metal, has_ao, size):
        self.base = base
        self.filename = filename
        self.sources = sources
        self.has_metal = has_metal
        self.has_ao = has_ao
        self.size = size


def BuildPackedMaps(name_for_image: dict, dest_dir: str, overwrite: bool):
    """Write one packed map per material set.

    Returns (results, skipped, orphans, errors) where orphans are groups that
    carried metallic/AO but no roughness to anchor them.
    """
    if np is None:
        return [], [], [], [("numpy", "numpy is unavailable in this Blender build")]

    results = []
    skipped = []
    orphans = []
    errors = []

    for base, roles in sorted(GroupByBase(name_for_image).items()):
        has_rough_signal = any(roles.get(r) is not None
                               for r in ("packed_arm", "packed_mr", "roughness", "smoothness"))
        if not has_rough_signal:
            # A metal or AO map with nothing to pair it with. Emitting one would
            # mean inventing a smoothness value, so report instead of guessing.
            if roles.get("metallic") is not None or roles.get("occlusion") is not None:
                orphans.append((base, sorted(roles.keys())))
            continue

        filename = base + PACKED_SUFFIX + ".png"
        dest_path = os.path.join(dest_dir, filename)
        if os.path.exists(dest_path) and not overwrite:
            skipped.append(filename)
            continue

        try:
            result = _packOne(base, roles, filename, dest_path)
        except (RuntimeError, ValueError, MemoryError, OSError) as e:
            errors.append((filename, str(e)))
            continue

        if result is not None:
            results.append(result)

    if results or skipped:
        try:
            _writeManifest(dest_dir, results)
        except (OSError, IOError) as e:
            errors.append((MANIFEST_NAME, str(e)))

    return results, skipped, orphans, errors


def _writeManifest(dest_dir, results) -> None:
    """Merge this run's entries into the folder's manifest.

    Merged rather than overwritten so packing one room's subset doesn't drop
    entries written by an earlier run into the same folder.
    """
    path = os.path.join(dest_dir, MANIFEST_NAME)

    entries = {}
    if os.path.isfile(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            for item in existing.get("maps", []):
                if "base" in item:
                    entries[item["base"]] = item
        except (ValueError, OSError):
            pass  # unreadable/stale manifest is replaced rather than fatal

    for r in results:
        entries[r.base] = {
            "base": r.base,
            "file": r.filename,
            "metal": bool(r.has_metal),
            "ao": bool(r.has_ao),
        }

    payload = {
        "version": MANIFEST_VERSION,
        "maps": [entries[k] for k in sorted(entries)],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)


def _packOne(base, roles, filename, dest_path):
    packed_src = roles.get("packed_arm") or roles.get("packed_mr")
    rough_src = roles.get("roughness")
    gloss_src = roles.get("smoothness")
    metal_src = roles.get("metallic")
    ao_src = roles.get("occlusion")

    # A dedicated roughness map defines the output resolution; fall back to the
    # packed map when that's all there is.
    primary = rough_src or gloss_src or packed_src
    primary_arr = _readChannels(primary)
    if primary_arr is None:
        return None
    h, w, _ = primary_arr.shape

    def read(src):
        if src is None:
            return None
        return primary_arr if src is primary else _readChannelsAt(src, w, h)

    packed_arr = read(packed_src)
    out = np.zeros((h, w, 4), dtype=np.float32)

    # --- A: smoothness. Dedicated maps win over the packed map. ---------------
    if gloss_src is not None:
        out[:, :, 3] = read(gloss_src)[:, :, 0]          # already smoothness
    elif rough_src is not None:
        out[:, :, 3] = 1.0 - read(rough_src)[:, :, 0]    # invert; URP wants smoothness
    elif packed_arr is not None:
        out[:, :, 3] = 1.0 - packed_arr[:, :, 1]         # roughness sits in G

    # --- R: metallic ----------------------------------------------------------
    has_metal = False
    if metal_src is not None:
        out[:, :, 0] = read(metal_src)[:, :, 0]
        has_metal = True
    elif packed_arr is not None:
        out[:, :, 0] = packed_arr[:, :, 2]               # metallic sits in B
        has_metal = True
    # else leave 0.0 -- correct for a dielectric

    # --- G: ambient occlusion -------------------------------------------------
    has_ao = False
    if ao_src is not None:
        out[:, :, 1] = read(ao_src)[:, :, 0]
        has_ao = True
    elif roles.get("packed_arm") is not None and packed_arr is not None:
        # Only the arm/orm convention defines AO in R. A glTF metallicRoughness
        # texture leaves R undefined, so don't guess there.
        out[:, :, 1] = packed_arr[:, :, 0]
        has_ao = True
    else:
        out[:, :, 1] = 1.0                               # unoccluded

    np.clip(out, 0.0, 1.0, out=out)
    _writeImage(filename, out, dest_path)

    consumed = [img for img in (rough_src, gloss_src, metal_src, ao_src, packed_src)
                if img is not None]
    return PackResult(base, filename, consumed, has_metal, has_ao, (w, h))
