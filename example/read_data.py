from dolfin import *
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '../FSIsolver/extension_operator')
import extension
sys.path.insert(1, '../FSIsolver/fsi_solver')
import solver
sys.path.insert(1, '../learnExt')
from NeuralNet.neural_network_custom import ANN, generate_weights
from coeff_machine_learning import NN_der

# create mesh: first create mesh by running ./create_mesh/create_mesh_FSI.py

# load mesh
mesh = Mesh()
with XDMFFile("./../Output/Mesh_Generation/mesh_triangles.xdmf") as infile:
    infile.read(mesh)
mvc = MeshValueCollection("size_t", mesh, 2)
mvc2 = MeshValueCollection("size_t", mesh, 2)
with XDMFFile("./../Output/Mesh_Generation/facet_mesh.xdmf") as infile:
    infile.read(mvc, "name_to_read")
with XDMFFile("./../Output/Mesh_Generation/mesh_triangles.xdmf") as infile:
    infile.read(mvc2, "name_to_read")
boundaries = cpp.mesh.MeshFunctionSizet(mesh, mvc)
domains = cpp.mesh.MeshFunctionSizet(mesh,mvc2)
bdfile = File("./../Output/Mesh_Generation/boundary.pvd")
bdfile << boundaries
bdfile = File("./../Output/Mesh_Generation/domains.pvd")
bdfile << domains

# boundary parts
params = np.load('../Output/Mesh_Generation/params.npy', allow_pickle='TRUE').item()

params["no_slip_ids"] = ["noslip", "obstacle_fluid", "obstacle_solid"]

# subdomains
fluid_domain = MeshView.create(domains, params["fluid"])
solid_domain = MeshView.create(domains, params["solid"])

# function space
T = VectorElement("CG", fluid_domain.ufl_cell(), 2)
FS = FunctionSpace(fluid_domain, MixedElement(T, T))

# read data
xdmf_input = XDMFFile("../Output/Extension/Data/input.xdmf")
xdmf_output = XDMFFile("../Output/Extension/Data/output.xdmf")

input = Function(FS)
output = Function(FS)

i = 0
error = False
while not error:
    try:
        xdmf_input.read_checkpoint(input, "input", i)
        xdmf_output.read_checkpoint(output, "output", i)
        i = i+1
    except:
        error = True