import numpy as np
from math import floor
from scipy.spatial import Delaunay

'''SOURCE: https://www.redblobgames.com/x/1842-delaunay-voronoi-sphere/'''


def stereographicProjection(verts, origin_verts, radius, transform):
    """
    0 = original sphere, 1 = full stereographic projection from bottom point

    :param origin_verts: original verts list (read only)
    :param float radius:
    :param verts: bmesh vertes list to modify
    :param float transform:
    """
    error_margin = 0.001 * np.ones(3)
    origin = np.array([0, 0, -radius])
    for i, v in enumerate(verts):
        coord = np.array(origin_verts[i])
        if not (coord - origin <= error_margin).all():
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


def delaunayTriangulate(mesh, bm):
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

