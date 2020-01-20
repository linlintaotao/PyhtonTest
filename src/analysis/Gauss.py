# coding: utf-8
import math

F = 1.0 / 298.257223563
A = 6378137.0
e2 = 2 * F - F * F
e4 = e2 * e2
e6 = e2 * e2 * e2
e8 = e4 * e4
D2R = math.pi / 180.0
A0 = 1. + 3. / 4. * e2 + 45. / 64. * e4 + 350. / 512. * e6 + 11025. / 16384. * e8
A2 = -.5 * (3. / 4. * e2 + 60. / 64. * e4 + 525. / 512. * e6 + 17640. / 16384. * e8)
A4 = .25 * (15. / 64. * e4 + 210. / 512. * e6 + 8820. / 16384. * e8)
A6 = -1 / 6. * (35. / 512. * e6 + 2520. / 16384. * e8)
A8 = 1 / 8. * (315. / 16384. * e8)


# R2D =

def GaussToMeter(B):
    dRA = 0.0
    X = (A + dRA) * (1. - e2) \
        * (A0 * B + A2 * math.sin(2. * B) + A4 * math.sin(4. * B) + A6 * math.sin(6. * B) + A8 * math.sin(8. * B))
    return X


# BLH_Degree[3] = latitude, longitude ,altitude
def Gauss_BLHToXYH(latitude, longtidute, altitude, dCenterMeriadian):
    latitude = latitude * D2R
    longitude = longtidute * D2R
    altitude = altitude

    L0 = dCenterMeriadian * D2R
    cosb = math.cos(latitude)
    sinb = math.sin(latitude)

    dl = longitude - L0
    dlcosb = dl * cosb
    dlcosb2 = dlcosb * dlcosb
    dlcosb3 = dlcosb2 * dlcosb
    dlcosb5 = dlcosb3 * dlcosb2
    dlcosb7 = dlcosb5 * dlcosb2

    dA = 0.0

    dM0 = GaussToMeter(0)
    dM = GaussToMeter(latitude)

    dTx = 0
    dTy = 500000
    dTK = 1.0
    t, t2, t4, t6 = 0.0, 0.0, 0.0, 0.0
    t = math.tan(latitude)
    t2 = t * t
    t4 = t2 * t2
    t6 = t4 * t2

    v = (A + dA) / math.sqrt(1.0 - e2 * sinb * sinb)

    rou = (A + dA) * (1. - e2) / math.pow(1 - e2 * sinb * sinb, 1.5)

    w, w2, w3, w4 = 0.0, 0.0, 0.0, 0.0
    w = v / rou
    w2 = w * w
    w3 = w2 * w
    w4 = w2 * w2

    dx = dTx + dTK * (dM - dM0) + dTK * v * sinb * dl * (
            dlcosb / 2. + dlcosb3 / 24. * (4. * w2 + w - t2)
            + dlcosb5 / 720. * (
                    8. * w4 * (11. - 24. * t2) - 28. * w3 * (1 - 6. * t2) + w2 * (1. - 32. * t2) - w * 2 * t2 + t4)
            + dlcosb7 / 40320. * (1385. - 3111 * t2 + 543 * t4 - t6))

    dy = dTy + dTK * v * (
            dlcosb + dlcosb3 / 6.0 * (w - t2)
            + dlcosb5 / 120. * (4.0 * w3 * (1. - 6. * t2) + w2 * (1. + 8. * t2) - 2 * w * t2 + t4)
            + dlcosb7 / 5040. * (61. - 479 * t2 + 179 * t4 - t6))

    return dx, dy, altitude
