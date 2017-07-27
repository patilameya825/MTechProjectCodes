import tensorflow as tf, sys
import cv2
# change this as you see fit
image_path = sys.argv[1]

# Read in the image_data
image_data = tf.gfile.FastGFile(image_path, 'rb').read()

# Loads label file, strips off carriage return
label_lines = [line.rstrip() for line 
                   in tf.gfile.GFile("retrained_labels.txt")]

# Unpersists graph from file
with tf.gfile.FastGFile("retrained_graph.pb", 'rb') as f:
    graph_def = tf.GraphDef()
    graph_def.ParseFromString(f.read())
    _ = tf.import_graph_def(graph_def, name='')

file1 = open("names.txt","w")
sess = tf.Session()
op = sess.graph.get_operations()
for m in range(0,1007):
	print "values are",op[m].values()
	file1.write(str(op[m].values()))
	file1.write("\n")

	
