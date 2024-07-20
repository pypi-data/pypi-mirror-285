import logging
from time import sleep

from chaiverse.http_client import DataClient


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PreferenceDataSet:
    submission_id: str
    name: str

    def __init__(self, submission_id):
        self.submission_id = submission_id

    @classmethod
    def from_submission_id(cls, submission_id):
        return cls(submission_id)

    def generate(self, limit=5000):
        client = DataClient()
        params = dict(limit=limit)
        self.name = client.post(f'/v1/big_data/submission_preferences/{self.submission_id}', params=params)
        return self

    def _load(self):
        assert self.name, 'Please call generate() to submit the request'
        client = DataClient()
        result = client.get(f'/v1/big_data/get_output/{self.name}')
        return result

    def get_download_link(self):
        while True:
            result = self._load()
            url = result.get('url')
            if url:
                break
            print('Waiting for dataset to be generated...')
            sleep(5)
        return url
