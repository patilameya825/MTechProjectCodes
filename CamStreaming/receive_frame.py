import cv2
import numpy as np
import urllib.request


class ameya:
	def rframe(self,bytes):
		stream = urllib.request.urlopen('http://192.168.0.103:8090/test.mjpg')
		while True:
			bytes += stream.read(1024)
			a = bytes.find(b'\xff\xd8')
			b = bytes.find(b'\xff\xd9')
			if a != -1 and b != -1:
				jpg = bytes[a:b+2]
				bytes = bytes[b+2:]
				len(jpg)
				i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
				#cv2.imshow('i', i)
				#if cv2.waitKey(1) == 27:
				#    exit(0)
				return i
