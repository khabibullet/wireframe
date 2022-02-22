import pygame as pg
import numpy as np
from os import path

relpath = '/fdf_maps/pylone.fdf'
dirpath = path.dirname(__file__)
wholepath = dirpath + relpath
map = open(wholepath)
a = np.loadtxt(map, delimiter=" ")

def draw_map(v, F):
    sc.fill(C_WHITE)
    zmin = np.min(v[2])
    for i, val in np.ndenumerate(v[1, :, :]):
        v[:, i[0], i[1]] = (F @ v[:, i[0], i[1]]) / v[2, i[0], i[1]]
        v[0, i[0], i[1]] = v[0, i[0], i[1]] + win[0] / 2
        v[1, i[0], i[1]] = -v[1, i[0], i[1]] + win[1] / 2
    if zmin > 0:
        for w in range(mapsize[1]):
            for h in range(mapsize[0] - 1):
                pg.draw.aaline(sc, C_BLACK, (v[0, h, w], v[1, h, w]),
                                            (v[0, h + 1, w], v[1, h + 1, w]))
        for h in range(mapsize[0]):
            for w in range(mapsize[1] - 1):
                pg.draw.aaline(sc, C_BLACK, (v[0, h, w], v[1, h, w]),
                                            (v[0, h, w + 1], v[1, h, w + 1]))
    pg.display.flip()

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

def set_cam_angle(fi, teta, v, v1):
	R = rot_matrix(fi, teta)
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = R @ v1[:, i[0], i[1]]
	return v, R

def move_cam(v, v1, dv, R):
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = v[:, i[0], i[1]] - dv # coords to plot
		v1[:, i[0], i[1]] = np.linalg.inv(R) @ v[:, i[0], i[1]]
	return v, v1

def map_vectors(a):
	xoffs = (np.shape(a)[0] - 1) / 2
	yoffs = (np.shape(a)[1] - 1) / 2
	v = np.empty((4, np.shape(a)[0], np.shape(a)[1]))
	for i, val in np.ndenumerate(v[1, :, :]):
		v[:, i[0], i[1]] = [i[0] - xoffs, i[1] - yoffs, a[i], 1]
	return v


win, mapsize = (700, 500), (np.shape(a)[0], np.shape(a)[1])
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
fi, teta, view_angle = 0, 0, 60
dx, dy, dz = 0, 0, 0
dr = 0.2
f = win[0] / np.tan(np.deg2rad(view_angle) / 2) / 2

v = map_vectors(a)
v1 = np.empty(np.shape(v))
R = rot_matrix(0, 0)
F = np.array([[f, 0, 0, 0],
			    [0, f, 0, 0],
			    [0, 0, f, 0],
	            [0, 0, 1, 0]])

pg.init()
sc = pg.display.set_mode(win)

clock = pg.time.Clock()

v, v1 = move_cam(v, v1, [0, 0, -15, 0], R)

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                exit()
            # x
            elif event.key == pg.K_d:
                dx += dr
            elif event.key == pg.K_a:
                dx += -dr
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
                dx += -dr
            elif event.key == pg.K_a:
                dx += dr
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
            fi += event.rel[0] / 2
            teta += -event.rel[1] / 2
    v, R = set_cam_angle(fi, teta, v, v1)
    v, v1 = move_cam(v, v1, [dx, dy, dz, 0], R)
    draw_map(v, F)
    clock.tick(60)