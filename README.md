# Sphere Topologies
Let's compare some topologies of spheres and see how they behave. This code is what I used to generate them

##### IMPORTANT DISCLAIMER
This code was made for me only, to generate and animate different sphere meshes inside Blender 2.90 for visual representation. 
This project is made to work as a Blender script that is able to create spheres and dynamically change its properties, 
so in the code there will be additional step that are not stricly concerned with the mesh generation.
This also means the code is poorly documented and absolutely not bug free. 
While the code works and can used in Blender, it comes as is, and it's probably more useful as a reference rather than a solid code base.

---
## Sphere types
Here there is a brief description of the different topologies with the relative pseudocode used to generate its vertices.
For more detailed code, feel free to look at the python files, but remember what is was written in the previous disclaimer

1. ##### Radial Sphere 
    Probably the most intuitive one, because it's built using basic trigonometry.
    Like the Earth's coordinates it is based on parallels and meridians, which means that this topology requires 2 numbers to define its resolution.
    Depending on the context, it can be very bad:
    * The distribution of vertices is not regular (near the pole there are more and closer together) 
    * Faces have different shape and size
    * Some faces have a different number of vertices from the others (they are quads in the middles, triangles near the poles)
    * Having an high number of meridians and low number of parallels (or viceversa) can produce weird results

        ```
        for p in range(parallels_num):
            plane_z = (1 - (2 * p) / (parallels_num - 1))
            teta = plane_z * pi / 2
            for m in range(meridians_num):
                phi = m / (meridians_num - 1) * 2 * pi
                addVertex([
                    radius * cos(phi) * cos(teta),
                    radius * sin(phi) * cos(teta),
                    radius * sin(teta)
                ])
        ```
1. ##### Spherified Cube
    Basically take a cube and normalize each vertex (so move it so that its distance from the center is equal to the final radius of the sphere).
    It's still quite intuitive to picture, not so much to code it.
    It still has problems:
    * Faces have different shape and size
    * The distribution of vertices is not regular (near the corners of the originating cube there are more and closer together)
    * unnecessarily complex

        ```
        k = resolution + 1
        for face in range(6):
            for j in range(k):
                for i in range(k):
                    addVertex(getTransformedCoordinates(face, i, j, resolution, radius))
                    
        def getTransformedCoordinates(face, i, j, resolution, radius):
            step = 1 / resolution
            step3 = np.ones(3) * step
            j3 = np.ones(3) * j
            i3 = np.ones(3) * i
            cube_coords = origin[face] * radius + step3 * (i3 * right[face] + j3 * up[face]) * radius * 2
            return normalize(cube_coords, radius)
        ```        
1. ##### Icosahedron
    Create a base icosahedron, then subdivide each face until you reach the desired resolution.
    The easiest way to generate the basic mesh is to hard code it (see [here](https://github.com/Hilicot/Sphere_Topologies/blob/334f1b12382f4a85f1754264d12651a8a8fe3577/Topologies/Icosahedron.py#L151)),
    and you get a 12 vertex solid with all identical triangular faces.
    
    Pros:
    * All faces are exactly identical
    * All vertices are equidistant from their neighbour (constant vertex density)
    
    Cons:
    * Each subdivision, from 1 face you create 4 new ones, 
    so the number of faces grows exponentially and you can't easily control it's vertex count.
        The geometric progression goes like: 20, 80, 320, 1280, 5120, 20480, ...
    
        ```
        mesh = generateBaseIcosahedron()
        for i in range(iterations):    
            for edge in mesh.edges:
                # get median point position, normalize and create median vertex
                co = [edge.verts[0].co[i] + edge.verts[1].co[i] for i in range(3)]
                addVertex(normalize(co, radius))
        ```
1. ##### Fibonacci Sphere
    This is a really simple, yet quite powerful, topology. 
    It's based on the golden angle to place the vertices on a spiral and achieve a very good vertex density
    The faces can be easily generated with Delauney Triangulation
    
    Pros:
    * Very fast to calculate
    * Faces have all similar size (but not exactly equal)
    * When you animate it it looks absolutely bonkers
    * Can be created with any number of vertices (so it's very granular)
    Cons:
    * Faces still have different shapes
    * The poles are the 2 ends of the spiral, so they can have a different local topology

        ```      
        phi = pi * (3 - sqrt(5))  # golden angle (radians)
        for i in range(res):
            theta = phi * i
            z = radius * (- 1 + (i / (res - 1)) * 2)
            x = radius * cos(theta) * sqrt(1 - z * z)
            y = radius * sin(theta) * sqrt(1 - z * z)
            addVertex([x, y, z])
        ```
1. ##### Random Sphere

    This is not a good topology: you need many points and the surface has areas of much higher density then others.
    This could be solved with a stronger pseudo-random generator, but it would still be bad
    The faces can be easily generated with Delauney Triangulation
        
         ```       
        for i in range(res):
            # generate random rotation angle and latitude
            phi = random() * 2 * pi
            latitude = radius * 2*random()-1
            dist = (radius ** 2 - latitude ** 2) ** 0.5
            
            addVertex([
                cos(phi) * dist,
                sin(phi) * dist,
                latitude
            ])
         ```   

### Sources
Very good article on Delauney Triangulation and Voronoi regions -> https://www.redblobgames.com/x/1842-delaunay-voronoi-sphere/
GitHub post on some basic topologies --> https://github.com/caosdoar/spheres