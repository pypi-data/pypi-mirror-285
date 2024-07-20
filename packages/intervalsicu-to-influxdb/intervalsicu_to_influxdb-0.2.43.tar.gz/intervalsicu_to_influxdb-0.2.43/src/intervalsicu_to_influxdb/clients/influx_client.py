from influxdb_client import BucketsApi, InfluxDBClient
from influxdb_client.client.write_api import ASYNCHRONOUS, SYNCHRONOUS


class InfluxClient:
    def __init__(self, url, token, org, bucket, timeout=10000, reset=False):
        self._org = org
        self._bucket = bucket
        self._client = InfluxDBClient(url=url, token=token, timeout=timeout)
        self._buckets = BucketsApi(self._client)
        bucket = self.get_bucket_by_name(self._bucket)
        if bucket is None:
            self.create_bucket(self._bucket)
        if reset:
            self.reset_bucket()

    def write_data(self, data, write_option=SYNCHRONOUS):
        try:
            write_api = self._client.write_api(write_option)
            write_api.write(self._bucket, self._org, data, write_precision="s")
        except Exception as e:
            print("Error on write influx:", e)

    def reset_bucket(self):
        bucket = self.get_bucket_by_name(self._bucket)
        if bucket is not None:
            try:
                print("Deleting bucket...")
                self._buckets.delete_bucket(bucket)
            except Exception as e:
                print("Error deleting")
                print(e)
        self.create_bucket(self._bucket)

    def delete_bucket(self, name):
        return self._buckets.delete_bucket(self._buckets.find_bucket_by_name(name))

    def create_bucket(self, name):
        print("Creating bucket with name", name)
        return self._buckets.create_bucket(bucket_name=name, org=self._org)

    def get_bucket_by_name(self, name):
        return self._buckets.find_bucket_by_name(name)

    def get_buckets(self):
        return self._buckets.find_buckets()

    def status(self):
        return self._client.health()
