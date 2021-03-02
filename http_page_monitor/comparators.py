""" Functions that generate comparitor functions that
    can be then used to compare the HTML of two pages"""
from bs4 import BeautifulSoup, NavigableString


def remove_whitespace(string):
    """ removes all white space from a string """
    return "".join(string.split())


def remove_text_from_soup(soup):
    """ removes all text from a soup element and its
        descendents.  modifies the soup that was passed in """

    string_elements = soup.find_all(string=True)
    for string in string_elements:
        string.replace_with("")


def remove_attributes_from_soup(soup):
    """ removes all text from a soup element and its
        descendents.  modifies the soup that was passed in """

    tags = soup.find_all()
    for tag in tags:
        tag.attrs.clear()


def html_text_comparison(selector=None, case_sensitive=True,
                    ignore_whitespace=False):

    """ This comparison function generator checks if
        the text of the selected elements have changed"""
    def generated_comparitor(old_html, new_html):
        old_soup = BeautifulSoup(old_html, features="html.parser")
        new_soup = BeautifulSoup(new_html, features="html.parser")
        if selector:
            old_soup = old_soup.select(selector)
            new_soup = new_soup.select(selector)

            old_text = [element.get_text() for element in old_soup]
            new_text = [element.get_text() for element in new_soup]
        else:
            old_text = [old_soup.get_text()]
            new_text = [new_soup.get_text()]

        compare_old_text = old_text[:]
        compare_new_text = new_text[:]

        if not case_sensitive:
            compare_old_text = map(str.lower, compare_old_text)
            compare_new_text = map(str.lower, compare_new_text)

        if ignore_whitespace:
            # Remove all the white space
            compare_old_text = \
                [remove_whitespace(text) for text in compare_old_text]
            compare_new_text = \
                [remove_whitespace(text) for text in compare_new_text]

        if len(old_text) != len(new_text):
            return "Number of selected elements"\
                   " is different from the last request:\n" +\
                   "\n".join(new_text)

        differences = []
        zip_comparison = zip(compare_old_text, compare_new_text,
                             old_text,         new_text)

        for old_compare, new_compare, old, new in zip_comparison:
            if old_compare != new_compare:
                differences.append("'{}' -> '{}'".format(old, new))

        if differences:
            return "Text differences found:\n" + "\n".join(differences)

        # Return None if no differences could be found
        return None

    return generated_comparitor


def html_tag_comparison(selector=None, ignore_attributes=False):
    """ This comparison function generator checks if
        the HTML of the selected elements have changed"""
    def generated_comparitor(old_html, new_html):
        old_soup = BeautifulSoup(old_html, features="html.parser")
        new_soup = BeautifulSoup(new_html, features="html.parser")
        if selector:
            old_html = old_soup.select(selector)
            new_html = new_soup.select(selector)
        else:
            old_html = [old_soup]
            new_html = [new_soup]

        for element in old_html:
            remove_text_from_soup(element)
        for element in new_html:
            remove_text_from_soup(element)

        if ignore_attributes:
            for element in old_html:
                remove_attributes_from_soup(element)
            for element in new_html:
                remove_attributes_from_soup(element)

        if len(old_html) != len(new_html):
            return "Number of selected elements"\
                    " is different from the last request.\nNew Elements:\n" +\
                    "\n".join([str(html) for html in new_html])

        differences = []
        zip_comparison = zip(old_html, new_html)

        for old, new in zip_comparison:
            if str(old) != str(new):
                differences.append("'{}' -> '{}'".format(old, new))

        if differences:
            return "HTML differences found:\n" + "\n".join(differences)

        # Return None if no differences could be found
        return None

    return generated_comparitor
