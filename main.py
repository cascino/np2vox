import numpy as np 
from converter import MeshConverter

# usage examples

# create mesh converter object
voxmesh = MeshConverter()

# array to visualize
vox = np.random.randint(2, size=(30, 30, 30))
voxmesh.render_voxels(vox)

# animation example
voxlist = []
ind = np.random.rand(30, 60, 30)

for i in range(60):
    base = np.zeros((30, 60, 30))   
    base[ind > 0.98] = 1
    base[:, i+15:, :] = 0
    base[:, :i+12, :] = 0
    
    voxlist.append(base)

voxmesh.render_voxel_ani(voxlist, 50)
