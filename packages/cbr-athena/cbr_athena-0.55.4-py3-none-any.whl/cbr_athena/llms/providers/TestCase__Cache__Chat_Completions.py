from unittest import TestCase

from dotenv import load_dotenv

from cbr_athena.llms.providers.Cache__Chat_Completions import Cache__Chat_Completions


class TestCase__Cache__Chat_Completions(TestCase):
    cache : Cache__Chat_Completions

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.cache = Cache__Chat_Completions()
        cls.cache.patch_apply()

    @classmethod
    def tearDownClass(cls):
        cls.cache.patch_restore()