import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
# from matplotlib.animation import FuncAnimation
plt.rcParams['keymap.save'].remove('s')
plt.rcParams['keymap.quit'].remove('q')

map = open("/Users/irek/Downloads/drive/MyDrive/fdf_maps/plat.fdf")
a = np.loadtxt(map, delimiter=" ")

def map_vectors(a):
	xoffs = (np.shape(a)[0] - 1) / 2
	yoffs = (np.shape(a)[1] - 1) / 2
	v = np.empty((4, np.shape(a)[0], np.shape(a)[1]))
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = [i[0] - xoffs, i[1] - yoffs, a[i], 1]
	return v

def trans_matrix(v0):
	return np.array([[1, 0, 0, -v0[0]],
					[0, 1, 0, -v0[1]],
					[0, 0, 1, -v0[2]],
					[0, 0, 0, 1]])

def rot_matrix(fi, teta):
	fi = np.deg2rad(-fi)
	teta = np.deg2rad(-teta)
	Rf = np.array([[np.cos(fi), np.sin(fi), 0, 0],
					[-np.sin(fi), np.cos(fi), 0, 0],
					[0, 0, 1, 0],
					[0, 0, 0, 1]])
	Rt = np.array([[1, 0, 0, 0],
					[0, np.cos(teta), np.sin(teta), 0],
					[0, -np.sin(teta), np.cos(teta), 0],
					[0, 0, 0, 1]])
	return np.matmul(Rt, Rf)

def proj_matrix(f):
	return np.array([[f, 0, 0, 0],
					[0, f, 0, 0],
					[0, 0, f, 0],
					[0, 0, 1, 0]])

def plot_map(v, win, F):
	plt.cla()
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = (F @ v[:, i[0], i[1]]) / v[2, i[0], i[1]]
	for w in range(np.shape(a)[1]):
		plt.plot(v[0, :, w], v[1, :, w], 'k-')
	for h in range(np.shape(a)[0]):
		plt.plot(v[0, h, :], v[1, h, :], 'k-')
	plt.xlim((-win / 2, win / 2))
	plt.ylim((-win / 2, win / 2))
	plt.gca().set_aspect("equal")
	plt.draw()


def set_cam_angle(fi, teta, v, v1):
	# getting cam system map coords after cam
	# rotation (in old cam system and/or initial system)
	R = rot_matrix(fi, teta)
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = R @ v1[:, i[0], i[1]]
	return v, R

def move_cam(v, v1, dv, R):
	# getting cam system map coords (v1)
	# and (cam system map coords without cam rotation (v))
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = v[:, i[0], i[1]] - dv # coords to plot
		v1[:, i[0], i[1]] = np.linalg.inv(R) @ v[:, i[0], i[1]]
	return v, v1

def key_press(event, v, v1, R, win, F, step):
	if (event.key == 'escape'):
		plt.close()
	if (event.key == 'd' or 'a' or 'w' or 's' or 'q' or 'e'):
		if (event.key == 'd'):
			v, v1 = move_cam(v, v1, [step, 0, 0, 0], R)
		if (event.key == 'a'):
			v, v1 = move_cam(v, v1, [-step, 0, 0, 0], R)
		if (event.key == 'w'):
			v, v1 = move_cam(v, v1, [0, 0, step, 0], R)
		if (event.key == 's'):
			v, v1 = move_cam(v, v1, [0, 0, -step, 0], R)
		if (event.key == 'q'):
			v, v1 = move_cam(v, v1, [0, -step, 0, 0], R)
		if (event.key == 'e'):
			v, v1 = move_cam(v, v1, [0, step, 0, 0], R)
		plot_map(v, win, F)
	return v, v1

def	mouse_move(event, fi, teta, v, v1, R, win, F, dx, dy):
	if event.button is MouseButton.LEFT:
		fi, teta = fi - dx, teta - dy
		dx, dy = dx + event.x / win, dy + event.y / win
		v, R = set_cam_angle(fi, teta, v, v1)
	plot_map(v, win, F)
	return v, R, fi, teta, dx, dy

fi, teta, win, view_angle, step = 20, 20, 30, 60, 0.5
f = win / np.tan(np.deg2rad(view_angle) / 2) / 2
dx, dy = 0, 0

v = map_vectors(a)
v1 = np.empty(np.shape(v))
F = proj_matrix(f)
R = rot_matrix(0, 0)

# cam handling
v, v1 = move_cam(v, v1, [0, 0, -15, 0], R)
v, R = set_cam_angle(20, 20, v, v1)

fig = plt.figure(figsize=(5, 5))
plot_map(v, win, F)
plt.connect('motion_notify_event', lambda event: mouse_move(event, fi, teta, v, v1, R, win, F, dx, dy))
plt.connect('key_press_event', lambda event: key_press(event, v, v1, R, win, F, step))
plt.show()
