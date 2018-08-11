import sys
import os
import time

sys.path.insert(0, './bin')
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from sort.sort import *
from color_extractor.color_extractor import ImageToColor

from controllers.ageGenderController import *

from multiprocessing import Process, Queue

sys.path.insert(0, './bin/tf_openpose')
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

# from age_gender.age_gender_main import *

from utils import *

import cv2

def crop_img(img,box):
    y,x,d = img.shape
    startx = int(x*box[0])
    starty = int(y*box[1])
    endx = int(x*box[3])
    endy = int(y*box[2])

    return img[starty:endy,startx:endx]

class Detector():
    def __init__(self, target_ip):
        
        self.CWD_PATH = os.getcwd()
        self.CWD_PATH = os.path.abspath(os.path.join(self.CWD_PATH, os.pardir))
        self.CWD_PATH = os.path.join(self.CWD_PATH, '3_BRobot')

        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
        PATH_TO_CKPT = os.path.join(self.CWD_PATH, 'object_detection', MODEL_NAME, 'frozen_inference_graph.pb')

        # List of the strings that is used to add correct label for each box.
        PATH_TO_LABELS = os.path.join(self.CWD_PATH, 'object_detection', 'data', 'mscoco_label_map.pbtxt')


        NUM_CLASSES = 90

        # Loading label map
        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                                    use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')


        self.right_clicks = []
        # self.right_clicks = [[375, 41], [1000, 709]]
        # mouse callback function
        def mouse_callback(event, x, y, flags, params):
            #right-click event value is 2
            if event == 2:
                if len(self.right_clicks) < 2:
                    self.right_clicks.append([x, y])
                else:
                    self.right_clicks = [[x,y]]

                print(self.right_clicks)

        CAM_ID = 1

        self.cam = cv2.VideoCapture(int(CAM_ID))

        self.window_name = 'Cam'+str(CAM_ID)
        cv2.namedWindow(self.window_name)
        cv2.setMouseCallback(self.window_name,mouse_callback)

        self.prevTime = 0
        self.window_size = (1312, 736)

        if self.cam.isOpened() == False:
            print('Can\'t open the CAM(%d)' % (CAM_ID))
            exit()

        self.face_queue = Queue()
        self.gender_queue = Queue()
        self.age_queue = Queue()

        self.process_gender = Process(target=gender_estimate, args=(self.face_queue,self.gender_queue))
        self.process_gender.start()

        self.process_age = Process(target=age_estimate, args=(self.face_queue,self.age_queue))
        self.process_age.start()

        self.w = self.window_size[0]
        self.h = self.window_size[1]
        self.e = TfPoseEstimator(get_graph_path('mobilenet_thin'), target_size=(self.w, self.h))

    def detect_objects(self, image_np, sess, detection_graph, mot_tracker, img_to_color, face_detect, face_queue, gender_queue, age_queue):
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

        person_attr = {
                    'age':'NA',
                    'gender':'NA',
                    'color':'NA'
                }

        if len(person_ids) > 0:
            selected_person_id = person_ids[0]
            
            person_box = boxes[0][selected_person_id]
            person_score = scores[0][selected_person_id]
            person_tracker = trackers[selected_person_id]

            if person_score > 0.6:

                def get_color(q, img):
                    try:
                        start_time = time.monotonic()
                        
                        c = img_to_color.get(img)
                        q.put({"flag":"color","value":c})

                        elapsed_time = time.monotonic() - start_time
                        print("Color", elapsed_time)
                    except:
                        q.put({"flag":"color","value":False})


                def detect_face(q, img, face_detect, face_queue, gender_queue, age_queue):

                    start_time = time.monotonic()
                    # your code
                    
                    files = []
                    
                    faces, face_files, rectangles, tgtdir = face_detect.run(img)
                    face_queue.put([face_files, img, tgtdir])
                    face_queue.put([face_files, img, tgtdir])

                    person_gender = gender_queue.get()
                    person_age = age_queue.get()
                    print("gender rcvd",person_gender)
                    print("Age rcvd",person_age)

                    q.put({"flag":"gender","value":person_gender})
                    q.put({"flag":"age","value":person_age})

                    elapsed_time = time.monotonic() - start_time
                    print("Age/Gender", elapsed_time)

                person_img = crop_img(image_np,person_box)

                q = Queue()
                procs = []

                process_color = Process(target=get_color, args=(q, person_img,))
                procs.append(process_color)

                process_face = Process(target=detect_face, args=(q, person_img, face_detect, face_queue, gender_queue, age_queue))
                procs.append(process_face)

                for proc in procs:
                    proc.start()

                results = []
                for proc in procs:
                    results.append(q.get())
                results.append(q.get())

                for proc in procs:
                    proc.join()

                

                for result in results:
                    person_attr[result['flag']] = result['value']

                # print(person_attr)
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
                    self.category_index,
                    use_normalized_coordinates=True,
                    line_thickness=3)

        return image_np, person_attr

    def detect_start(self):

        with self.detection_graph.as_default():
            with tf.Session(graph=self.detection_graph) as sess:
                # Load modules
                mot_tracker = Sort() 

                npz = np.load('./bin/color_extractor/color_names.npz')
                img_to_color = ImageToColor(npz['samples'], npz['labels'])

                face_detect = face_detection_model('dlib', './bin/age_gender/Model/shape_predictor_68_face_landmarks.dat')
                person_attr = False

                while (True):
                    ret, frame = self.cam.read()

                    # Detection
                    if len(self.right_clicks) == 2:
                        print(self.right_clicks)
                        _y,_x,_d = frame.shape
                        [_c1, _c2] = self.right_clicks
                        crop_box = [
                            _c1[0] / _x,
                            _c1[1] / _y,
                            _c2[0] / _x,
                            _c2[1] / _y,
                        ]
                        cropped_img = crop_img(frame, crop_box)

                        try:
                            image_process, person_attr = self.detect_objects(cropped_img, sess, self.detection_graph, mot_tracker, img_to_color, face_detect, self.face_queue, self.gender_queue, self.age_queue)
                            print("####", person_attr)
                            if isinstance(person_attr, list):
                                if person_attr[0]['gender'] != 'NA' and person_attr[0]['gender'] != False:
                                    break
                            else:
                                if person_attr['gender'] != 'NA' and person_attr['gender'] != False:
                                    break

                        except Exception as e:
                            print(e)
                            pass
                        
                    
                    curTime = time.time()
                    sec = curTime - self.prevTime
                    self.prevTime = curTime
                    fps = 1 / (sec)

                    str1 = "FPS : %0.1f" % fps
                    str2 = "Testing . . ."
                    cv2.putText(frame, str1, (5, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
                    cv2.putText(frame, str2, (100, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0))
                    cv2.imshow(self.window_name, frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        self.detect_stop()
                        break

                    # plt.figure(figsize=IMAGE_SIZE)
                    # plt.imshow(image_process)
                    # plt.show()

                if person_attr:
                    return person_attr
                else:
                    return False   

    def detect_stop(self):
        # self.cam.release()
        # cv2.destroyWindow(self.window_name)
        print("Detect Stop")
        self.process_gender.join()
        self.process_age.join()

        return True

    def pose_start(self):
        print("Pose Start")
        result = False
        while (True):
            ret, frame = self.cam.read()

            cropped_img = None
            if len(self.right_clicks) == 2:
                # print(self.right_clicks)
                _y,_x,_d = frame.shape
                [_c1, _c2] = self.right_clicks
                crop_box = [
                    _c1[0] / _x,
                    _c1[1] / _y,
                    _c2[0] / _x,
                    _c2[1] / _y,
                ]
                cropped_img = crop_img(frame, crop_box)

                humans = self.e.inference(cropped_img, resize_to_default=(self.w > 0 and self.h > 0), upsample_size=4.0)
                if len(humans) > 0:
                    if 7 in humans[0].body_parts or 4 in humans[0].body_parts:
                        print("Hands Detected")
                        result = 1
                        break

                image = TfPoseEstimator.draw_humans(cropped_img, humans, imgcopy=False)

                cv2.imshow('tf-pose-estimation result', image)
            
            cv2.imshow(self.window_name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        return result