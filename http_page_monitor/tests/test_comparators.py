""" Tests the comparators that are used to compare reponses """
import unittest
from bs4 import BeautifulSoup
from .. import comparators


def generate_page(title, body):
    """ Scaffolding for a basic html page """
    return "<html><head><title>{0}\
            </title></head>\
            <body>{0}{1}</body></html>".format(title, body)


class TestHelperFunctions(unittest.TestCase):
    """ Test some of the helper functions available to the comparators """
    def test_whitespace_removal(self):
        """ Test the whitespace removal function """
        self.assertEqual(
                comparators.remove_whitespace("\n 1 1 \n2 3\t \n"),
                "1123"
        )

    def test_remove_text_from_soup(self):
        """ Test to see if the text removal function works """
        page =\
            """
            <html><head><title>title</title></head>
                <body>some text
                    <b class=\"under\">some bold text</b>
                </body>
            </html>
            """

        page_just_tags =\
            """
            <html><head><title></title></head>
                <body>
                    <b class=\"under\"></b>
                </body>
            </html>
            """

        soup_page = BeautifulSoup(page, features="html.parser")
        comparators.remove_text_from_soup(soup_page)

        soup_page_just_tags = BeautifulSoup(page_just_tags,
                                            features="html.parser")
        comparators.remove_text_from_soup(soup_page_just_tags)

        self.assertEqual(
                soup_page.prettify(),
                soup_page_just_tags.prettify()
        )

    def test_remove_attributes_from_soup(self):
        """ Test if attributes are removed properly """
        page =\
            """
            <html><head><title>title</title></head>
                <body>some text
                    <b class=\"under\">some bold text</b>
                </body>
            </html>
            """

        page_no_attributes =\
            """
            <html><head><title>title</title></head>
                <body>some text
                    <b>some bold text</b>
                </body>
            </html>
            """

        soup_page = BeautifulSoup(page, features="html.parser")
        comparators.remove_attributes_from_soup(soup_page)
        soup_page_no_attributes = BeautifulSoup(page_no_attributes,
                                                features="html.parser")

        self.assertEqual(
                str(soup_page_no_attributes),
                str(soup_page)
        )


class TestTextComparisons(unittest.TestCase):
    """ Tests the text comparison function generator """
    def setUp(self):
        """ Create some pages we can compare against each other """
        page_body =\
            "<ol>\
                 <li>item1</li>\
                 <li>item2</li>\
             </ol>"
        self.page_base = generate_page("Test1", page_body)

        page_body = "<ol type=\"something\">\
                          <li>item1</li>\
                          <li>item2</li>\
                      </ol>"
        self.page_attribute = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>item3</li>\
                      </ol>"
        self.page_html_text_change = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>Item2</li>\
                      </ol>"
        self.page_capitalization_change = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>Item2</li>\
                          <li>item3</li>\
                      </ol>"
        self.page_extra_element = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>item 2</li>\
                      </ol>"
        self.page_extra_whitespace = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>Item 2</li>\
                      </ol>"
        self.page_whitespace_and_case_change =\
            generate_page("Test1", page_body)

    def test_defaults_equal_pages(self):
        """ Test the default options of the text comparitor """
        compare = comparators.html_text_comparison()
        self.assertEqual(compare(self.page_base, self.page_base), None)

    def test_defaults_capitalization(self):
        """ Test if capitalizaiton matters by default """
        compare = comparators.html_text_comparison()
        # Make sure we get some differences
        self.assertIn("Text differences found:\n",
                      compare(self.page_base, self.page_capitalization_change))

    def test_defaults_extra_element(self):
        """ Test with an extra element """
        compare = comparators.html_text_comparison()
        # Make sure we get some differences
        self.assertIn("Text differences found:\n",
                      compare(self.page_base, self.page_extra_element))

    def test_defaults_extra_whitespace(self):
        """ Test with an extra whitespace added """
        compare = comparators.html_text_comparison()
        # Make sure we get some differences
        self.assertIn("Text differences found:\n",
                      compare(self.page_base, self.page_extra_whitespace))

    def test_text_difference(self):
        """ Test with a changed character """
        compare = comparators.html_text_comparison()
        # Make sure we get some differences
        self.assertIn("Text differences found:\n",
                      compare(self.page_base, self.page_html_text_change))

    def test_select_multiple_elements_equal(self):
        """ Test by selecting all li inside the ol element """
        compare = comparators.html_text_comparison("ol > li")
        # Make sure we get none since they are the same
        self.assertEqual(compare(self.page_base, self.page_base), None)

    def test_select_multiple_elements_different(self):
        """ Test by selecting all li inside the ol element """
        compare = comparators.html_text_comparison("ol > li")
        # Make sure we get an error since they have different text
        self.assertIn("Text differences found:\n",
                      compare(self.page_base, self.page_html_text_change))
        # Make sure we get an error since they have different capitalizaiton
        self.assertIn("Text differences found:\n",
                      compare(self.page_base, self.page_capitalization_change))

    def test_select_multiple_elements_extra(self):
        """ Test by selecting all li inside the ol element """
        compare = comparators.html_text_comparison("ol > li")
        # Make sure we get none since they are the same
        self.assertIn("Number of selected elements"
                      " is different from the last request",
                      compare(self.page_base, self.page_extra_element))

    def test_ignore_whitespace_different(self):
        """ Test with an extra whitespace ignored but same """
        compare = comparators.html_text_comparison(ignore_whitespace=True)
        # Make sure we get some differences
        self.assertEqual(compare(self.page_base, self.page_extra_whitespace),
                         None)

    def test_attribute_ignore(self):
        """ Test to make sure params are ignored """
        compare = comparators.html_text_comparison()
        self.assertEqual(compare(self.page_base, self.page_attribute), None)

    def test_ignore_case_and_whitespace(self):
        """ Test to make sure both case and whitespace can be ignored """
        compare = comparators.html_text_comparison(case_sensitive=False,
                                                   ignore_whitespace=True)
        self.assertEqual(compare(self.page_base,
                                 self.page_whitespace_and_case_change), None)


