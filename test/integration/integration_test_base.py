from abc import ABC
from os.path import join, dirname
from unittest import TestCase

from dotenv import load_dotenv


class IntegrationTestBase(ABC, TestCase):

    def setUp(self) -> None:
        load_dotenv(join(dirname(__file__), '.test.env'))
