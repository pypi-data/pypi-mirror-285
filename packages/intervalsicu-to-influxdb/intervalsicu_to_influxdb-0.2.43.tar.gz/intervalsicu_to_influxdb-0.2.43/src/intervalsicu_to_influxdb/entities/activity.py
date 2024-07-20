import datetime

from ..my_utils import MyUtils

utils = MyUtils()


class Activity(dict):
    fields = [
        "id",
        "start_date_local",
        "type",
        "icu_ignore_time",
        "icu_pm_cp",
        "icu_pm_w_prime",
        "icu_pm_p_max",
        "icu_pm_ftp",
        "icu_pm_ftp_secs",
        "icu_pm_ftp_watts",
        "icu_ignore_power",
        "icu_rolling_cp",
        "icu_rolling_w_prime",
        "icu_rolling_p_max",
        "icu_rolling_ftp",
        "icu_rolling_ftp_delta",
        "icu_training_load",
        "icu_atl",
        "icu_ctl",
        "paired_event_id",
        "name",
        "description",
        "start_date",
        "distance",
        "icu_distance",
        "moving_time",
        "elapsed_time",
        "coasting_time",
        "total_elevation_gain",
        "timezone",
        "trainer",
        "commute",
        "max_speed",
        "average_speed",
        "device_watts",
        "has_heartrate",
        "max_heartrate",
        "average_heartrate",
        "average_cadence",
        "calories",
        "average_temp",
        "min_temp",
        "max_temp",
        "avg_lr_balance",
        "gap",
        "gap_model",
        "use_elevation_correction",
        "race",
        "gear",
        "perceived_exertion",
        "device_name",
        "power_meter",
        "power_meter_serial",
        "power_meter_battery",
        "crank_length",
        "external_id",
        "file_sport_index",
        "file_type",
        "icu_athlete_id",
        "created",
        "icu_sync_date",
        "analyzed",
        "icu_ftp",
        "icu_w_prime",
        "threshold_pace",
        "icu_hr_zones",
        "pace_zones",
        "lthr",
        "icu_resting_hr",
        "icu_weight",
        "icu_power_zones",
        "icu_sweet_spot_min",
        "icu_sweet_spot_max",
        "icu_power_spike_threshold",
        "trimp",
        "icu_warmup_time",
        "icu_cooldown_time",
        "icu_chat_id",
        "icu_ignore_hr",
        "ignore_velocity",
        "ignore_pace",
        "icu_weighted_avg_watts",
        "icu_training_load_data",
        "interval_summary",
        "stream_types",
        "has_segments",
        "power_field_names",
        "power_field",
        "icu_zone_times",
        "icu_hr_zone_times",
        "pace_zone_times",
        "gap_zone_times",
        "use_gap_zone_times",
        "tiz_order",
        "icu_achievements",
        "icu_intervals_edited",
        "lock_intervals",
        "icu_lap_count",
        "icu_joules",
        "icu_joules_above_ftp",
        "icu_max_wbal_depletion",
        "icu_recording_time",
        "icu_hrr",
        "icu_sync_error",
        "icu_color",
        "icu_power_hr_z2",
        "icu_power_hr_z2_mins",
        "icu_cadence_z2",
        "icu_rpe",
        "feel",
        "kg_lifted",
        "decoupling",
        "icu_median_time_delta",
        "p30s_exponent",
        "workout_shift_secs",
        "strava_id",
        "lengths",
        "pool_length",
        "compliance",
        "source",
        "oauth_client_id",
        "oauth_client_name",
        "power_load",
        "hr_load",
        "pace_load",
        "hr_load_type",
        "pace_load_type",
        "tags",
        "recording_stops",
        "pace",
        "athlete_max_hr",
        "group",
        "icu_average_watts",
        "icu_intensity",
        "icu_variability_index",
        "icu_efficiency_factor",
        "icu_power_hr",
        "session_rpe",
        "average_stride",
    ]

    iterable_fields = [
        "gear",
        "interval_summary",
        "power_field_names",
        "icu_hrr",
        "stream_types",
        "recording_stops",
        "icu_achievements",
    ]

    iterable_zones = [
        "icu_hr_zones",
        "pace_zones",
        "icu_power_zones",
        "icu_zone_times",
        "icu_hr_zone_times",
        "pace_zone_times",
        "gap_zone_times",
    ]

    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    def extract_data(self, data):
        fields = {}
        activity = Activity(**data)
        for key, value in activity.items():
            if key not in self.iterable_fields and key not in self.iterable_zones:
                if key == "pace":
                    fields[key] = value
                    fields["converted_pace"] = utils.convert_pace(value)
                elif key in ["gear", "group"]:
                    fields[key] = str(value)
                elif key == "start_date_local":
                    fields[key] = value
                    fields["activity_date"] = datetime.datetime.strptime(
                        value, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%Y-%m-%d")
                elif key in ["max_speed", "average_speed"]:
                    fields[key] = value
                    fields["converted_speed"] = utils.convert_speed(value)
                else:
                    fields[key] = value
        for key, value in self.extract_zones(activity).items():
            fields[key] = value
        return fields

    def extract_zones(self, activity):
        zones = {}
        for zone in self.iterable_zones:
            try:
                if activity[zone] is not None:
                    if zone != "icu_zone_times":
                        for j, value_zone in enumerate(activity[zone]):
                            zones[zone + "_" + str(j)] = value_zone
                    else:
                        for value_zone in activity[zone]:
                            zones[zone + "_" + value_zone["id"]] = value_zone["secs"]
            except Exception as e:
                print(e)
                continue
        return zones

    def get_streams(self, data):
        streams = []
        for stream in data["stream_types"]:
            streams.append(stream)
        return streams

    def get_intervals_summary(self, data):
        intervals_summary = []
        for interval_summary in data["interval_summary"]:
            intervals_summary.append(interval_summary)
        return intervals_summary

    def get_icu_hrr(self, data):
        hrr = {}
        hrr["start_index"] = data["start_index"]
        hrr["end_index"] = data["end_index"]
        hrr["start_time"] = data["start_time"]
        hrr["end_time"] = data["end_time"]
        hrr["start_bpm"] = data["start_bpm"]
        hrr["end_bpm"] = data["end_bpm"]
        hrr["average_watts"] = data["average_watts"]
        hrr["hrr"] = data["hrr"]
        return hrr

    def get_recording_stops(self, data):
        stops = []
        for stop in data["recording_stops"]:
            stops.add(stop)
        return stops
