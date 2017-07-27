import tensorflow as tf, sys
import cv2
import time
import urllib.request
import numpy as np

stream = urllib.request.urlopen('http://192.168.43.139:8090/test.mjpg')
print(type(stream))
bytes = bytes()

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("retrained_labels.txt")]

# Unpersists graph from file
with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

with tf.Session() as sess:
	while True:
		start = time.time()
		urllib.request.urlcleanup()
		bytes += stream.read(1024)
		a = bytes.find(b'\xff\xd8')
		b = bytes.find(b'\xff\xd9')
		if a != -1 and b != -1:
			jpg = bytes[a:b+2]
			bytes = bytes[b+2:]
			i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
			frame = i
			# Feed the image_data as input to the graph and get first prediction
			softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
			predictions = sess.run(softmax_tensor, \
			     {'DecodeJpeg:0': frame})
			#print predictions
			#print predictions.shape
			#print type(predictions)
			#cv2.imwrite("conv_1.jpg",predictions)
			# Sort to show labels of first prediction in order of confidence
			top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]

			for node_id in top_k:
				human_string = label_lines[node_id]
				score = predictions[0][node_id]
				print('%s (score = %.5f)' % (human_string, score))
			print((time.time()-start))
			cv2.imshow('i', i)
			if cv2.waitKey(1) == 27:
				exit(0)
