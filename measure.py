from harvesters.core import Harvester
import traceback
import sys
import cv2
import numpy as np
import time
import yolo
import statistics
import camera
import numpy

# dokładność pomiaru - ilość pobranych próbek
data_nr = 30

## MEASURE GENERUJE PLIK "equations.txt" W KTÓRYM SĄ WSPÓŁCZYNIKI PRZY FORMUŁACH NA Y I W
## FORMUŁA BĘDZIE POBIERANA Z TEGO PLIKU NA POCZĄTKU WYKONYWANIA PROGRAMU CAMERA

def to_file( file_name, y):
    f = open(file_name, 'a')
    s = str(y) + "\n"
    f.write(s)
    f.close()

## finds objects on an image using pre-trained model for detecting objcect and manipulates with them, showing them on screen
def objects_recognision(img, net, classes, output_layers, index_of_photo):

    img = cv2.resize(img, None, fx=0.4, fy=0.4)
    height, width, channels = img.shape
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

        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                if label == 'person':
                    y_new = y + h
                    w_new = w
                    to_file("y.txt", y_new)
                    #f_y = open('y.txt', 'a')
                    #s_y = str(y_new) + "\n"
                    #f_y.write(s_y)
                    #f_y.close()
                    to_file("w.txt", w_new)
                    #f_w = open('w.txt', 'a')
                    #s_w = str(w_new) + "\n"
                    #f_w.write(s_w)
                    #f_w.close()
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow("PROGRAM", img)

def photo_manipulation(buffer, net, classes , ol, index):
    img = buffer.payload.components[0].data
    img = img.reshape(buffer.payload.components[0].height, buffer.payload.components[0].width)
    img_copy = img.copy()
    img_copy = cv2.cvtColor(img, cv2.COLOR_BayerRG2RGB)
    cv2.namedWindow("PROGRAM", cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
    objects_recognision(img_copy, net, classes, ol, index)

def get_and_clean(fname):
    with open(fname) as f:
        lines = [int(i) for i in f]
    open(fname, 'w').close()
    sr = statistics.mean(lines)
    return sr


def camera():
    h = Harvester()
    h.add_cti_file("C:\Program Files\MATRIX VISION\mvIMPACT Acquire\\bin\\x64\mvGenTLProducer.cti")
    h.update_device_info_list()
    ia = h.create_image_acquirer(id_='VID2005_PID5533_FFB00089')

    try:
        ia.start_image_acquisition()
        i = 0
        done = False
        net = yolo.yolo_full()
        classes, output_leyers = yolo.load_yolo(net)

        while not done:
            with ia.fetch_buffer() as buffer:
                if i % 20 == 0:
                    photo_manipulation(buffer, net, classes, output_leyers, i)
                key = cv2.waitKey(1)
                y_size = sum(1 for line in open('y.txt'))
                w_size = sum(1 for line in open('w.txt'))
                if y_size >= data_nr and w_size >= data_nr:
                    done = True
                if cv2.getWindowProperty('PROGRAM', 0) < 0:
                    exit(0)
                i = i + 1
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    finally:
        ia.stop_image_acquisition()
        ia.destroy()
        cv2.destroyAllWindows()
        h.reset()
        y_new = get_and_clean("y.txt")
        w_new = get_and_clean("w.txt")
        return y_new, w_new

def calcualte_y(ys, xs, file):
    func = numpy.polyfit(xs,ys, 2)
    func_r = "{:.6f}".format(func[0]) + "\n" + "{:.6f}".format(func[1]) + "\n" + "{:.6f}".format(func[2]) + "\n"
    file.write(func_r)

def calculate_w(f_y, f_w, width, file):
    w = int(width) / 10
    w_10_cm = [i / w for i in f_w]
    func = numpy.polyfit(f_y, w_10_cm, 1)
    func_r = "{:.6f}".format(func[0]) + "\n" + "{:.6f}".format(func[1]) + "\n"
    file.write(func_r)

def main():

    print("podaj z szacowane pole widzenia (w pionie) kamery w metrach")
    size = input()
    print("podaj swoją szerokosc w barkach")
    width = input()
    arr_size = int(size) * 2
    print("stań w najbliższej odległości dla której widać całą sylwetkę w kamerze \ngry pojawi się widok z kamery stój nieruchomo aż okno zniknie \n"
        "gdy ekran zminknie przesuń się o 0,5 m do tyłu \ntakiego pomiaru dokonasz", arr_size, "razy ")
    time.sleep(5)
    cmeters = numpy.zeros(arr_size)
    sr_y = numpy.zeros(arr_size)  # srednie wyniki y_floor
    sr_w = numpy.zeros(arr_size)  # srednie wyniki szerokości postaci w pix
    for a in range(arr_size):
        cmeters[a] = a * 50 + 50
    for i in range(arr_size):
        y, w = camera()
        sr_y[i] = y
        sr_w[i] = w
        time.sleep(5)
    file = open("equations2.txt", 'a') # to powinno być equations.txt ale jeszcze nie zrobiłam wystarzająco dużo testów
    file.truncate(0)
    calcualte_y(cmeters, sr_y, file)
    calculate_w(sr_y, sr_w, width, file)
    file.close()

if __name__ == "__main__":
    print("witam w programie pomiarowym ")
    main()