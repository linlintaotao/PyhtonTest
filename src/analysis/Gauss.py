# coding: utf-8
import math
from datetime import timedelta, datetime


def LatLon2XY(latitude, longitude):
    a = 6378137.0
    e2 = 0.0066943799013

    # 将经纬度转换为弧度
    latitude2Rad = (math.pi / 180.0) * latitude

    beltNo = int((longitude + 1.5) / 3.0)  # 计算3度带投影度带号
    L = beltNo * 3  # 计算中央经线
    l0 = longitude - L  # 经差
    tsin = math.sin(latitude2Rad)
    tcos = math.cos(latitude2Rad)
    t = math.tan(latitude2Rad)
    m = (math.pi / 180.0) * l0 * tcos
    et2 = e2 * pow(tcos, 2)
    et3 = e2 * pow(tsin, 2)
    X = 111132.9558 * latitude - 16038.6496 * math.sin(2 * latitude2Rad) + 16.8607 * math.sin(
        4 * latitude2Rad) - 0.0220 * math.sin(6 * latitude2Rad)
    N = a / math.sqrt(1 - et3)

    x = X + N * t * (0.5 * pow(m, 2) + (5.0 - pow(t, 2) + 9.0 * et2 + 4 * pow(et2, 2)) * pow(m, 4) / 24.0 + (
            61.0 - 58.0 * pow(t, 2) + pow(t, 4)) * pow(m, 6) / 720.0)
    y = 500000 + N * (m + (1.0 - pow(t, 2) + et2) * pow(m, 3) / 6.0 + (
            5.0 - 18.0 * pow(t, 2) + pow(t, 4) + 14.0 * et2 - 58.0 * et2 * pow(t, 2)) * pow(m, 5) / 120.0)

    return x, y


if __name__ == '__main__':
    print('start Gauss_BLHToXYH %s' % datetime.strftime(datetime.now(), '%H%M%S.%f'))
    # print(Gauss_BLHToXYH(40.07837722329, 116.23514827596, 54, 116.23514827596))
    print('end Gauss_BLHToXYH %s' % datetime.strftime(datetime.now(), '%H%M%S.%f'))
    print(LatLon2XY(40.07837722329, 116.23514827596))
    print('end LatLon2XY %s' % datetime.strftime(datetime.now(), '%H%M%S.%f'))
