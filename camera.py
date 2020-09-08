from harvesters.core import Harvester
import traceback
import sys
import cv2
import numpy as np
import logic
import yolo
from numba import jit, cuda
#import jetson.interface
#import jetson.utils

font = cv2.FONT_HERSHEY_PLAIN
global lines
with open("equations.txt") as f:
    lines = [float(i) for i in f]

## finds objects on an image using pre-trained model for detecting objcect and manipulates with them, showing them on screen
def objects_recognision(img, net, classes, output_layers):

    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape
    # bigger size is (609, 609), medium (416, 416)
    blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    class_ids = []
    confidences = []
    boxes = []
    centers = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                centers.append([center_x, center_y])
                confidences.append(float(confidence))
                class_ids.append(class_id)
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        color_array = [(0, 255, 0)] * len(boxes)
        distances_array = [-1] * len(boxes)

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color_copy = color_array.copy()
                distance_copy = distances_array.copy()
                color_array, distances_array = logic.safety_check(boxes, color_copy, i, indexes, classes, class_ids, distance_copy)

                if label == 'person':
                    cv2.rectangle(img, (x, y), (x + w, y + h), color_array[i], 2)
                    if distances_array[i] != -1:
                        cv2.putText(img, "{:.2f}".format(distances_array[i]), (x, y - 10), font, 1, (255, 0, 0), 1)
        cv2.imshow("PROGRAM", img)

#  i get photo from buffer create window and send it to object_recognition func.
def photo_manipulation(buffer, net, classes , ol, index):
    img = buffer.payload.components[0].data
    img = img.reshape(buffer.payload.components[0].height, buffer.payload.components[0].width)
    img_copy = img.copy()
    img_copy = cv2.cvtColor(img, cv2.COLOR_BayerRG2RGB)
    cv2.namedWindow("PROGRAM", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    objects_recognision(img_copy, net, classes, ol)

# main function uses Harvesters to connect my program with Matrix Vision cti software finds my Baluff camera nad
# connect it with my program. I read images from camera, and  send it to photo_manipulation func in a loop until i
# finish running program pressing space
def main():
    h = Harvester()
    h.add_cti_file("C:\Program Files\MATRIX VISION\mvIMPACT Acquire\\bin\\x64\mvGenTLProducer.cti")
    h.update_device_info_list()
    ia = h.create_image_acquirer(id_='VID2005_PID5533_FFB00089')
    try:
        ia.start_image_acquisition()
        i = 0
        done = False
        tiny = False
        net = yolo.yolo_full()
        classes, output_leyers = yolo.load_yolo(net)
        while not done:
            with ia.fetch_buffer() as buffer:
                ## wyświetlam co 20 zdjęcie żeyby czas był mniej więcej rzeczywisty, bo długo trwa to i jest duże opóźnienie
                # wersja na pełnym yolo
                if tiny == False:
                    if i % 20 == 0:
                        photo_manipulation(buffer, net, classes, output_leyers, i)
                if tiny == True:
                    if i % 5 == 0:
                        photo_manipulation(buffer, net, classes, output_leyers, i)

                key = cv2.waitKey(1)
                if key == ord(' '):
                    done = True
                if key == ord('t'):
                    net = yolo.yolo_tiny()
                    classes, output_leyers = yolo.load_yolo(net)
                    tiny= True
                if key == ord('f'):
                    net = yolo.yolo_full()
                    classes, output_leyers = yolo.load_yolo(net)
                    tiny= False
                if cv2.getWindowProperty('PROGRAM', 0) < 0:
                    done = True
                i = i + 1

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        ia.stop_image_acquisition()
        ia.destroy()
        cv2.destroyAllWindows()
        h.reset()

if __name__ == "__main__":
    print("t - change mode to yolo-tiny\nf - change mode to yolo-full\nspace - close program")
    main()