class TestHTMLComparisons(unittest.TestCase):
    """ Tests the text comparison function generator """
    def setUp(self):
        """ Create some pages we can compare against each other """
        page_body = "<ol>\
                          <li>item1</li>\
                          <li>item2</li>\
                      </ol>"
        self.page_base = generate_page("Test1", page_body)

        page_body = "<ol type=\"something\">\
                          <li>item1</li>\
                          <li>item2</li>\
                      </ol>"
        self.page_attribute = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>item3</li>\
                      </ol>"
        self.page_html_text_change = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>Item2</li>\
                      </ol>"
        self.page_capitalization_change = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>Item2</li>\
                          <li>item3</li>\
                      </ol>"
        self.page_extra_element = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>item 2</li>\
                      </ol>"
        self.page_extra_whitespace = generate_page("Test1", page_body)

        page_body = "<ol>\
                          <li>item1</li>\
                          <li>Item 2</li>\
                      </ol>"
        self.page_whitespace_and_case_change =\
            generate_page("Test1", page_body)

    def test_defaults_equal_pages(self):
        """ Test the default options of the text comparitor """
        compare = comparators.html_tag_comparison()
        self.assertEqual(compare(self.page_base, self.page_base), None)

    def test_defaults_extra_element(self):
        """ Test with an extra element """
        compare = comparators.html_tag_comparison()
        # Make sure we get some differences
        self.assertIn("HTML differences found:\n",
                      compare(self.page_base, self.page_extra_element))

    def test_defaults_extra_whitespace(self):
        """ Test with an extra whitespace added """
        compare = comparators.html_tag_comparison()
        # Make sure we get some differences
        self.assertEqual(compare(self.page_base, self.page_extra_whitespace),
                         None)

    def test_text_difference(self):
        """ Test with a changed character """
        compare = comparators.html_tag_comparison()
        # Make sure we get some differences
        self.assertEqual(compare(self.page_base, self.page_html_text_change), None)

    def test_select_multiple_elements_equal(self):
        """ Test by selecting all li inside the ol element """
        compare = comparators.html_tag_comparison("ol > li")
        # Make sure we get none since they are the same
        self.assertEqual(compare(self.page_base, self.page_base), None)

    def test_select_multiple_elements_extra(self):
        """ Test by selecting all li inside the ol element """
        compare = comparators.html_tag_comparison("ol > li")
        # Make sure we get none since they are the same
        self.assertIn("Number of selected elements"
                      " is different from the last request",
                      compare(self.page_base, self.page_extra_element))

    def test_attribute_different(self):
        """ Test with an html attribute being the difference"""
        compare = comparators.html_tag_comparison()
        # Make sure we get some differences
        self.assertIn("HTML differences found:\n",
                      compare(self.page_base, self.page_attribute))

    def test_attribute_different_ignore(self):
        """ Test with an html attribute being the difference"""
        compare = comparators.html_tag_comparison(ignore_attributes=True)
        # Make sure we get some differences
        self.assertEqual(compare(self.page_base, self.page_attribute), None)

    def test_ignore_case_and_whitespace(self):
        """ Test to make sure both case and whitespace can be ignored """
        compare = comparators.html_tag_comparison()
        self.assertEqual(compare(self.page_base,
                                 self.page_whitespace_and_case_change), None)
