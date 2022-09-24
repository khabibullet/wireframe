import pygame as pg
import numpy as np
from os import path

relpath = '/fdf_maps/pylone.fdf'
dirpath = path.dirname(__file__)
wholepath = dirpath + relpath
map = open(wholepath)
a = np.loadtxt(map, delimiter=" ")

def draw_map(v1):
	sc.fill(C_WHITE)
	for w in range(mapsize[1]):
		for h in range(mapsize[0] - 1):
			if (v1[2, h + 1, w] != 0 and v1[2, h, w] != 0):
				pg.draw.aaline(sc, C_BLACK, (v1[0, h, w], v1[1, h, w]),
								(v1[0, h + 1, w], v1[1, h + 1, w]))
	for h in range(mapsize[0]):
		for w in range(mapsize[1] - 1):
			if (v1[2, h, w] != 0 and v1[2, h, w + 1] != 0):
				pg.draw.aaline(sc, C_BLACK, (v1[0, h, w], v1[1, h, w]),
								(v1[0, h, w + 1], v1[1, h, w + 1]))
	pg.display.flip()
	return

def get_projection(v1, f):
	zmin = np.min(v1[2])
	for i, val in np.ndenumerate(v1[1, :, :]):
		v1[0, i[0], i[1]] = -(f * v1[0, i[0], i[1]] / v1[2, i[0], i[1]]) + win[0] / 2
		v1[1, i[0], i[1]] = -(f * v1[1, i[0], i[1]] / v1[2, i[0], i[1]]) + win[1] / 2
		if (v1[2, i[0], i[1]] < 0):
			v1[2, i[0], i[1]] = 0
	return v1

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
	R = np.matmul(Rt, Rf)
	return R

def set_cam_angle(v1, v2, R):
	for i, val in np.ndenumerate(v1[1, :, :]):
		v1[:, i[0], i[1]] = R @ v2[:, i[0], i[1]]
	return v1

def move_cam(v1, v2, R, dv):
	R1 = np.transpose(R)
	for i, val in np.ndenumerate(v1[1, :, :]):
		v1[:, i[0], i[1]] = v1[:, i[0], i[1]] - dv # coords to plot 
		v2[:, i[0], i[1]] = R1 @ v1[:, i[0], i[1]]
	return v1, v2

def map_vectors(a):
	xoffs = (np.shape(a)[1] - 1) / 2
	yoffs = (np.shape(a)[0] - 1) / 2
	zmid = (np.max(a) + np.max(a)) / 2;
	v1 = np.empty((4, np.shape(a)[0], np.shape(a)[1]))
	for i, val in np.ndenumerate(v1[1, :, :]):
		v1[:, i[0], i[1]] = [i[1] - xoffs, i[0] - yoffs, -a[i] + zmid, 1]
	return v1


win, mapsize = (700, 500), (np.shape(a)[0], np.shape(a)[1])
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
fi, teta, view_angle = 0, 0, 60
dx, dy, dz = 0, 0, 0
dr = 0.5
f = win[0] / np.tan(np.deg2rad(view_angle) / 2) / 2

v1 = map_vectors(a)
v2 = np.empty(np.shape(v1))

pg.init()
sc = pg.display.set_mode(win)
clock = pg.time.Clock()

R = rot_matrix(fi, teta)
v1, v2 = move_cam(v1, v2, R, [0, 0, -15, 0])

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
            # x
            elif event.key == pg.K_d:
                dx += -dr
            elif event.key == pg.K_a:
                dx += dr
            # y
            elif event.key == pg.K_e:
                dy += dr
            elif event.key == pg.K_q:
                dy += -dr
            # z
            elif event.key == pg.K_w:
                dz += dr
            elif event.key == pg.K_s:
                dz += -dr
        elif event.type == pg.KEYUP:
            if event.key == pg.K_d:
                dx += dr
            elif event.key == pg.K_a:
                dx += -dr
            # y
            elif event.key == pg.K_e:
                dy += -dr
            elif event.key == pg.K_q:
                dy += dr
            # z
            elif event.key == pg.K_w:
                dz += -dr
            elif event.key == pg.K_s:
                dz += dr
        elif event.type == pg.MOUSEMOTION:
            fi += -event.rel[0] / 2
            teta += -event.rel[1] / 2
    R = rot_matrix(fi, teta)
    v1 = set_cam_angle(v1, v2, R)
    v1, v2 = move_cam(v1, v2, R, [dx, dy, dz, 0])
    v1 = get_projection(v1, f)
    draw_map(v1)
    clock.tick(60)