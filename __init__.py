bl_info = {
    "name": "Sphere Topologies",
    "blender": (2, 80, 0),
    "category": "Mesh",
}

from . import main

def register():
    main.register()


def unregister():
    main.unregister()
