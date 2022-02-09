from fenics import *
from dolfin_adjoint import *
import numpy as np
import moola


def compute_optimal_coefficient(mesh, V, Vs, params, deformation, def_boundary_parts,
                                zero_boundary_parts, boundaries, output_directory):

    u = Function(V)
    v = TestFunction(V)

    # boundary conditions
    bc = []
    bc2 = []
    zero = Constant(("0.0", "0.0"))
    zeros = Constant(0.)
    for i in def_boundary_parts:
        bc.append(DirichletBC(V, deformation, boundaries, params[i]))
    for i in zero_boundary_parts:
        bc.append(DirichletBC(V, zero, boundaries, params[i]))
        bc2.append(DirichletBC(Vs, zeros, boundaries, params[i]))

    ufile = File(output_directory + "displacement.pvd")
    afile = File(output_directory + "alpha_opt.pvd")

    # solve optimal control problem
    alpha = interpolate(Constant("0.0"), Vs)

    b = Function(Vs)
    vb = TestFunction(Vs)
    E1 = inner(grad(b), grad(vb))*dx(mesh) - inner(alpha, vb)*dx(mesh)
    solve(E1 == 0, b, bc2)


    E = inner((1.0 + b) * (grad(u) + grad(u).T), grad(v) + grad(v).T) * dx(mesh)

    # solve PDE
    solve(E == 0, u, bc)

    # save initial
    up = project(u, V)
    upi = project(-1.0 * u, V)
    ALE.move(mesh, up, annotate=False)
    ufile << up
    afile << alpha
    ALE.move(mesh, upi, annotate=False)

    # J
    eta = 1e-3
    J = assemble(pow((1.0 / (det(Identity(2) + grad(u))) + det(Identity(2) + grad(u))), 2) * dx(mesh) + 0.5 * eta * (
                inner(alpha, alpha) + inner(grad(alpha), grad(alpha))) * dx(mesh))
    control = Control(alpha)

    def Hinit(x):
        w = Function(Vs)
        w.vector().set_local(x)
        u = TrialFunction(Vs)
        v = TestFunction(Vs)
        a = (inner(u, v) + inner(grad(u), grad(v))) * dx(mesh)
        L = inner(w, v) * dx(mesh)
        A, b = PETScMatrix(), PETScVector()
        assemble_system(a, L, [], A_tensor=A, b_tensor=b)
        u = Function(Vs)
        solve(A, u.vector(), b)
        return moola.DolfinPrimalVector(u)

    rf = ReducedFunctional(J, control)

    problem = MoolaOptimizationProblem(rf)
    alpha_moola = moola.DolfinPrimalVector(alpha)
    solver = moola.BFGS(problem, alpha_moola,
                        options={'jtol': 0, 'gtol': 1e-9, 'Hinit': Hinit, 'maxiter': 100, 'mem_lim': 10})

    sol = solver.solve()
    alpha_opt = sol['control'].data

    b_opt = Function(Vs)
    E1 = inner(grad(b_opt), grad(vb)) * dx(mesh) - inner(alpha_opt, vb) * dx(mesh)
    solve(E1 == 0, b_opt, bc2)

    # solve u_opt
    E = inner((1.0 + b_opt) * (grad(u) + grad(u).T), grad(v)) * dx(mesh)
    solve(E == 0, u, bc)

    up = project(u, V)
    upi = project(-u, V)
    ALE.move(mesh, up, annotate=False)
    ufile << up
    afile << b_opt
    ALE.move(mesh, upi, annotate=False)

    # breakpoint()
    normgradtraf = project(inner(0.5 * (grad(u) + grad(u).T), 0.5 * (grad(u) + grad(u).T)), Vs)

    xdmf = XDMFFile(output_directory + "optimal_control_data.xdmf")

    xdmf.write_checkpoint(b_opt, "alpha_opt", 0, append=True)
    xdmf.write_checkpoint(normgradtraf, "normgradtraf", 0, append=True)
