import unittest
import time
from datetime import datetime, timedelta
from formant.sdk.cloud.v2.src.ingest_api import IngestAPI
from formant.sdk.cloud.v2.formant_ingest_api_client.models.ingestion_request import (
    IngestionRequest,
)
from formant.sdk.cloud.v2.src.query_api import QueryAPI
from formant.sdk.cloud.v2.formant_query_api_client.models.query import (
    Query,
    QueryTypesItem,
)

from formant.sdk.cloud.v2.formant_query_api_client.models.stream_data_points_item import (
    StreamDataPointsItem,
)
import dateutil.parser as parser
import os

DEFAULT_BASE_URL = "https://api.formant.io/v1"
DEFAULT_DEVICE_ID =  "404e2d2c-f95f-41d8-bce1-915e314a6898"

EMAIL = os.getenv("FORMANT_EMAIL")
PASSWORD = os.getenv("FORMANT_PASSWORD")
DEVICE_ID = os.getenv("DEVICE_ID", DEFAULT_DEVICE_ID)
BASE_URL = os.getenv("BASE_URL", DEFAULT_BASE_URL)

END_TIME_IS_NOW = os.getenv("END_TIME_IS_NOW", "true")

## PLEASE READ:
## There is no guarantee that the query will return any data, so the tests are designed to pass
## if the query returns 200 status code and the response does not contain any data, the test will print a warning

class TestQueries(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestQueries, self).__init__(*args, **kwargs)
        if not EMAIL or not PASSWORD:
            raise Exception("Please provide FORMANT_EMAIL and FORMANT_PASSWORD in environment variables")

        self.client = QueryAPI(email=EMAIL, password=PASSWORD, base_url=BASE_URL)
        self.ingestClient = IngestAPI(email=EMAIL, password=PASSWORD, base_url=BASE_URL)
        self.device_id = DEVICE_ID
        self.tags = {}

        if END_TIME_IS_NOW == "true":
            self.end = datetime.utcnow()
            self.start = self.end - timedelta(hours=2)
        else:
            self.start = parser.isoparse("2022-11-11T02:00:00.000Z")
            self.end = parser.isoparse("2022-12-11T02:02:00.000Z")

    def check_query_result(self, result, attribute):
        self.assertEqual(result.status_code, 200, f"expected 200, got {result.status_code}")
        if result.parsed.items:
            stream_data_points_item = result.parsed.items[0].points[0]

            self.assertIsInstance(
                stream_data_points_item,
                StreamDataPointsItem,
                "not an instance of StreamDataPointsItem",
            )

            self.assertIsNotNone(getattr(stream_data_points_item, attribute), f"{attribute} value is None")
        else:
            # it's ok for the list to be empty
            print(f"warning! got empty items list for {attribute}")
            self.assertEqual(result.parsed.items, [], "got empty items list")


    def test_query_numeric(self):
        types = [QueryTypesItem.NUMERIC]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'numeric')

    def test_query_text(self):
        types = [QueryTypesItem.TEXT]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'text')

    def test_query_bitset(self):
        types = [QueryTypesItem.BITSET]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'bitset')

    def test_query_localization(self):
        types = [QueryTypesItem.LOCALIZATION]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'localization')

    def test_query_point_cloud(self):
        types = [QueryTypesItem.POINT_CLOUD]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'point_cloud')

    def test_query_location(self):
        types = [QueryTypesItem.LOCATION]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'location')

    def test_query_file(self):
        start = parser.isoparse("2022-11-11T02:00:00.000Z")
        end = parser.isoparse("2022-12-11T02:02:00.000Z")

        types = [QueryTypesItem.FILE]
        query = Query(start=start, end=end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'file')

    def test_query_health(self):
        types = [QueryTypesItem.HEALTH]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'health')

    def test_query_transform_tree(self):
        types = [QueryTypesItem.TRANSFORM_TREE]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'transform_tree')

    def test_query_battery(self):
        types = [QueryTypesItem.BATTERY]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'battery')

    def test_query_video(self):
        types = [QueryTypesItem.VIDEO]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'video')

    def test_query_numeric_set(self):
        types = [QueryTypesItem.NUMERIC_SET]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'numeric_set')

    def test_query_json(self):
        types = [QueryTypesItem.JSON]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'json')

    def test_query_image(self):
        types = [QueryTypesItem.IMAGE]
        query = Query(start=self.start, end=self.end, types=types, next_="true")
        result = self.client.queries.query(query=query)

        self.check_query_result(result, 'image')


unittest.main()
