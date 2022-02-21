from fenics import *
from dolfin_adjoint import *
import numpy as np
import moola
from coeff_machine_learning import NN_der

def smoothmax(r, eps=1e-4):
    return conditional(gt(r, eps), r - eps / 2, conditional(lt(r, 0), 0, r ** 2 / (2 * eps)))

def compute_optimal_coefficient_new(mesh, V, Vs, params, deformation, def_boundary_parts,
                                zero_boundary_parts, boundaries, output_directory, net=None, threshold=None):
    u = Function(V)
    v = TestFunction(V)

    # boundary conditions
    #bc = DirichletBC(V, deformation, "on_boundary")
    #bc2 = []
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

    set_working_tape(Tape())

    # solve optimal control problem
    alpha = interpolate(Constant("0.0"), Vs)

    b = Function(Vs)
    vb = TestFunction(Vs)
    E1 = inner(grad(b), grad(vb)) * dx(mesh) - inner(alpha, vb) * dx(mesh)
    solve(E1 == 0, b, bc2)

    if net==None:
        E = inner((1.0 + b) * grad(u), grad(v)) * dx(mesh)
    else:
        E = inner((NN_der(threshold, inner(grad(u), grad(u)), self.net) + b) * grad(u), grad(v)) * dx(mesh)

    # solve PDE
    solve(E == 0, u, bc)

    # J
    eta = 1
    ds = Measure('ds', domain=mesh, subdomain_data=boundaries)
    J = assemble(pow((1.0 / (det(Identity(2) + grad(u))) + det(Identity(2) + grad(u))), 2) * ds(2)
                 + inner(grad(det(Identity(2) + grad(u))), grad(det(Identity(2) + grad(u)))) * ds(2)
                 + inner(grad(det(Identity(2) + grad(u))), grad(det(Identity(2) + grad(u)))) * dx
                 + 0.5 * eta * inner(alpha, alpha) * dx(mesh))
    control = Control(alpha)

    rf = ReducedFunctional(J, control)

    test = False
    if test == True:
        h = interpolate(Expression("100*x[0]*x[1]", degree=1),alpha.function_space())
        taylor_test(rf, alpha, h)
        breakpoint()

    # save initial
    up = project(u, V)
    upi = project(-1.0 * u, V)
    ALE.move(mesh, up, annotate=False)
    ufile << up
    afile << alpha
    ALE.move(mesh, upi, annotate=False)

    problem = MoolaOptimizationProblem(rf)
    alpha_moola = moola.DolfinPrimalVector(alpha)
    solver = moola.BFGS(problem, alpha_moola,
                        options={'jtol': 1e-4, 'gtol': 1e-9, 'Hinit': "default", 'maxiter': 100, 'mem_lim': 10})

    sol = solver.solve()
    alpha_opt = sol['control'].data

    b_opt = Function(Vs)
    E1 = inner(grad(b_opt), grad(vb)) * dx(mesh) - inner(alpha_opt, vb) * dx(mesh)
    solve(E1 == 0, b_opt, bc2)

    # solve u_opt
    if net==None:
        E = inner((1.0 + b_opt) * grad(u), grad(v)) * dx(mesh)
    else:
        E = inner((NN_der(threshold, inner(grad(u), grad(u)), self.net) + b_opt) * grad(u), grad(v)) * dx(mesh)
    solve(E == 0, u, bc)

    if self.net != None:
        b_opt = project(NN_der(threshold, inner(grad(u_opt), grad(u_opt)), self.net) - 1 + b_opt, Vs)

    up = project(u, V)
    upi = project(-u, V)
    ALE.move(mesh, up, annotate=False)
    ufile << up
    afile << b_opt
    ALE.move(mesh, upi, annotate=False)

    # breakpoint()
    normgradtraf = project(inner(grad(u), grad(u)), Vs)

    xdmf = XDMFFile(output_directory + "optimal_control_data.xdmf")

    xdmf.write_checkpoint(b_opt, "alpha_opt", 0, append=True)
    xdmf.write_checkpoint(normgradtraf, "normgradtraf", 0, append=True)
