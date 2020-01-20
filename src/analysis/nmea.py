# NMEA-0183
from datetime import timedelta, datetime
from src.analysis import Gauss


class GNGGAFrame:

    def __init__(self, name, data, localTime):
        self._name = name.split('.txt')[0]
        self._time = localTime
        self.timeCheck = False
        self._gga = None
        self.parseData(data)

    def get_name(self):
        return self._name

    def nmeatime(self, date):
        time = datetime.strptime(date, '%H%M%S.%f')
        if (time.microsecond > 970) | time.microsecond < 30:
            time += timedelta(seconds=1)
        # 当GNGGA中出现'000000.'时，天数-=1
        if '000000.' in date:
            self._time += timedelta(days=1)
        return time.replace(year=self._time.year, month=self._time.month, day=self._time.day)

    def parseData(self, data):
        '''
            check gngga data timestamp and update it's type to YYmmdd-hhmmss.f
        '''
        if self.timeCheck is False:
            for time in data.loc[:, '1']:
                if '000000.' in time:
                    self._time -= timedelta(days=1)
        data.loc[:, '1'] = data.loc[:, '1'].apply(lambda t: self.nmeatime(t))
        self._gga = data.set_index('1')
        print(self._gga)
        self._gga.loc[:, '2'] = self._gga.loc[:, '2'].astype(float).apply(lambda x: self.dmTodd(x))
        self._gga.loc[:, '4'] = self._gga.loc[:, '4'].astype(float).apply(lambda x: self.dmTodd(x))

    def dmTodd(self, dm):
        dd = int(dm / 100)
        res = dd + (dm % 100) / 60
        return res

    def get_fixState(self):
        return self._gga.loc[:, '6'].astype(float)

    def get_sateNum(self):
        return self._gga.loc[:, '7'].astype(float)

    def get_latitude(self):
        return self._gga.loc[:, '2']

    def get_longitude(self):
        return self._gga.loc[:, '4']

    def get_altitude(self):
        return self._gga.loc[:, '9'].astype(float)

    def get_scatter(self):
        latitude = self.get_latitude()
        longitude = self.get_longitude()
        altitude = self.get_altitude()
        xlist, ylist, zlist = list(), list(), list()
        centerLongitude = None
        for i in range(len(latitude)):
            if (centerLongitude is None) & (longitude[i] is not None) & (longitude[i] != 0):
                centerLongitude = longitude[i]
            try:
                x, y, z = Gauss.Gauss_BLHToXYH(latitude[i], longitude[i], altitude[i], centerLongitude)
                xlist.append(x)
                ylist.append(y)
                zlist.append(z)
            except Exception as e:
                print(e)
                continue

        return xlist, ylist, zlist


class Satellite:

    def __init__(self, name, visible_Times, cn0):
        self._name = name
        self.visible_Times = visible_Times
        self._cn0 = cn0

    def get_name(self):
        return self._name

    def get_visible_Times(self):
        return self.visible_Times

    def get_mean_cn0(self):
        return self._cn0


GPGSV = '$GPGSV'
GBGSV = '$GBGSV'
GLGSV = '$GLGSV'
GAGSV = '$GAGSV'

GSVLIST = [GPGSV, GBGSV, GLGSV, GAGSV]
GSVNAME = ['G', 'C', 'R', 'E']


class GSV:
    '''
        GPGSV Gps
        GBGSV Beidou
        GLGSV GLONASS
        GAGSV Galileo
        gsv = '$GPGSV, 3,1,10, 10,33,308,45, 12,02,143,39, 13,16,059,40, 15,47,059,49, 1*6A'
    '''

    def __init__(self, name, gsv):
        self._name = name.split('.txt')[0]
        self._satellites = self.parseGSV(gsv)
        # print(self._gsv)

    def parseGSV(self, data):
        satellites = []
        print(type(data))
        print(data[data['0'] == GPGSV])
        for i in range(len(GSVLIST)):
            gsv = data[data['0'] == GSVLIST[i]]
            gsd = gsv[['4', '7']].dropna()
            gsd.columns = ['s', 'n']
            gsd2 = gsv[['8', '11']].dropna()
            gsd2.columns = ['s', 'n']
            gsd3 = gsv[['12', '15']].dropna()
            gsd3.columns = ['s', 'n']
            gsd4 = gsv[['16', '19']].dropna()
            gsd4.columns = ['s', 'n']
            gsvsn = gsd.append([gsd2, gsd3, gsd4], ignore_index=True, sort=False)
            print(gsvsn)
            s = gsvsn.loc[:, 's']
            for name in set(s):
                cn0 = gsvsn.loc[gsvsn['s'] == name].astype(int)
                satellites.append(Satellite(GSVNAME[i] + name, len(cn0), int(cn0['n'].mean())))
        return sorted(satellites, key=lambda x: x.get_mean_cn0())

    def get_satellites_status(self):

        return self._satellites

    def get_name(self):
        return self._name


if __name__ == '__main__':
    gsv = GSV()
