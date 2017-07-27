import cv2
import urllib.request
import numpy as np

stream = urllib.request.urlopen('http://192.168.0.103:8090/test.mjpg')
bytes = bytes()
count = 0
cnt = 0
while True:
	bytes += stream.read(1024)
	a = bytes.find(b'\xff\xd8')
	b = bytes.find(b'\xff\xd9')
	if a != -1 and b != -1:
		jpg = bytes[a:b+2]
		bytes = bytes[b+2:]
		i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
		w,h,ch = i.shape
		#print(w,h,ch)
		left = i[:,300:600,:]
		print(left.shape)
		cv2.imshow('i', left)
		if cv2.waitKey(1) == 27:
			exit(0)
