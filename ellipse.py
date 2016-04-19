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

lstep = 0
for lstep in range(int(max_depth/x_layer) + 1):
    print("g0 x10 z0")
    x = 10.0
    z = 0
    min_x = -x_layer * lstep
    for zstep in range(int(z_length/z_layer)):
        for xstep in range(raster):
            nx = min_x*(1+sin(float(xstep) / raster * 2 * pi * 2 - 90))/2
            nz = (zstep + float(xstep) / raster) * z_layer
            k = sqrt((nx - x)**2 + (nz - z)**2)
            print("g33 x{} z{} k{}".format(round(nx, 5), round(nz, 5), round(k*raster, 5)))
            x = nx
            z = nz
    print("g0 x10 z{}".format(z_length))

print("m2")
