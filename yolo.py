import cv2

# load lighter, smaller version of pre-trained object detecting net
def yolo_tiny():
    net = cv2.dnn.readNet("yolov3-tiny.weights", "darknet/cfg/yolov3-tiny.cfg")
    return net

# load full version of pre-trained object detecting net
def yolo_full():
    net = cv2.dnn.readNet("yolov3.weights", "darknet/cfg/yolov3.cfg")
    return net

# load yolo-coco data base names
def load_yolo(net):
    # aby przyspieszyło powinno działać na GPU zamiast CPU
    # net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
    # net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return classes, output_layers
