"""
general functions for all scripts in the Sphere Topologies package
"""

import bpy
import bmesh
import main
from math import atan2, pi


def createNewEmptyObject(objName="new Empty Object"):
    """
    Create new empty object and and empty mesh

    :rtype (Object, Mesh):
    :param objName:
    """
    # create a new object, which mesh will be replaced by the new BMesh
    mesh = bpy.data.meshes.new(objName)
    obj = bpy.data.objects.new(objName, mesh)
    obj.location = bpy.context.scene.cursor.location
    bpy.context.collection.objects.link(obj)

    # set object as active
    bpy.context.view_layer.objects.active = obj

    return obj, mesh


def getCurrentBMesh():
    """
    return the mesh of the active object, None if there is no active object

    :return mesh:
    """
    # if there aren't active objects, return error
    if bpy.context.object is None:
        print("No object is selected!")
        return None, None

    return bpy.context.object.data


def defineVertex(bm, index, coordinates) -> None:
    """
    define a vertex of a bmesh: if a vertex with index <index> exists, modify its coordinates, else append a new vertex after the last existing vertex


    :param bmesh bm:
    :param int index:
    :param list coordinates: list of 3 float numbers, coordinates on XYZ axis
    """
    verts = bm.verts
    current_len = len(verts)
    verts.ensure_lookup_table()

    if index < current_len:
        verts[index].co = coordinates
    else:
        verts.new(coordinates)


def removeExcessBMElem(l, correct_length):
    """
    removes vertices, edges or faces with index > correct_length

    :param BMElemSeq l: list of BMesh elements, like bm.vert, bm.edges or bm.faces
    :param int correct_length:
    """
    l.ensure_lookup_table()
    length = len(l)
    i = length - correct_length
    while i > 0:
        l.remove(l[correct_length + i - 1])
        l.ensure_lookup_table()
        i -= 1


def normalizeVert(v, radius):
    """
    Normalize vertex <v> by placing it at distance <radius> from the origin along the same normal direction

    :param vertex v: vertex
    :param float radius:
    """
    # calculate current distance
    dist = (v.co.x ** 2 + v.co.y ** 2 + v.co.z ** 2) ** 0.5

    # normalize
    for axis in range(3):
        v.co[axis] = v.co[axis] / dist * radius


def normalize(coords, radius):
    """
    Normalize a list of 3 coordinates relative to the origin

    :param coords:
    :param radius:
    :return co:
    """
    co = coords.copy()
    # calculate current distance
    dist = (coords[0] ** 2 + coords[1] ** 2 + coords[2] ** 2) ** 0.5
    # normalize
    for axis in range(3):
        co[axis] = coords[axis] / dist * radius
    return co


def getFlatAngle(vert):
    return atan2(vert[1], vert[0])+2*pi


def insertFace(bm, v):
    """
    insert face using an array of vertices indices

    :param bm:
    :param v: list of vertices indices
    """
    a = []
    for k in range(len(v)):
        a.append(bm.verts[v[k]])
    f = bm.faces.new(a)
    bm.faces.ensure_lookup_table()
    return f


def setSphereUpdated(props):
    props.sphere_old_resolution = props.sphere_resolution * props.sphere_resolution2 + props.sphere_transform2
    props.sphere_old_transradius = props.sphere_transform + props.sphere_radius


def sphereUpdateIfNeeded(mesh):
    props = mesh.SphereTopology
    if props.sphere_old_resolution != props.sphere_resolution * props.sphere_resolution2 + props.sphere_transform2:
        main.modules[props.sphere_type].updateSphereResolution(mesh)
    elif props.sphere_old_transradius != props.sphere_transform + props.sphere_radius:
        main.modules[props.sphere_type].morphSphere(mesh)


def printAllProps(props):
    return "%s -> %d = %d * %d, %f = %f + %f" % (
        props.sphere_type, props.sphere_old_resolution, props.sphere_resolution,
        props.sphere_resolution2, props.sphere_old_transradius, props.sphere_radius, props.sphere_transform)
