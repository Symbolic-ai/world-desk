"""Builds the 3D models for World Desk in Blender and exports GLB files.

Run: /Applications/Blender.app/Contents/MacOS/Blender -b -P tools/build_models.py
Material names are the contract with the game: Hull, Brass, Accent, Windows, Panel, Glass, Dark.
"""
import bpy, math, os
from mathutils import Vector

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'models')


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def mat(name, color, metal=0.0, rough=0.4, emit=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1)
        b.inputs['Emission Strength'].default_value = strength
    return m


def finish(obj, material, bevel=0.0, smooth=True, subsurf=0):
    obj.data.materials.clear()
    obj.data.materials.append(material)
    if bevel:
        mod = obj.modifiers.new('bevel', 'BEVEL'); mod.width = bevel; mod.segments = 3; mod.limit_method = 'ANGLE'
    if subsurf:
        mod = obj.modifiers.new('sub', 'SUBSURF'); mod.levels = subsurf; mod.render_levels = subsurf
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
        if hasattr(obj.data, 'set_sharp_from_angle'):
            obj.data.set_sharp_from_angle(angle=math.radians(40))
    return obj


def active():
    return bpy.context.view_layer.objects.active


def export(name):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, name + '.glb'), export_format='GLB', export_apply=True,
                              use_selection=True, export_yup=True)


# ---------------------------------------------------------------- hub station
reset()
HULL = mat('Hull', (0.86, 0.83, 0.76), metal=0.65, rough=0.32)
BRASS = mat('Brass', (0.80, 0.62, 0.36), metal=1.0, rough=0.25)
ACCENT = mat('Accent', (0.93, 0.15, 0.13), metal=0.2, rough=0.35)
WIN = mat('Windows', (1.0, 0.85, 0.6), emit=(1.0, 0.8, 0.55), strength=6.0)
DARK = mat('Dark', (0.05, 0.06, 0.1), metal=0.5, rough=0.5)
GLASS = mat('Glass', (0.1, 0.2, 0.5), metal=0.2, rough=0.05)

# Habitat ring (Blender Z is up; glTF export converts to Y up).
bpy.ops.mesh.primitive_torus_add(major_radius=0.62, minor_radius=0.075, major_segments=96, minor_segments=24)
finish(active(), HULL)
# Window band around the outer equator of the ring
bpy.ops.mesh.primitive_torus_add(major_radius=0.692, minor_radius=0.012, major_segments=96, minor_segments=8)
finish(active(), WIN)
# Brass trim rings above and below the windows
for z in (-0.045, 0.045):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.66, minor_radius=0.01, major_segments=96, minor_segments=8, location=(0, 0, z))
    finish(active(), BRASS)
# Habitat pods on the ring
for i in range(12):
    a = i / 12 * math.tau
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, segments=24, ring_count=12, location=(math.cos(a) * 0.62, math.sin(a) * 0.62, 0.06))
    pod = active(); pod.scale = (1, 1, 0.55)
    finish(pod, ACCENT if i % 3 == 0 else HULL)
# Spokes
for i in range(6):
    a = i / 6 * math.tau + math.tau / 24
    mid = Vector((math.cos(a) * 0.36, math.sin(a) * 0.36, 0))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.5, vertices=16, location=mid, rotation=(0, math.pi / 2, a))
    finish(active(), BRASS)
# Central hub: a drum with two domes
bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.12, vertices=48)
finish(active(), HULL, bevel=0.012)
bpy.ops.mesh.primitive_cylinder_add(radius=0.152, depth=0.018, vertices=48)
finish(active(), WIN)
for z, s in ((0.06, 1), (-0.06, -1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=48, ring_count=24, location=(0, 0, z))
    d = active(); d.scale = (1, 1, 0.55 * s)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
    for v in d.data.vertices:
        v.select = v.co.z < -0.001
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT')
    finish(d, GLASS if s > 0 else HULL)
# Mast and dish on top, thruster below
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.36, vertices=12, location=(0, 0, 0.26))
finish(active(), BRASS)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.022, segments=16, ring_count=8, location=(0, 0, 0.45))
finish(active(), ACCENT)
bpy.ops.mesh.primitive_cone_add(radius1=0.09, radius2=0.012, depth=0.05, vertices=40, location=(0.0, 0.0, 0.34), rotation=(math.pi, 0, 0))
finish(active(), HULL)
bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.08, depth=0.1, vertices=32, location=(0, 0, -0.16), rotation=(math.pi, 0, 0))
finish(active(), DARK)
bpy.ops.mesh.primitive_cylinder_add(radius=0.052, depth=0.01, vertices=32, location=(0, 0, -0.21))
finish(active(), mat('Thruster', (0.3, 0.55, 1.0), emit=(0.3, 0.55, 1.0), strength=8.0))
export('hub')

# ---------------------------------------------------------------- satellite
reset()
FOIL = mat('Foil', (0.85, 0.62, 0.25), metal=1.0, rough=0.38)
HULL = mat('Hull', (0.86, 0.83, 0.76), metal=0.65, rough=0.32)
PANEL = mat('Panel', (0.05, 0.12, 0.35), metal=0.6, rough=0.22)
BRASS = mat('Brass', (0.80, 0.62, 0.36), metal=1.0, rough=0.25)
ACCENT = mat('Accent', (0.93, 0.15, 0.13), metal=0.2, rough=0.35)
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.14, vertices=8)
finish(active(), FOIL, bevel=0.006)
bpy.ops.mesh.primitive_cylinder_add(radius=0.062, depth=0.012, vertices=8, location=(0, 0, 0.074))
finish(active(), HULL)
for s in (-1, 1):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(s * 0.2, 0, 0))
    p = active(); p.scale = (0.24, 0.1, 0.006)
    finish(p, PANEL, bevel=0.002, smooth=False)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.08, vertices=8, location=(s * 0.07, 0, 0), rotation=(0, math.pi / 2, 0))
    finish(active(), BRASS)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, segments=32, ring_count=16, location=(0, 0, 0.13))
dish = active(); dish.scale = (1, 1, 0.35)
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='DESELECT'); bpy.ops.object.mode_set(mode='OBJECT')
for v in dish.data.vertices:
    v.select = v.co.z > 0.001
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.delete(type='VERT'); bpy.ops.object.mode_set(mode='OBJECT')
finish(dish, HULL)
bpy.ops.mesh.primitive_cylinder_add(radius=0.004, depth=0.07, vertices=8, location=(0, 0, 0.14))
finish(active(), BRASS)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.01, segments=12, ring_count=6, location=(0, 0, 0.18))
finish(active(), ACCENT)
export('satellite')
print('MODELS_OK')
