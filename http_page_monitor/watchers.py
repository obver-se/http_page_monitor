""" This file allows the user to monitor pages for changes"""
from datetime import datetime, timedelta
from threading import Thread, Event, Lock
from random import normalvariate
# from subprocess import run
import logging
import requests
# import page_comparators


class PageWatcher (Thread):
    """ Watches a single page for changes """
    def __init__(self, url, time_interval=120, 
    	         comparison_function=None,
                 ignore_errors=True,
                 alert_function=logging.info):

        super().__init__()
        self.url = url

        # A function to compare the content of two requests
        self.compare_content = comparison_function
        self.frequency = time_interval
        self.last_request = None

        # Set the time until next run to 0 to start
        self.reset_next_run_time()

        # Determine how to handle network errors
        self.ignore_errors = ignore_errors

        # Keep track of if we should be running as a thread
        self.running = False
        self.stop_alert = Event()

        # By default the alert function will just be a logger
        self.alert_function = alert_function

    def run(self):
        """ Start this page watcher """
        # Print out the initial value of what is being
        # observed by comparing it to an empty document
        self.last_request = self.request_page()
        if self.compare_content is not None:
            logging.info("===========================\n"
                         "URL: %s\nIntial comparison:\n%s\n"
                         "===========================\n",
                         self.url,
                         self.compare_content(b"", self.last_request.content))
        else:
            logging.info("===========================\n"
                         "URL: %s\nIntial comparison:\n%s\n"
                         "===========================\n",
                         self.url,
                         self.last_request.content)

        self.running = True
        while self.running:
            # If there is time to wait then wait and then execute
            if self.current_sleep_time() > 0:
                self.stop_alert.wait(timeout=self.current_sleep_time())

            # If the reason we exited the wait was because we stopped then stop
            if self.stop_alert.isSet():
                self.stop_alert.clear()
                break

            result = self.check_for_change()
            self.reset_next_run_time()
            if result is not None:
                self.alert_function(self.url, result)

    def stop(self):
        """ Stop this page watcher """
        self.running = False
        self.stop_alert.set()

    def check_for_change(self):
        """ Fetch the page and compare it to
            the last time this page was fetched """
        request = self.request_page()
        diffs = self.compare_to_new_request(request)
        self.last_request = request
        return diffs

    def reset_next_run_time(self):
        """ Reset the next request to be based on
            the frequency plus some randomness """
        self.time_of_next_run =\
            datetime.now() +\
            timedelta(0, self.frequency + normalvariate(0, self.frequency / 4))

    def request_page(self):
        """ Request the page that we are
            pointed to and return the data """
        logging.debug('Requesting %s', self.url)
        try:
            return requests.get(self.url,
                                headers={'User-agent':
                                         'page_monitor'})
        except ConnectionError:
            logging.info('Error while trying to request: %s', self.url)
            if not self.ignore_errors:
                self.alert_function("Error while trying to access page")
            # Return an exact copy of the last time so that this is ignored
            return self.last_request

    def compare_to_new_request(self, new_request_data):
        """ Compare the new request data to the
            request that was previously made """
        # If we don't have a custom comparison function then just
        # check if the content is equal
        if self.compare_content is None:
            if new_request_data.content == self.last_request.content:
                return None
            return "The requests are different"

        return self.compare_content(self.last_request.content,
                                    new_request_data.content)

    def current_sleep_time(self, current_time=None):
        """ Returns the number of seconds until the request should be resent"""
        current_time = datetime.now()
        return (self.time_of_next_run - current_time).total_seconds()


class WatcherManager:
    """ Manages the running of several PageWatchers """
    def __init__(self, page_watchers, alert_function=logging.info):
        if page_watchers is None:
            self.watchers = []
        else:
            self.watchers = page_watchers

        self.alert = alert_function
        self.alert_method_sync = Lock()
        self.running = False

    def add_page(self, page_watcher):
        """ Add a page to be watched"""
        self.watchers.add(page_watcher)

    def start(self):
        """ Start all the page watchers """
        self.running = True
        for watcher in self.watchers:
            watcher.alert_function = self.alert_wrapper
            watcher.start()

    def alert_wrapper(self, url, data):
        """ Wraps the alert function so that is only called
            once even though multiple threads are using it """
        self.alert_method_sync.acquire()
        self.alert(url, data)
        self.alert_method_sync.release()

    def stop(self):
        """ Stop all the page watchers """
        self.running = False
        for watcher in self.watchers:
            watcher.stop()


# logging.basicConfig(level=logging.INFO)

