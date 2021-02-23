import numpy as np
from math import floor
from scipy.spatial import Delaunay
import bmesh
from funcs.general_functions import getFlatAngle

'''SOURCE: https://www.redblobgames.com/x/1842-delaunay-voronoi-sphere/'''


def stereographicProjection(verts, origin_verts, radius, transform):
    """
    0 = original sphere, 1 = full stereographic projection from bottom point

    :param origin_verts: original verts list (read only)
    :param float radius:
    :param verts: bmesh vertes list to modify
    :param float transform:
    """
    error_margin = 0.001 * np.ones(3)  # mandated by the delaunay transform
    origin = np.array([0, 0, -radius])
    for i, v in enumerate(verts):
        coord = np.array(origin_verts[i])
        if (coord - origin <= error_margin).all():
            # stereographic project doesn't work if the point is too close to the south pole (the projection goes to infinity),
            # so manually put it at a very long distance (could cause problems for very dense sphere,
            # in that case you would need to further increase teh distance)
            corrected_coords = [1, np.random.rand() * 2 - 1, -radius + error_margin[
                2]]  # introduce randomness in case there are more than one problematic points
            sp = np.array([project(radius, corrected_coords[0], corrected_coords[2]),
                           project(radius, corrected_coords[1], corrected_coords[2]), -1])
        else:
            sp = np.array([project(radius, coord[0], coord[2]), project(radius, coord[1], coord[2]), -1])
        v.co = sp * (1 - transform) + transform * coord


def project(radius, ordinates, z):
    """
    given two points (0,-radius), (ordinates, z) find the line that goes trough them and get the ordinate of it's intersection with the horizontal axis

    :param radius:
    :param ordinates:
    :param z:
    """
    return radius * ordinates / (z + radius)


def delaunayTriangulate(mesh, bm, threshold=0.8):
    """
    given a <mesh> and Bmesh <bm>, flatten the mesh with stereographic project, create a certain number of faces and restore the original shape og the sphere

    number of faces and final form are controlled through the sphere_transform and sphere_transform2 properties

    :param threshold: sphere_transform value after which the bottom hole is filled (set to 0 to always fill it, 1 to never fill it)
    :param mesh:
    :param bm:
    :return:
    """
    props = mesh.SphereTopology
    iterations = floor(props.sphere_transform2 * props.sphere_resolution)
    if iterations < 1:
        stereographicProjection(bm.verts, mesh['verts'], props.sphere_radius, props.sphere_transform)
        return

    verts_list = list(bm.verts)

    # project the copied vertices on plane
    stereographicProjection(bm.verts, mesh['verts'], props.sphere_radius, 0)

    # randomly remove excess vertices to copied list (= ignore them) to allow animation of Delaunay triangulation
    ratio = 3. - 5. ** 0.5
    for i in range(props.sphere_resolution - iterations):
        print(floor(((i * ratio) % 1) * (props.sphere_resolution - i)))
        verts_list.pop(floor(((i * ratio) % 1) * (props.sphere_resolution - i)))

    points = [[v.co[0], v.co[1]] for v in
              verts_list]  # create list of points (if transform2<1, some points will be ignored)

    # run delauney triangulation and add faces
    tri = Delaunay(points)
    for face in tri.simplices:  # face is a list of the indices of the 3 vertices
        bm.faces.new([verts_list[index] for index in face])
        bm.faces.ensure_lookup_table()

    # re-project back to shape defined by transform2
    stereographicProjection(bm.verts, mesh['verts'], props.sphere_radius, props.sphere_transform)

    # after the <threshold>, fill the gap at the bottom of the mesh with triangles (might not match the Delauney pattern)
    if props.sphere_transform2 > threshold:
        border_verts = sorted([v for v in bm.verts if v.is_boundary], key=lambda v: getFlatAngle(v.co))
        new_face = bm.faces.new(border_verts)
        # noinspection PyArgumentList
        bmesh.ops.triangulate(bm, faces=[new_face])
