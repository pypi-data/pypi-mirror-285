"""Tests methods in user module"""

import json
import os
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from slims.internal import Record

from aind_slims_api.core import SlimsClient
from aind_slims_api.models.user import SlimsUser

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestUser(unittest.TestCase):
    """Tests top level methods in user module"""

    example_client: SlimsClient
    example_fetch_user_response: list[Record]

    @classmethod
    def setUpClass(cls):
        """Load json files of expected responses from slims"""
        example_client = SlimsClient(
            url="http://fake_url", username="user", password="pass"
        )
        cls.example_client = example_client
        with open(RESOURCES_DIR / "example_fetch_user_response.json", "r") as f:
            response = [
                Record(json_entity=r, slims_api=example_client.db.slims_api)
                for r in json.load(f)
            ]
        cls.example_fetch_user_response = response

    @patch("slims.slims.Slims.fetch")
    def test_fetch_user_content_success(self, mock_fetch: MagicMock):
        """Test fetch_user when successful"""
        mock_fetch.return_value = self.example_fetch_user_response
        user_info = self.example_client.fetch_model(SlimsUser, username="PersonA")
        self.assertEqual(
            self.example_fetch_user_response[0].json_entity,
            user_info.json_entity,
        )


if __name__ == "__main__":
    unittest.main()
