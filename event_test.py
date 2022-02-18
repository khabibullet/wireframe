import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from matplotlib.animation import FuncAnimation

# parsing map
map = open("/Users/irek/Downloads/drive/MyDrive/fdf_maps/plat.fdf")
a = np.loadtxt(map, delimiter=" ")

# rotation matrixes
def rotH(fi):
	fi = fi / 180 * np.pi
	return np.array([[np.cos(fi), np.sin(fi), 0], [-np.sin(fi), np.cos(fi), 0], [0, 0, 1]])

def rotV(teta):
	teta = teta / 180 * np.pi
	return np.array([[1, 0, 0], [0, np.cos(teta), np.sin(teta)], [0, -np.sin(teta), np.cos(teta)]])

# map handling
def default(a, fi, teta, zoom, win):
	xoffs = (np.shape(a)[0] - 1) / 2
	yoffs = (np.shape(a)[1] - 1) / 2
	[X, Y, Z] = np.empty((3, np.shape(a)[0], np.shape(a)[1]))
	for i, val in np.ndenumerate(X):
			X[i] = i[0] - xoffs
			Y[i] = i[1] - yoffs
			Z[i] = a[i]
	X, Y, Z, fi = rotateH0(X, Y, Z, 0, fi, 0)
	X, Y, Z, teta = rotateV0(X, Y, Z, 0, teta)
	return X, Y, Z

def rotateH0(X, Y, Z, fi, dfi, teta):
	X, Y, Z, empty = rotateV0(X, Y, Z, teta, -teta)
	for i, val in np.ndenumerate(X):
		[X[i], Y[i], Z[i]] = np.matmul(rotH(dfi), [X[i], Y[i], Z[i]])
	X, Y, Z, empty = rotateV0(X, Y, Z, teta, teta)
	fi = fi + dfi
	if (fi > 360):
		fi = fi - 360
	if (fi <  -360):
		fi = fi + 360
	return X, Y, Z, fi

def rotateV0(X, Y, Z, teta, dteta):
	for i, val in np.ndenumerate(X):
		[X[i], Y[i], Z[i]] = np.matmul(rotV(dteta), [X[i], Y[i], Z[i]])
	teta = teta + dteta
	if (teta > 180):
		teta = 180
	if (teta <  0):
		teta = 0
	return X, Y, Z, teta

def shift(X, Y, dx, dy):
	[X, Y] = [X + dx, Y + dy]
	return X, Y

def scale(X, Y, Z, zoom):

	midx, midy = (np.max(X) + np.min(X)) / 2, (np.max(Y) + np.min(Y)) / 2
	X, Y = X - midx, Y - midy
	for i, val in np.ndenumerate(X):
		[X[i], Y[i], Z[i]] = [X[i] * zoom, Y[i] * zoom, Z[i] * zoom]
	X, Y = X + midx, Y + midy
	return X, Y, Z

def plot_map(X, Y):
    for h in range(np.shape(a)[1]):
        plt.plot(X[:,h], Y[:,h], 'k-')
    for v in range(np.shape(a)[0]):
        plt.plot(X[v,:], Y[v,:], 'k-')
    plt.axhline(0)
    plt.axvline(0)
    plt.xlim((-win / 2, win / 2))
    plt.ylim((-win / 2, win / 2))
    plt.gca().set_aspect("equal")

# event handling
def on_move(event):
    # get the x and y pixel coords
    x, y = event.x, event.y
    if event.inaxes:
        ax = event.inaxes  # the axes instance
        print('data coords %f %f' % (event.xdata, event.ydata))


def on_click(event):
    if event.button is MouseButton.LEFT:
        print('disconnecting callback')
        plt.disconnect(binding_id)

def rot_cam_v(X, Y, Z, fi, dfi, teta, dteta, zoom):
    X, Y, Z, teta = rotateV0(X, Y, Z, teta, dteta)
    for i, val in np.ndenumerate(X):
        Y[i] = Y[i] * np.cos(np.deg2rad(dteta)) + 1 / zoom * np.sin(np.deg2rad(dteta))
    zoom = 1 / (1 / zoom * np.cos(np.deg2rad(dteta)) - Y[i] * np.sin(np.deg2rad(dteta)))
    X, Y, Z = scale(X, Y, Z, zoom)
    return X, Y, Z, fi, teta, zoom

# map plotting
plt.figure(figsize=(5, 5))

fi, teta, zoom, win = 0, 0, 1, 30

X, Y, Z = default(a, fi, teta, zoom, win)
X, Y, Z, fi, teta, zoom = rot_cam_v(X, Y, Z, fi, 0, teta, 5, zoom)

plot_map(X, Y)

def anim_rotate(i, X, Y, Z, fi, teta, zoom):
    X, Y, Z, fi, teta, zoom = rot_cam_v(X, Y, Z, fi, 0, teta, 1, zoom)
    plt.cla()
    plot_map(X, Y) 
    return X, Y, Z, fi, teta

# ani = FuncAnimation(plt.gcf(), anim_rotate, fargs=(X, Y, Z, fi, teta), interval = 200)

binding_id = plt.connect('motion_notify_event', on_move)
plt.connect('button_press_event', on_click)
plt.show()