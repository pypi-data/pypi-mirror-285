class MyUtils:
    def convert_pace(self, time):
        """Convert pace from m/s to min/km

        Args:
            time (float): pace in m/s

        Returns:
            float: pace converted to min/km in float format. Example: 4:30 => 4.3, 4:55 => 4.55
        """
        try:
            time = float((float(3600 / (float(time) * 3.6))) / 60)
            res = time - int(time)
            res = round(res * 0.6, 2)
            if res == 0.6:
                time = int(time) + 1
                res = 0
            return float(int(time) + res)
        except Exception:
            return time

    def convert_speed(self, time):
        """Convert speed from m/s to km/h

        Args:
            time (float): speed in m/s

        Returns:
            float: speed converted to km/h
        """
        try:
            return float(float(time) * 3.6)
        except Exception:
            return time
