#! /usr/bin/python3

import numpy as np

def dist(a,b):
	n = len(a)
	if n != len(b):
		return None
	if isinstance(a, np.ndarray):
		return np.linalg.norm(a-b)
	res = 0
	for i in range(n):
		res += (a[i]-b[i])**2
	return np.sqrt(res)

def D(p,pts):
	values = map(lambda x: dist(p,x), pts)
	return sum(values)

def get_centroid(pts):
	if not isinstance(pts, list):
		return None
	D_vect = list()
	for pt in pts:
		if isinstance(pt, np.ndarray):
			others = filter(lambda x: not (x == pt).all(), pts)
		else:
			others = filter(lambda x: x != pt, pts)
		D_vect.append(D(pt,others))
	d_min = min(D_vect)
	return pts[D_vect.index(d_min)]

if __name__ == '__main__':
	pts = [(1,-2,-3,4), (-1,2,3,2), (-1,2,3,2), (1,10,1,-14), (0,-1,2,0),
		(0,-1,2,0), (10,0,0,0), (9,1,2,1), (0,0,1,1), (0,0,1,-1)]
	pts_2 = [np.random.randint(10, size=3).reshape(3,1) for i in range(10)]

	print(pts)
	print('centroid = {}'.format(get_centroid(pts)))
	print(pts_2)
	print('centroid = {}'.format(get_centroid(pts_2)))
