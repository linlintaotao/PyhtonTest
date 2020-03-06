# coding: utf-8
import math
from datetime import timedelta, datetime


# F = 1.0 / 298.257223563
# A = 6378137.0
# e2 = 2 * F - math.pow(F, 2)
# # e4 = e2 * e2
# e4 = math.pow(e2, 2)
# # e6 = e2 * e2 * e2
# e6 = math.pow(e2, 3)
# # e8 = e4 * e4
# e8 = math.pow(e4, 2)
# D2R = math.pi / 180.0
# A0 = 1. + 3. / 4. * e2 + 45. / 64. * e4 + 350. / 512. * e6 + 11025. / 16384. * e8
# A2 = -.5 * (3. / 4. * e2 + 60. / 64. * e4 + 525. / 512. * e6 + 17640. / 16384. * e8)
# A4 = .25 * (15. / 64. * e4 + 210. / 512. * e6 + 8820. / 16384. * e8)
# A6 = -1 / 6. * (35. / 512. * e6 + 2520. / 16384. * e8)
# A8 = 1 / 8. * (315. / 16384. * e8)
#
#
# def GaussToMeter(B):
#     dRA = 0.0
#     X = (A + dRA) * (1. - e2) \
#         * (A0 * B + A2 * math.sin(2. * B) + A4 * math.sin(4. * B) + A6 * math.sin(6. * B) + A8 * math.sin(8. * B))
#     return X
#
#
# # BLH_Degree[3] = latitude, longitude ,altitude
# def Gauss_BLHToXYH(latitude, longitude, altitude, dCenterMeriadian):
#     if altitude is  None:
#         return LatLon2XY(latitude, longitude)
#     else:
#         latitude = latitude * D2R
#         longitude = longitude * D2R
#
#         L0 = dCenterMeriadian * D2R
#         cosb = math.cos(latitude)
#         sinb = math.sin(latitude)
#
#         dl = longitude - L0
#         dlcosb = dl * cosb
#         # dlcosb2 = dlcosb * dlcosb
#         dlcosb2 = math.pow(dlcosb, 2)
#         dlcosb3 = dlcosb2 * dlcosb
#         dlcosb5 = dlcosb3 * dlcosb2
#         dlcosb7 = dlcosb5 * dlcosb2
#
#         dA = 0.0
#
#         dM0 = GaussToMeter(0)
#         dM = GaussToMeter(latitude)
#
#         dTx = 0
#         dTy = 500000
#         dTK = 1.0
#         t, t2, t4, t6 = 0.0, 0.0, 0.0, 0.0
#         t = math.tan(latitude)
#         # t2 = t * t
#         t2 = math.pow(t, 2)
#         # t4 = t2 * t2
#         t4 = math.pow(t2, 2)
#         t6 = t4 * t2
#
#         v = (A + dA) / math.sqrt(1.0 - e2 * sinb * sinb)
#
#         rou = (A + dA) * (1. - e2) / math.pow(1 - e2 * sinb * sinb, 1.5)
#
#         w, w2, w3, w4 = 0.0, 0.0, 0.0, 0.0
#         w = v / rou
#         w2 = math.pow(w, 2)
#         # w2 = w * w
#         w3 = w2 * w
#         # w4 = w2 * w2
#         w4 = math.pow(w2, 2)
#
#         dx = dTx + dTK * ((dM - dM0) + v * sinb * dl * (
#                 dlcosb / 2.0 + dlcosb3 / 24.0 * (4. * w2 + w - t2)
#                 + dlcosb5 / 720. * (
#                         8. * w4 * (11. - 24. * t2) - 28. * w3 * (1 - 6. * t2) + w2 * (1. - 32. * t2) - w * 2 * t2 + t4)
#                 + dlcosb7 / 40320. * (1385. - 3111 * t2 + 543 * t4 - t6)))
#
#         dy = dTy + dTK * v * (
#                 dlcosb + dlcosb3 / 6.0 * (w - t2)
#                 + dlcosb5 / 120. * (4.0 * w3 * (1. - 6. * t2) + w2 * (1. + 8. * t2) - 2 * w * t2 + t4)
#                 + dlcosb7 / 5040. * (61. - 479 * t2 + 179 * t4 - t6))
#
#         return dx, dy, altitude


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
    print(Gauss_BLHToXYH(40.07837722329, 116.23514827596, 54, 116.23514827596))
    print('end Gauss_BLHToXYH %s' % datetime.strftime(datetime.now(), '%H%M%S.%f'))
    print(LatLon2XY(40.07837722329, 116.23514827596))
    print('end LatLon2XY %s' % datetime.strftime(datetime.now(), '%H%M%S.%f'))
