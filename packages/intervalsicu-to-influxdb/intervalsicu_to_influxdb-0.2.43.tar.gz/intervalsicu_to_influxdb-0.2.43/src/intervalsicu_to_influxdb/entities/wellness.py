class Wellness(dict):
    fields = [
        "id",
        "ctl",
        "atl",
        "rampRate",
        "ctlLoad",
        "atlLoad",
        "sportInfo",
        "updated",
        "weight",
        "restingHR",
        "hrv",
        "hrvSDNN",
        "menstrualPhase",
        "menstrualPhasePredicted",
        "kcalConsumed",
        "sleepSecs",
        "sleepScore",
        "sleepQuality",
        "avgSleepingHR",
        "soreness",
        "fatigue",
        "stress",
        "mood",
        "motivation",
        "injury",
        "spO2",
        "systolic",
        "diastolic",
        "hydration",
        "hydrationVolume",
        "readiness",
        "baevskySI",
        "bloodGlucose",
        "lactate",
        "bodyFat",
        "abdomen",
        "vo2max",
        "comments",
        "steps",
        "respiration",
        "locked",
    ]

    iterable_fields = [
        "sportInfo",
    ]

    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    def extract_data(self, data):
        fields = {}
        wellness = Wellness(**data)
        for key, value in wellness.items():
            if key not in Wellness().fields:
                continue
            if key not in self.iterable_fields:
                fields[key] = value
                if key == "ctl":
                    ctl = value
                if key == "atl":
                    atl = value
        fields["form"] = ctl - atl
        fields["form_percent"] = ((ctl - atl) / ctl) * 100
        fields["acwr"] = atl / ctl
        return fields

    def sport_info(self, wellness):
        # TODO: to be implemented
        return
