import bpy
import bmesh
import numpy as np

import sys, os

filePath = os.path.dirname(bpy.data.filepath)
if filePath not in sys.path:
    sys.path.append(filePath)

import general_functions
import SpherifiedCube

print("Executing test.py")


def generateMesh():
    (obj, mesh) = general_functions.createNewEmptyObject(SpherifiedCube.LABEL)

    # create BMesh
    radius = 2
    res = 4
    transform = 0
    bm = bmesh.new()
    print("ciao")
    SpherifiedCube.placeAllVertices(bm, 3, radius, transform)
    bm.to_mesh(mesh)
    bm.free()


generateMesh()
