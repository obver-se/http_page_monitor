# http\_page\_watcher
**http\_page\_watcher** is a highpowered website monitor. It allows for several levels of granularity in the way that changes are found, reported and detected. By default you can just throw a url into the PageWatcher object and it will print whenever any change is detected to the url, but provide a comparison function and you can compare and precisely as a single html element.

## Usage

### Simply watch a single page

``` python
from http_page_watcher import PageWatcher

# Set up a PageWatcher for example.com
pw = PageWatcher("https://example.com")

# Start it up!
pw.start()
```

This example will have started a single PageWatcher element that checks for changes every 120 seconds by default.

### Control every facet

``` python
from http_page_watcher import PageWatcher

# A function that we will use to compare the old request data to the new request data
def compare_3rd_character(old, new):
	if old[2] != new[2]:
		return "The third character is different"
		
	# Return None when no changes are detected
	return None

# Set up a PageWatcher for example.com
pw = PageWatcher("https://example.com",
				time_interval=30, # Check every 30 seconds
				comparison_function=compare_3rd_character, # Compare the third character of this page
				alert_function=lamda url, alert: print(url + ", " + alert) # Use the stdout to for alerts
)

# Start it up!
pw.start()
```

### Use provided page comparison function generators

``` python
from http_page_watcher import PageWatcher
from http_page_watcher.comparators import html_text_comparison

# Use the function generator to make a comparison function that will check the h1 tag's text
generated_comparison_function = html_text_comparison(selector="h1")

# Set up a PageWatcher for example.com
pw = PageWatcher("https://example.com",
				comparison_function=generated_comparison_function
)

# Start it up!
pw.start()
```

This example will only check the text of the h1 elements on this page.

### Manage a bunch of page watchers

``` python
from http_page_watcher import PageWatcher, WatcherManager

page_watchers = []
page_watchers.append(PageWatcher("https://example.com"))
page_watchers.append(PageWatcher("https://example.com/1"))
page_watchers.append(PageWatcher("https://example.com/2"))
page_watchers.append(PageWatcher("https://example.com/3"))

wm = WatcherManager(page_watchers, 
				    alert_function=lambda url, alert: print(url + ", " + alert)
)

# Start all the watchers!
wm.start()
```

This example will start many PageWatchers all funneling their alerts into the single alert function which the manager makes thread safe.