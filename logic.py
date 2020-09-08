import math

alert = 150

h_real = 170
## kąt  nachylenie (0, 90), gdzie 0 to kamera patrząca na wprost (równoległa do ziemi) a 90 to kamera skierowana prostopadle do ziemi
alfa = 50

def smallest(new, old):
    if abs(new) < old:
        return abs(new)
    else:
        return old

def sr_geom(delta_x , delta_y):
    cube = delta_x**2 + delta_y**2
    wynik = math.sqrt(cube)
    return wynik

def y_od_10cm_na_pix(x):
    #result= float(camera.lines[3]) * x + float(camera.lines[4])
    #return result
    return 0.0166 * x + 7.6545

def get_x(x, x_curr, w, w_curr, h):
    l = x
    p = x + w
    l_curr = x_curr
    p_curr = x_curr + w_curr
    min_x = abs(l_curr - l)
    min_x = smallest(l_curr - p, min_x)
    min_x = smallest(p_curr - l, min_x)
    min_x = smallest(p_curr - p, min_x)
    ten_cm_pix = y_od_10cm_na_pix(h)
    odl = min_x * 10 / ten_cm_pix
    return odl

def y_func(x):
    # result= float(camera.lines[0]) * x**2 + float(camera.lines[1]) * x + float(camera.lines[2])
    # return result
    return 0.0019 * float(x**2) - 2.2879 * x + 744.26

def get_y(y, y_curr):
    odl1 = y_func(y)
    odl2 = y_func(y_curr)
    delta = abs(odl1 - odl2)
    return delta

def safety_check(boxes, colors, curr_i, indexes, classes, class_id, distance_array):

    distance = 0
    for i in range(len(indexes)):
        nr = int(indexes[i])
        if int(indexes[i]) > curr_i:
            type1 = (classes[class_id[curr_i]])
            type2 = str(classes[class_id[nr]])
            if type1 == type2 == 'person':
                x_curr, y_curr, w_curr, h_curr = boxes[curr_i]
                x, y, w, h = boxes[int(indexes[i])]
                floor_lvl_curr = y_curr + h_curr
                floor_lvl = y + h
                distance_y = get_y(floor_lvl, floor_lvl_curr)
                y_sr = (floor_lvl + floor_lvl_curr) / 2
                distance_x = get_x(x, x_curr, w, w_curr, y_sr)
                distance = sr_geom(distance_x, distance_y)

                if distance < alert:
                    print(int(indexes[i]) , " i ", int(curr_i), " : ", distance)
                    colors[int(indexes[i])] = (0, 0, 255)
                    colors[int(curr_i)] = (0, 0, 255)
                    if distance < distance_array[int(curr_i)] or distance_array[int(curr_i)] == -1:
                        distance_array[int(curr_i)] = distance
                    if distance < distance_array[nr] or distance_array[nr] == -1:
                        distance_array[nr] = distance

    return colors, distance_array


    # shorter = h if h < h_curr else h_curr
    # distance_x = get_x(x, x_curr, h, h_curr, shorter)
    # distance_y = get_y(y, y_curr, shorter)
    # distance_z = get_z(h, h_curr)
    # yz2 = float( distance_y**2) + float(distance_z**2)
    # y_z = math.sqrt(yz2)
    # distance2 = float(distance_x**2) + float(y_z**2)
    # distance = math.sqrt(distance2)

## WESJA DZIAŁAJĄCA NA KUBKACH
# if type1 == type2 == 'cup':
#   x_curr, y_curr, w_curr, h_curr = boxes[curr_i]
#   x, y, w, h = boxes[int(indexes[i])]
#   shorter = h if h < h_curr else h_curr
#   distance_x = get_x(x, x_curr, h, h_curr, shorter)
#   distance_y = get_y(y, y_curr, shorter)
#   distance_z = get_z(h, h_curr)
###distance_z_2 = get_z_2(h, h_curr)
###print("h z nowego wzoru: ", distance_z_2)
# distance_y_z = math.sqrt(float(distance_y ** 2) + float(distance_z ** 2))
#####print("w osi y: ", distance_y)
## w przypaku wysokich kątów y robi róznicę, pomyślę jeszcze nad poprawnością
# dxd = distance_x ** 2 + distance_y_z ** 2
# distance = math.sqrt(dxd)
# print("w osi z: ", distance_z, "w osi x: ", distance_x, "w ogóle: ", distance)

## METODA ZGLĘDEM ŚRODKA
##metoda względem środka ## średnio działa
###center_x = x + w/2
###center_y = y + h/2
##center_x_curr = x_curr + w_curr/2
###center_y_curr = y_curr + h_curr/2
##dis_2 = (center_x - center_x_curr)**2 + (center_y - center_y_curr)**2
##dis = math.sqrt(dis_2)
# skala = (h + h_curr)/2
# odleglosc= (5 * dis) /skala
# print("odleglosc: ",odleglosc)
## KONIEC METODY WZGLĘDEM ŚRODKA


## kamera pod kątem 90 stopni do ściany
# pobiera wartość w pix i zwraca odległośćw cm
def human_90(x):
    odl = 89866 * float(1/(x**0.952))
    return odl

def get_z(h, h_curr):
    odl = human_90(h)
    odl_curr = human_90(h_curr)
    distance = abs(odl - odl_curr)
    return distance

def rotacja_p(x,y):
    rad = alfa * (math.pi / 180)
    x_new = x * math.cos(rad) - y * math.sin(rad)
    y_new = x * math.sin(rad) + y * math.cos(rad)
    return x_new, y_new

