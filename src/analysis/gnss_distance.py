# include
import math
import re

F = 1.0 / 298.257223563
A = 6378137.0
e2 = 2 * F - F * F
PI = math.pi
radian = PI / 180

fromlatlon = [0, 0, 0]
to_positon = [0, 0, 0]


# position ={latitude ,longitude , altitude}
def getDistance(fromPosition, toPosition):
    fromXyz = blhToXyz(fromPosition)
    toXyz = blhToXyz(toPosition)
    distance = math.sqrt(math.pow(fromXyz[0] - toXyz[0], 2)
                         + math.pow(fromXyz[1] - toXyz[1], 2)
                         + math.pow(fromXyz[2] - toXyz[2], 2))
    print(distance)


def blhToXyz(position):
    position[0] = position[0] * radian
    position[1] = position[1] * radian
    cosb = math.cos(position[0])
    sinb = math.sin(position[0])
    N = A / math.sqrt(1 - e2 * sinb * sinb)
    dx = (N + position[2]) * cosb * math.cos(position[1])
    dy = (N + position[2]) * cosb * math.sin(position[1])
    dz = (N * (1 - e2) + position[2]) * sinb
    return dx, dy, dz


def formate(latlon):
    latlon = math.floor(latlon / 100) + (latlon % 100) / 60.0
    return latlon


# DMS转化为DDD
def DmsToDdd(data):
    dms = re.split('[°′″]', data)
    ddd = int(dms[0]) + float(dms[1]) / 60 + float(dms[2]) / 3600
    return round(ddd, 8)


# DD.DDD转化为DMS
def DddToDms(data):
    ddd = int(data)
    ms = data - ddd
    mmm = int(ms * 60)
    sss = (ms * 60 - mmm) * 60
    return str(ddd) + '°' + str(mmm) + '′' + str(sss) + '″'


if __name__ == '__main__':
    # DmsToDdd('31°21′20.44″')
    # DmsToDdd("121°26′1.40″")

    # # 4003.8515829, 11613.6874719, 54.656]
    # print('======c===========')
    # print((DmsToDdd('40°05′42.012″')))
    # print((DmsToDdd('116°12′37.8332″')))
    # print('======b===========')
    # print((DmsToDdd('40°05′42.205″')))
    # print((DmsToDdd('116°12′39.4121″')))
    # print('======a===========')
    # print((DmsToDdd('40°05′42.1921″')))
    # print((DmsToDdd('116°12′40.3425″')))
    # 4003.8942378, N, 11613.6288949

    # 30°27′31.419036″	114°24′17.37″
    print(DmsToDdd('30°27′20.766114″'), DmsToDdd('114°24′08.382822″'))
