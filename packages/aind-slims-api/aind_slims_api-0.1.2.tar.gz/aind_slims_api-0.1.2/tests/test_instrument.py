"""Tests methods in mouse module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.models.instrument import SlimsInstrument

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestInstrument(unittest.TestCase):
    """Tests top level methods in mouse module"""

    example_client: SlimsClient
    example_response: Record

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        cls.example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_response = [
            Record(json_entity=r, slims_api=cls.example_client.db.slims_api)
            for r in json.loads(
                (
                    RESOURCES_DIR / "example_fetch_instrument_response.json_entity.json"
                ).read_text()
            )
        ]

    @patch("slims.slims.Slims.fetch")
    def test_fetch_content_success(
        self,
        mock_fetch: MagicMock,
    ):
        """Test fetch_instrument_content when successful and multiple are
        returned from fetch
        """
        mock_fetch.return_value = self.example_response + self.example_response
        response = self.example_client.fetch_model(
            SlimsInstrument, name="323_EPHYS1_OPTO"
        )
        self.assertEqual(response.json_entity, self.example_response[0].json_entity)


if __name__ == "__main__":
    unittest.main()
