from math import pi, sin, sqrt

print("""g21
g64
m8

s26 m3
g4p2
f75
""")

z_length = 100.0  # (length)
max_depth = 20.0  # (maximum depth)
x_layer = 2.0     # (x-layer thickness)
z_layer = 4.0     # (z-slice thickness)
raster = 60       # (steps / commands per turn)
e_distance = 10.0  # Entry and exit distance.
e_turns = 1       # Fixed amount of turns for an entry / exit move.
jitter = 0.001
epsilon = 0.0001


def ellipse(z, phi, min_x):
    """ Generate the x-values """
    return min_x * (1+sin(phi * 2 - pi / 2)) / 2


def find_max_x(z, min_x, form, raster):
    mi, mx = -1, None
    for i in range(raster):
        phi = float(i) / raster * 2 * pi
        x = form(z, phi, min_x)
        if mx is None or x > mx:
            mi, mx = i, x
    #print("Maximum: ", mi, mx)
    return mi, mx


def g33(x, z, k):
    assert k > 0
    print("g33 x{} z{} k{}".format(round(x, 5), round(z, 5), round(k, 5)))


lstep = 0
for lstep in range(int(max_depth/x_layer) + 1):
    print("g0 x{} z0".format(e_distance))
    x = e_distance
    z = 0
    min_x = -x_layer * lstep

    # Do the entry-move.
    mi, mx = find_max_x(z, min_x, ellipse, raster)
    # Be at max x one raster step befor the actual max x.
    mi = (mi-1) % raster
    t = e_turns + float(mi) / raster
    k = abs(x-mx) / t
    #print("Entry move in {} turns land at step {}".format(round(t, 2), mi))
    g33(mx, z, k)
    x = mx

    # Complete the current turn.
    for phi_step in range(mi + 1, raster):
        phi = float(phi_step) / raster * 2 * pi
        nx = ellipse(z, phi, min_x)
        if abs(nx - x) < epsilon:
            nx += jitter
        k = abs(nx - x) * raster
        #print(phi_step, ':', end='')
        g33(nx, z, k)
        x = nx

    # Do another full turn.
    for phi_step in range(0, raster):
        phi = float(phi_step) / raster * 2 * pi
        nx = ellipse(z, phi, min_x)
        if abs(nx - x) < epsilon:
            nx += jitter
        k = abs(nx - x) * raster
        #print(phi_step, ':', end='')
        g33(nx, z, k)
        x = nx

    # Now do the spiral.
    for zstep in range(int(z_length/z_layer)):
        for phi_step in range(raster):
            phi = float(phi_step) / raster * 2 * pi
            nz = (zstep + float(phi_step) / raster) * z_layer
            nx = ellipse(nz, phi, min_x)
            k = sqrt((nx - x)**2 + (nz - z)**2) * raster
            if k < epsilon:
                nx += jitter
                k = sqrt((nx - x)**2 + (nz - z)**2) * raster
            #print(phi_step, ':', end='')
            g33(nx, nz, k)
            x = nx
            z = nz
    z = z_length
    # Do another full turn.
    for phi_step in range(0, raster):
        phi = float(phi_step) / raster * 2 * pi
        nx = ellipse(z, phi, min_x)
        if abs(nx - x) < epsilon:
            nx += jitter
        k = abs(nx - x) * raster
        #print(phi_step, ':', end='')
        g33(nx, z, k)
        x = nx

    # Move to the maximum x for this z.
    mi, _ = find_max_x(z, min_x, ellipse, raster)
    for phi_step in range(0, mi+1):
        phi = float(phi_step) / raster * 2 * pi
        nx = ellipse(z, phi, min_x)
        if abs(nx - x) < epsilon:
            nx += jitter
        k = abs(nx - x) * raster
        #print(phi_step, ':', end='')
        g33(nx, z, k)
        x = nx

    # Exit move.
    print("g0 x{} z{}".format(e_distance, z))

print("m2")
