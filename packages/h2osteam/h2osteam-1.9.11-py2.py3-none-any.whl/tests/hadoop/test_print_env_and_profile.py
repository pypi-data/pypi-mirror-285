import h2osteam
import sys
import io
import re
from . import helper


class TestPrintProfile:
    _reg_out = None

    def setup_method(self, method):
        # Redirect stdout to allow saving print to string
        helper.connect_as_admin()
        TestPrintProfile._reg_out = sys.stdout

    def teardown_method(self, method):
        sys.stdout = TestPrintProfile._reg_out

    def test_print_all_profiles(self):
        connection = h2osteam.api()
        profiles = connection.get_profiles()
        sys.stdout = io.StringIO()
        h2osteam.print_profiles()
        printed = sys.stdout.getvalue()
        for profile in profiles:
            expected_regex = r'(\n|.)*Profile name: ' + profile['name'] + r'(\n|.)*'
            assert re.match(expected_regex, printed)
    # TODO: Flesh out this test class


class TestPrintPyEnv:
    _reg_out = None

    @classmethod
    def setup_class(cls):
        # Redirect stdout to allow saving print to string
        helper.connect_as_admin()
        TestPrintPyEnv._reg_out = sys.stdout

    @classmethod
    def teardown_class(cls):
        sys.stdout = TestPrintPyEnv._reg_out

    def test_print_all_py_envs(self):
        connection = h2osteam.api()
        envs = connection.get_python_environments()
        sys.stdout = io.StringIO()
        h2osteam.print_python_environments()
        printed = sys.stdout.getvalue()
        for env in envs:
            expected_regex = r'(\n|.)*Name: ' + env['name'] + r'(\n|.)*'
            assert re.match(expected_regex, printed)
    # TODO: Flesh out this test class


