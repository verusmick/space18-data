import numpy as np
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import scipy.interpolate as interpolate
import os
import conda

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

from mpl_toolkits.basemap import Basemap

# plt.figure(figsize=(8, 8))
# m = Basemap(projection='ortho', resolution=None, lat_0=50, lon_0=-100)
# m.bluemarble(scale=0.5);
# plt.show()
import numpy as np
import cv2


def plot_ana(data):
    imgname = "worldtopo.png"
    frame = cv2.imread(imgname)
    worldarray = np.array(frame, dtype=float)

    lat = 180
    lon = 360
    [x, y, rgb] = np.shape(worldarray)

    Xpx = x / lat
    Ypx = y / lon

    # data = np.loadtxt('icevel.dat', dtype=float)
    # data = np.loadtxt('icetemp.dat', dtype=float)

    [datR, datC] = np.shape(data)
    data = np.array([data[:, 1], data[:, 0], data[:, 2]])

    datapx = np.array([(data[0, :]) * Xpx, (data[1, :] + 180) * Ypx], dtype=int)
    print(datapx)

    for i in range(datR):
        xi = datapx[0, i]
        yi = datapx[1, i]
        xf = int(xi + Xpx)
        yf = int(yi + Ypx)
        color = data[2, i] + 100
        if color >= 255:
            color = 255
        cv2.rectangle(worldarray, (xi, yi), (xf, yf), (0, color, 0), thickness=cv2.FILLED, lineType=8, shift=0)
    cv2.imwrite('prueba.png', worldarray)

def grid2(x, y, z, resX=50, resY=50):
    xi = np.linspace(min(x), max(x), resX)
    yi = np.linspace(min(y), max(y), resY)
    X, Y = np.meshgrid(xi,yi)
    Z = interpolate.griddata((x,y),z,(X,Y),method='linear')
    return X, Y, Z


def grid(x, y, z, resX=50, resY=50):
    "Convert 3 column data to matplotlib grid"
    xi = np.linspace(min(x), max(x), resX)
    yi = np.linspace(min(y), max(y), resY)
    Z = mlab.griddata(x, y, z, xi, yi, interp='linear')
    # Z = interpolate.griddata(x, y, z, xi, yi, method='linear')
    X, Y = np.meshgrid(xi, yi)
    return X, Y, Z

def plot_world_flat(lat, lon, data, file=None):
    if file:
        print('generatiing image for file: ' + str(file))
    plt.figure(figsize=(8, 8))
    m = Basemap(projection='cyl', resolution='l', llcrnrlat=-90, urcrnrlat=90, llcrnrlon=-180, urcrnrlon=180)
    # m.bluemarble()
    m.drawcoastlines(linewidth=0.5)
    m.drawparallels(np.arange(-90., 120., 30.), labels=[1, 0, 0, 0])
    m.drawmeridians(np.arange(-180., 181., 45.), labels=[0, 0, 0, 1])
    x, y = m(lon, lat)
    print('computing new grid')
    xx, yy, zz = grid2(x, y, data)

    # try:
    #     xx, yy, zz = grid2(x, y, data)
    # except Exception as e:
    #     print(e.message)
    #     e.
    #     print('error procesing fifel ' +  str(file))
    #     return
    print('generate plot')
    m.pcolormesh(xx, yy, zz)
    if file:
        print('save image./ DODE')
        plt.savefig(file)
    else:
        print('dispplay image onluy')
        plt.show()