import sys
import os
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from sort.sort import *

import atexit

import time

import socket
import redis
r = redis.StrictRedis(host='redis.hwanmoo.kr', port=6379, db=0)


CWD_PATH = os.getcwd()

# Path to frozen detection graph. This is the actual model that is used for the object detection.
MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
PATH_TO_CKPT = os.path.join(CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join(CWD_PATH, 'object_detection', 'data', 'mscoco_label_map.pbtxt')


NUM_CLASSES = 90

# Loading label map
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                            use_display_name=True)
category_index = label_map_util.create_category_index(categories)

def detect_objects(image_np, sess, detection_graph, mot_tracker, r, local_ip):
    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
    image_np_expanded = np.expand_dims(image_np, axis=0)
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

    # Each box represents a part of the image where a particular object was detected.
    boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

    # Each score represent how level of confidence for each of the objects.
    # Score is shown on the result image, together with the class label.
    scores = detection_graph.get_tensor_by_name('detection_scores:0')
    classes = detection_graph.get_tensor_by_name('detection_classes:0')
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')

    # Actual detection.
    (boxes, scores, classes, num_detections) = sess.run(
        [boxes, scores, classes, num_detections],
        feed_dict={image_tensor: image_np_expanded})

    trackers = mot_tracker.update(boxes[0])
    
    person_ids = [i for i, e in enumerate(classes[0]) if e == 1]

    if len(person_ids) > 0:
        selected_person_id = person_ids[0]
        
        person_box = boxes[0][selected_person_id]
        person_score = scores[0][selected_person_id]
        person_tracker = trackers[selected_person_id]

        def crop_img(img,box):
            y,x,d = img.shape
            startx = int(x*box[0])
            starty = int(y*box[1])
            endx = int(x*box[3])
            endy = int(y*box[2])

            return img[starty:endy,startx:endx]

        person_img = crop_img(image_np,person_box)

        start_time = time.time()

        r.hdel('person_images_shape',local_ip)
        r.hdel('person_images',local_ip)
        r.hdel('person_attr',local_ip)
    
        r.hset('person_images',local_ip,person_img.tobytes())
        r.hset('person_images_shape',local_ip,person_img.shape)
        # print("IMG Sent to server")    
        while True:
            msg = r.hget('person_attr',local_ip)
            if msg is not None:
                r.hdel('person_attr',local_ip)

                results = eval(msg)
                break    

        elapsed_time = time.time() - start_time
        print("ET",elapsed_time)
        person_attr = {
            'age':1,
            'gender':1,
            'color':1
        }
        for r in results:
            person_attr[r['flag']] = r['value']

        print(person_attr)

        # override boxes
        boxes = np.expand_dims(person_box, axis=0)
        classes = [1]
        scores = np.expand_dims(person_score, axis=0)
        trackers = np.expand_dims(person_tracker, axis=0)
        person_attr = [person_attr]

        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            boxes,
            classes,
            scores,
            trackers,
            person_attr,
            category_index,
            use_normalized_coordinates=True,
            line_thickness=3)

    return image_np

# First test on images
PATH_TO_TEST_IMAGES_DIR = 'object_detection/test_images'
TEST_IMAGE_PATHS = [ os.path.join(PATH_TO_TEST_IMAGES_DIR, 'image{}.jpg'.format(i)) for i in range(1, 3) ]

# Size, in inches, of the output images.
IMAGE_SIZE = (12, 8)

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

import cv2
import time

CAM_ID = 0
cam = cv2.VideoCapture(CAM_ID)

if cam.isOpened() == False:
    print('Can\'t open the CAM(%d)' % (CAM_ID))
    exit()

cv2.namedWindow('Cam')
prevTime = 0

''' Getting Local IP of this Computer '''
local_ip = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1][0]

ips = eval(r.hget('subscribers','list'))
if ips is None:
    ips = [local_ip]
else:
    if local_ip not in ips:
        ips.append(local_ip)

r.hset('subscribers','list',ips)
r.hset('subscribers',local_ip,True)

def unset_redis_at_exit(r,local_ip):
    r.hset('subscribers',local_ip,False)

atexit.register(unset_redis_at_exit,r=r,local_ip=local_ip)

with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        # Load modules
        mot_tracker = Sort() 

        while (True):
            ret, frame = cam.read()
            
            # Detection
            image_process = detect_objects(frame, sess, detection_graph, mot_tracker, r, local_ip)

            curTime = time.time()
            sec = curTime - prevTime
            prevTime = curTime
            fps = 1 / (sec)

            str = "FPS : %0.1f" % fps
            str2 = "Testing . . ."
            cv2.putText(frame, str, (5, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            cv2.putText(frame, str2, (100, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
            cv2.imshow('Cam', cv2.resize(frame, (1300, 800)))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cam.release()
                cv2.destroyWindow('Cam')
                break

            
            
            # plt.figure(figsize=IMAGE_SIZE)
            # plt.imshow(image_process)
            # plt.show()

        process_gender.join()
        process_age.join()