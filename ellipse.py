from math import pi, sin, sqrt
import sys

print("""g21
g64 p1
m8

g4p2
f150
""")

z_length = 100.0  # (length)
max_depth = 20.0  # (maximum depth)
x_layer = 2.0     # (x-layer thickness)
z_layer = 4.0     # (z-slice thickness)
raster = 90       # (steps / commands per turn)
e_distance = 10.0  # Entry and exit distance.
e_turns = 1       # Fixed amount of turns for an entry / exit move.
jitter = 0.001
epsilon = 0.0001


def ellipse(z, phi, min_x):
    """ Generate the x-values """
    return min_x * (1+sin(phi * 2 - pi / 2)) / 2

def cylinder(z, phi, min_x):
    return min_x

form = cylinder

def find_max_x(z, min_x, form, raster):
    mi, mx = -1, None
    for i in range(raster):
        phi = float(i) / raster * 2 * pi
        x = form(z, phi, min_x)
        if mx is None or x > mx:
            mi, mx = i, x
    #print("Maximum: ", mi, mx)
    return mi, mx


class RasterMachine:
    def __init__(self, raster):
        self.raster = raster
        self.x, self.z, self.a_step = 0, 0, 0

    def gcoords(self):
        a = float(self.a_step) / self.raster * 360
        return "z{} x{} a{}".format(self.x, self.z, a)

    def g0(self, x, z, a_step):
        self.new_position(x, z, a_step)
        print("g0 " + self.gcoords())

    def g1(self, x, z, a_step):
        self.new_position(x, z, a_step)
        print("g1 " + self.gcoords())

    def new_position(self, x, z, a_step):
        self.x, self.z = x, z

        turns, rel = divmod(self.a_step, self.raster)
        a_rel = a_step % self.raster
        if a_rel < rel:
            turns += 1
        self.a_step = turns * self.raster + a_rel


m = RasterMachine(raster)

lstep = 0
for lstep in [int(max_depth/x_layer)]: #range(int(max_depth/x_layer) + 1):
    x = e_distance
    z = 0
    min_x = -x_layer * lstep

    # Do the entry-move.
    mi, mx = find_max_x(z, min_x, form, raster)
    # Be at max x one raster step befor the actual max x.
    m.g0(e_distance, z, mi-1)
    #print("Entry move in {} turns land at step {}".format(round(t, 2), mi))
    m.g1(mx, z, mi)
    x = mx

    # Complete the current turn.
    for phi_step in range(mi + 1, raster):
        phi = float(phi_step) / raster * 2 * pi
        nx = form(z, phi, min_x)
        #print(phi_step, ':', end='')
        m.g1(nx, z, phi_step)
        x = nx

    # Do another full turn.
    for phi_step in range(0, raster):
        phi = float(phi_step) / raster * 2 * pi
        nx = form(z, phi, min_x)
        #print(phi_step, ':', end='')
        m.g1(nx, z, phi_step)
        x = nx

    # Now do the spiral.
    for zstep in range(int(z_length/z_layer)):
        for phi_step in range(raster):
            phi = float(phi_step) / raster * 2 * pi
            nz = (zstep + float(phi_step) / raster) * z_layer
            nx = form(nz, phi, min_x)
            #print(phi_step, ':', end='')
            m.g1(nx, nz, phi_step)
            x = nx
            z = nz
    z = z_length
    # Do another full turn.
    for phi_step in range(0, raster):
        phi = float(phi_step) / raster * 2 * pi
        nx = form(z, phi, min_x)
        #print(phi_step, ':', end='')
        m.g1(nx, z, phi_step)
        x = nx

    # Move to the maximum x for this z.
    mi, _ = find_max_x(z, min_x, form, raster)
    for phi_step in range(0, mi+1):
        phi = float(phi_step) / raster * 2 * pi
        nx = form(z, phi, min_x)
        #print(phi_step, ':', end='')
        m.g1(nx, z, phi_step)
        x = nx

    # Exit move.
    m.g0(e_distance, z, phi_step)

print("m2")
