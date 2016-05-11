class Metrics:
    def __init__(self, time, temp, humd, wind_speed_10min, wind_dir_10min):
        self.time = time
        self.temp = temp
        self.humd = humd
        self.wind_speed_10min = wind_speed_10min
        self.wind_dir_10min = wind_dir_10min
        self.sunrise = None
        self.sunset = None

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)
    def cal(self):
        return self.temp + self.humd