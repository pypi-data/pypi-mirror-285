"""Tests methods in mouse module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.models.mouse import SlimsMouseContent

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestMouse(unittest.TestCase):
    """Tests top level methods in mouse module"""

    example_client: SlimsClient
    example_fetch_mouse_response: list[Record]

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_client = example_client
        with open(RESOURCES_DIR / "example_fetch_mouse_response.json", "r") as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_mouse_response = response

    @patch("slims.slims.Slims.fetch")
    def test_fetch_mouse_content_success(self, mock_fetch: MagicMock):
        """Test fetch_mouse_content when successful"""
        mock_fetch.return_value = self.example_fetch_mouse_response
        mouse_details = self.example_client.fetch_model(
            SlimsMouseContent, barcode="123456"
        )
        self.assertEqual(
            self.example_fetch_mouse_response[0].json_entity, mouse_details.json_entity
        )


if __name__ == "__main__":
    unittest.main()
