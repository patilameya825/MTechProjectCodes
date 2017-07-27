import tensorflow as tf, sys
import cv2
import time
import numpy as np
import receive_frame as r
import urllib.request
import socket               # Import socket module
import string

req_clas = 't shirt'
req_score = 0.3

def send_var(var):	
	s = socket.socket()         # Create a socket object
	host = '192.168.0.103' # Get local machine name
	port = 5003                # Reserve a port for your service.
#s.connect((host,port))
#while True:
	s.connect((host, port))
	#var = input('Enter number: ')
	var1 = var.encode()
	#print(type(var1))
	s.send(var1)
	s.close                     # Close the socket when done

def read_var():	
	time.sleep(1)
	s = socket.socket()         # Create a socket object
	host = '192.168.0.103' # Get local machine name
	port = 5003                # Reserve a port for your service.
#s.connect((host,port))
#while True:
	s.connect((host, port))
	num = s.recv(1024)
	num = num.decode()
	num = int(num)
	s.close                     # Close the socket when done
	return num

j = r.ameya()
bytes = bytes()

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("retrained_labels.txt")]

# Unpersists graph from file
with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

def detect_class(sess):
	i = j.rframe(bytes)
	#cv2.imshow('i', i)
	#if cv2.waitKey(1) == 27:
	#	exit(0)
	frame = i
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
		return human_string, score

def detect_class_1(sess):
	i = j.rframe(bytes)
	#cv2.imshow('i', i)
	#if cv2.waitKey(1) == 27:
	#	exit(0)
	leftframe = i[:,0:300,:]
	centerframe = i[:,100:500]
	rightframe = i[:,300:600,:]
	# Feed the image_data as input to the graph and get first prediction
	softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
	predictions_left = sess.run(softmax_tensor, \
	     {'DecodeJpeg:0': leftframe})
	predictions_center = sess.run(softmax_tensor, \
	     {'DecodeJpeg:0': centerframe})
	predictions_right = sess.run(softmax_tensor, \
	     {'DecodeJpeg:0': rightframe})
	#print predictions
	#print predictions.shape
	#print type(predictions)
	#cv2.imwrite("conv_1.jpg",predictions)
	# Sort to show labels of first prediction in order of confidence
	top_kl = predictions_left[0].argsort()[-len(predictions_left[0]):][::-1]
	top_kc = predictions_center[0].argsort()[-len(predictions_center[0]):][::-1]
	top_kr = predictions_right[0].argsort()[-len(predictions_right[0]):][::-1]

	for (node_idl,node_idc,node_idr) in (zip(top_kl,top_kc,top_kr)):
		human_stringl = label_lines[node_idl]
		scorel = predictions_left[0][node_idl]
		human_stringc = label_lines[node_idc]
		scorec = predictions_center[0][node_idc]
		human_stringr = label_lines[node_idr]
		scorer = predictions_right[0][node_idr]
		print('%s (score = %.5f)		%s (score = %.5f)		%s (score = %.5f)' % (human_stringl, scorel,human_stringc, scorec,human_stringr, scorer))
		break
	if (human_stringl == req_clas and human_stringc == req_clas):
		return 8
	if (human_stringr == req_clas and human_stringc == req_clas):
		return 8
	if (human_stringc == req_clas and scorel > req_score):
		return 8
	if (human_stringl == req_clas and scorel > req_score):
		return 4
	if (human_stringr == req_clas and scorel > req_score):
		return 6
	else:
		return 5

def obstacle_detect():
	send_var('1')
	chk = read_var()
	if chk == 1:
		send_var('9')
		right_s = read_var()
		send_var('10')
		center_s = read_var()
		send_var('11')
		left_s = read_var()
		if right_s > 150:
			return 3
		else: 
			if center_s > 150:
				return 2
			else:
				if left_s > 150:
					return 1
				else:
					return 0

def acquire_frame():
	i = j.rframe(bytes)
	#cv2.imshow('i', i)
	#if cv2.waitKey(1) == 27:
	#	exit(0)
	#frame = i
	#print(type(i))
	return i
			
def object_track_forward(sess):
	#frame = acquire_frame()
	#print(frame.size)
	print("Entered forward")
	location = detect_class_1(sess)
	obs = 0
	obs = obstacle_detect()
	print("forward obs is ", obs)
	if obs == 0:
		send_var('130')
		send_var('140')
		send_var(str(location))
		time.sleep(0.5)
	send_var('5')
	human_string, score = detect_class(sess)
	if ((human_string != req_clas)or (human_string == req_clas and score < req_score)) and obs == 0:
		return 3 # No backpack; Overflowed false detection; No object/obstacle in front; means object is not present in the immediate vicinity
	else:
		return 2
	
	
def object_track_rotate(sess):
	#frame = acquire_frame()
	human_string, score = detect_class(sess)
	if (human_string != req_clas) or (human_string == req_clas and score < req_score):
		send_var('130')
		send_var('140')
		send_var('6')
		time.sleep(0.5)
	send_var('5')
	human_string, score = detect_class(sess)
	if human_string == req_clas and score > req_score:
		return 2 # No backpack; Overflowed false detection; No object/obstacle in front; means object is not present in the immediate vicinity
	else:
		return 3

val = 3	

send_var('3')
send_var('3')

def rotate(sess):
	for i in range(0,8):
		val = object_track_rotate(sess)
		if val == 	

def find_object(sess):
	while True:
		val = rotate(sess)
		if val == 1:
			return 0
		val = forward(sess)
		if val == 1:
			return 0

with tf.Session() as sess:
	while True:
		start = time.time()
		find_object(sess)
		approach_object()
		print((time.time()-start))

