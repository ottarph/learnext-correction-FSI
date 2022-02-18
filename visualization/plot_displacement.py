import matplotlib.pyplot as pl
import numpy as np

#times = np.asarray(range(len(displacement)))*deltat

#pl.plot(times, displacement)
#pl.axis([0,15, -0.1, 0.1])
#pl.savefig('./displacement_plot.png')

colors = [np.asarray([0, 101, 189])*1./255,
          np.asarray([218, 215, 213])*1./255]#,
         # np.asarray([227, 114, 34])*1./255,
         # np.asarray([0, 0, 0])*1./255
         #]

def plot_displacement(list, times, str):
    colors = [np.asarray([0, 101, 189])*1./255,
          np.asarray([218, 215, 213])*1./255]
    if len(list)>2:
        colors = [(len(list)-i)/(len(list))*colors[0] + i/(len(list))*colors[1] for i in range(len(list)+1)]
    for i in range(len(list)):
        pl.plot(times[i], list[i], color = colors[i], linewidth=0.6)
        pl.axis([0, 15, -0.1, 0.1])
        pl.savefig(str)
    pl.close()

def plot_determinant(list, times, str):
    colors = [np.asarray([0, 101, 189]) * 1. / 255,
              np.asarray([218, 215, 213]) * 1. / 255]
    if len(list) > 2:
        colors = [(len(list)-i)/(len(list))*colors[0] + i/(len(list))*colors[1] for i in range(len(list)+1)]
    for i in range(len(list)):
        pl.plot(times[i], list[i], color = colors[i], linewidth=0.6)
        pl.axis([0, 15, -0.1, 1.1])
        pl.savefig(str)
    pl.close()

def plot_timestep(times, str):
    colors = [np.asarray([0, 101, 189]) * 1. / 255,
              np.asarray([218, 215, 213]) * 1. / 255]
    if len(times) > 2:
        colors = [(len(list) - i) / (len(list)) * colors[0] + i / (len(list)) * colors[1] for i in
                  range(len(list)+1)]
    times_max = times[0][0] # assume that first time step of first simulation is the maximal timestep
    for i in range(len(times)):
        times_diff = [times[i][k+1] - times[i][k] for k in range(len(times[i])-1)]
        times_mid = [0.5*(times[i][k+1] + times[i][k]) for k in range(len(times[i])-1)]
        pl.plot(times_mid, times_diff, color=colors[i], linewidth=0.6)
        pl.axis([0, 15, 0.0, 0.011])
        pl.savefig(str)
    pl.close()

if __name__ == "__main__":
    times = np.loadtxt('../Output/files/learned/times.txt')

    displacement = np.loadtxt('../Output/files/learned/displacementy.txt')

    plot_displacement([displacement, displacement*1.1, displacement*1.2, displacement*1.3], [times, times, times, times],
                      '../Output/visualizations/displacement_plot.pdf')

    determinant = np.loadtxt('../Output/files/learned/determinant.txt')

    plot_determinant([determinant], [times],
                     '../Output/visualizations/determinant_plot.pdf')

    plot_timestep([times],
                     '../Output/visualizations/timestepsize_plot.pdf')
