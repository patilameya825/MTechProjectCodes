import tensorflow as tf, sys
import cv2
import time

cap = cv2.VideoCapture(0)

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("retrained_labels.txt")]

# Unpersists graph from file
with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

while True:
	with tf.Session() as sess:
		start = time.time()
		ret, frame = cap.read()
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
			print (score)
		print((time.time()-start))
