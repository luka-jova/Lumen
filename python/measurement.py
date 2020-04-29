from datetime import datetime as dt

class Measurement:
    ATTRIBUTES = [
        "machine_name",
        "sensor_type",
        "date_measurement",
        "start_timestamp",
        "end_timestamp",
        "realvalue",
        "unit"
    ]
    CSV_HEADER = ';'.join(['"' + i + '"' for i in ATTRIBUTES]) + '\n'
    def __init__(self, csv):
        attributes = csv.split(';')
        for i, attr in enumerate(attributes):
            self[Measurement.ATTRIBUTES[i]] = attr

    def to_csv(self, attributes = ATTRIBUTES):
        return ';'.join([self[attr] for attr in attributes])

    def __getitem__(self, key):
        if type(key) is str:
            if key == "machine_name":
                return self.machine_name
            elif key == "sensor_type":
                return self.sensor_type
            elif key == "date_measurement":
                return dt.fromordinal(self.date_measurement).strftime("%Y-%m-%d")
            elif key == "start_timestamp":
                return dt.fromtimestamp(self.start_timestamp).strftime('"%Y-%m-%d %H:%M:%S.%f"')
            elif key == "end_timestamp":
                return dt.fromtimestamp(self.end_timestamp).strftime('"%Y-%m-%d %H:%M:%S.%f"')
            elif key == "realvalue":
                return str(self.realvalue)
            elif key == "unit":
                return self.unit
            else:
                raise KeyError()

    def __setitem__(self, key, value):
        if type(key) is str:
            if key == "machine_name":
                self.machine_name = value
            elif key == "sensor_type":
                self.sensor_type = value
            elif key == "date_measurement":
                if type(value) == int:
                    self.date_measurement = value
                elif type(value) == str:
                    self.date_measurement = dt.strptime(value, "%Y-%m-%d").toordinal()
            elif key == "start_timestamp":
                if type(value) == int:
                    self.start_timestamp = value
                elif type(value) == str:
                    if '.' in value:
                        self.start_timestamp = dt.strptime(value, '"%Y-%m-%d %H:%M:%S.%f"').timestamp()
                    else:
                        self.start_timestamp = dt.strptime(value, '"%Y-%m-%d %H:%M:%S"').timestamp()
            elif key == "end_timestamp":
                if type(value) == int:
                    self.end_timestamp = value
                elif type(value) == str:
                    if '.' in value:
                        self.end_timestamp = dt.strptime(value, '"%Y-%m-%d %H:%M:%S.%f"').timestamp()
                    else:
                        self.end_timestamp = dt.strptime(value, '"%Y-%m-%d %H:%M:%S"').timestamp()
            elif key == "realvalue":
                self.realvalue = float(value)
            elif key == "unit":
                self.unit = value
            else:
                raise KeyError()

# FL02;lifting_gear_a_max;2019-07-10;"2019-07-10 07:13:29.647";"2019-07-10 07:13:29.647";8609.316;mg (milli-g)

