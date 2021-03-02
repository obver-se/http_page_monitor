""" Tests the PageWatcher class to ensure that
    requests are being made and compared properly """
import unittest
import time

from http_page_monitor.tests.logging_http_server\
    import setup_logging_server
from .. import watchers


class TestPageWatcher(unittest.TestCase):
    """ Tests the PageWatcher class """
    @classmethod
    def setUpClass(cls):
        cls.server = setup_logging_server()
        cls.server.handle_requests()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        """ Reset the log before each test """
        self.server.reset_log()

    def test_initial_request(self):
        """ Make sure that the initial request is made when the watcher is started """
        page_w = watchers.PageWatcher(self.server.generate_address('/'),
                                  comparison_function=lambda a, b: None)

        # Start and immediatly stop to trigger a single request
        page_w.start()
        page_w.stop()

        # Allow the request to go through
        time.sleep(1)
        # Assert that there was an initial request
        self.assertEqual(self.server.request_count, 1)

    def test_single_request(self):
        """ Test to ensure a second request is made after the initial request """
        page_w = watchers.PageWatcher(self.server.generate_address('/'),
                                  time_interval=0.5)

        # Give the page watcher time to make a second request
        page_w.start()
        time.sleep(0.75)
        page_w.stop()

        # Assert that there was an initial request and a second request
        self.assertEqual(self.server.request_count, 2)

    def test_equal_pages_difference(self):
        """ Test how the watcher responds to a page that doesn't
            change with the default comparison function """
        alerts = []
        def dummy_alert_function(url, info):
            alerts.append((url, info))

        page_w = watchers.PageWatcher(self.server.generate_address('/'),
                                  time_interval=0.5,
                                  alert_function=dummy_alert_function)

        # Give the page watcher time to make a second request
        page_w.start()
        time.sleep(0.75)
        page_w.stop()

        # Assert that there was an initial request and a second request
        self.assertEqual(self.server.request_count, 2)

        # Assert that an alert wasn't made
        self.assertEqual(len(alerts), 0)

    def test_page_difference(self):
        """ Test how the watcher responds to a page 
            difference with the default comparison function """
        alerts = []
        def dummy_alert_function(url, info):
            alerts.append((url, info))

        page_w = watchers.PageWatcher(self.server.generate_address('/every2'),
                                  time_interval=0.5,
                                  alert_function=dummy_alert_function)

        # Give the page watcher time to make a second request
        page_w.start()
        time.sleep(0.7)
        page_w.stop()

        # Assert that there was an initial request and a second request
        self.assertEqual(self.server.request_count, 2)

        # Assert that an alert was made
        self.assertEqual(len(alerts), 1)

    def test_custom_page_difference_function(self):
        """ Test how the watcher responds to a page 
            difference with the default comparison function """
        def custom_comparison_function(old, new):
            return "%s, %s there was a difference" %\
                (old.decode('UTF-8'), new.decode('UTF-8'))

        alerts = []
        def dummy_alert_function(url, info):
            alerts.append((url, info))

        page_w = watchers.PageWatcher(self.server.generate_address('/every2'),
                                  time_interval=0.5,
                                  alert_function=dummy_alert_function,
                                  comparison_function=custom_comparison_function)

        # Give the page watcher time to make a second request
        page_w.start()
        time.sleep(0.7)
        page_w.stop()

        # Assert that there was an initial request and a second request
        self.assertEqual(self.server.request_count, 2)

        # Assert that an alert was made
        self.assertEqual(len(alerts), 1)

        # Make sure that the message was passed down
        self.assertEqual(alerts[0][1], "Response 1, Response 2 there was a difference")

    def test_custom_page_difference_function_no_difference(self):
        """ Test how the watcher responds to a page 
            difference with the default comparison function """
        def custom_comparison_function(old, new):
            return None

        alerts = []
        def dummy_alert_function(url, info):
            alerts.append((url, info))

        page_w = watchers.PageWatcher(self.server.generate_address('/every2'),
                                  time_interval=0.5,
                                  alert_function=dummy_alert_function,
                                  comparison_function=custom_comparison_function)

        # Give the page watcher time to make a second request
        page_w.start()
        time.sleep(0.7)
        page_w.stop()

        # Assert that there was an initial request and a second request
        self.assertEqual(self.server.request_count, 2)

        # Assert that no alerts were made
        self.assertEqual(len(alerts), 0)
