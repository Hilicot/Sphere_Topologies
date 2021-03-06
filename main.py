# Copyright (c) 2021 Marco Porro
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
# AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


bl_info = {
    "name": "Sphere Topologies",
    "blender": (2, 80, 0),
    "category": "Mesh",
}

import bpy

# add script folder to path if not present TODO: removable if deployed
import sys
import os

filePath = os.path.dirname(bpy.data.filepath)
if filePath not in sys.path:
    sys.path.append(filePath)

import gui
from funcs import general_functions
from Topologies import RandomSphere, FibonacciSphere, Icosahedron, SpherifiedCube, RadialSphere, TruncatedIcosahedron

modules = {
    RadialSphere.LABEL: RadialSphere,
    SpherifiedCube.LABEL: SpherifiedCube,
    Icosahedron.LABEL: Icosahedron,
    TruncatedIcosahedron.LABEL: TruncatedIcosahedron,
    RandomSphere.LABEL: RandomSphere,
    FibonacciSphere.LABEL: FibonacciSphere
}
previous_frame = -1


def trigger_update_on_frame_change(scene, depsgraph):
    global previous_frame
    if scene.frame_current != previous_frame:
        previous_frame = scene.frame_current
        for obj in scene.objects:
            if obj.type == 'MESH' and obj.data.SphereTopology.sphere_type != "null":
                mesh_eval = obj.data.evaluated_get(depsgraph)
                general_functions.sphereUpdateIfNeeded(mesh_eval)


# function triggered by manual update of Resolution properties
def updateResolution(self=None, context=bpy.context):
    """
    Called when Resolution property changes.
    Calls the updateSphereResolution function of the appropriate module

    :param self:
    :param context:
    :return None:
    """
    mesh = general_functions.getCurrentBMesh()

    if mesh is None or not mesh.SphereTopology.sphere_do_update:
        return

    _type = mesh.SphereTopology.sphere_type
    if _type == "null":
        print("Mesh was not created by the Sphere Topology module")
    else:
        mod = modules[_type]
        mod.updateSphereResolution(mesh)


# function triggered by manual update of transform/radius properties
def updateTransform(self=None, context=bpy.context):
    """
    Called when Radius/Transform properties change.
    Calls the morphSphere function of the appropriate module

    :param self:
    :param context:
    :return None:
    """
    mesh = general_functions.getCurrentBMesh()
    if mesh is None or not mesh.SphereTopology.sphere_do_update:
        return

    _type = mesh.SphereTopology.sphere_type
    if _type == "null":
        print("Mesh was not created by the Sphere Topology module")
    else:
        mod = modules[_type]
        mod.morphSphere(mesh)


def register():
    # TODO: for a regular addon, this duplicates should be removed (but useful when debugging stuff)
    try:
        for mod in modules.values():
            mod.unregister()
    except RuntimeError:
        pass
    try:
        gui.unregister()
    except RuntimeError:
        pass

    for mod in modules.values():
        mod.register()

    gui.register()

    bpy.app.handlers.frame_change_post.append(trigger_update_on_frame_change)


def unregister():
    for mod in modules.values():
        mod.unregister()
    gui.unregister()

    bpy.app.handlers.frame_change_pre.remove(trigger_update_on_frame_change)


if __name__ == "__main__":
    register()
