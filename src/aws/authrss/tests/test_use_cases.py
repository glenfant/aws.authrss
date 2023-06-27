from aws.authrss.testing import AWS_AUTHRSS_FUNCTIONAL_TESTING
from io import BytesIO
from lxml import etree
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser

import unittest


class TestUseCasesFunctionalTest(unittest.TestCase):
    layer = AWS_AUTHRSS_FUNCTIONAL_TESTING

    def anonymous_browser(self):
        """Browser of anonymous"""
        import transaction

        transaction.commit()
        browser = Browser(self.layer["app"])
        browser.handleErrors = False
        return browser

    def _auth_browser(self, login, password):
        """Browser of authenticated user
        :param login: A known user login
        :param password: The password for this user
        """
        browser = self.anonymous_browser()
        browser.addHeader(
            "Authorization",
            "Basic {}:{}".format(
                login,
                password,
            ),
        )

        return browser

    def manager_browser(self):
        """Browser with Manager authentication
        :return: Browser object with manager HTTP basic authentication header
        """
        return self._auth_browser(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def member_browser(self):
        """Browser with Member authentication
        :return: Browser object with member HTTP basic authentication header
        """
        return self._auth_browser(TEST_USER_NAME, TEST_USER_PASSWORD)

    def rss_feed_urls(self, feed):
        """URLs of an RSS feed
        :param feed: an RSS feed as XML string
        :return: sequence of tarrget URLs of the feed
        """
        namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "dc": "http://purl.org/dc/elements/1.1/",
            "syn": "http://purl.org/rss/1.0/modules/syndication/",
            "rss": "http://purl.org/rss/1.0/",
        }
        feed_file = BytesIO(feed)
        feed_tree = etree.parse(feed_file)
        return feed_tree.xpath(
            "//rss:items//rdf:li/@rdf:resource", namespaces=namespaces
        )

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.setUpContent()

    def tearDown(self):
        del self.portal["foo"]

    def setUpContent(self):
        mgr_browser = self.manager_browser()
        mgr_browser.open(self.portal.absolute_url() + "/++add++Folder")
        mgr_browser.getControl(name="form.widgets.IDublinCore.title").value = "Foo"
        mgr_browser.getControl(name="form.buttons.save").click()
        mgr_browser.getLink(id="workflow-transition-publish").click()

    def test_isSiteSyndicationAllowed(self):
        """Checking global syndication settings"""
        from Products.CMFCore.utils import getToolByName

        syntool = getToolByName(self.portal, "portal_syndication")
        self.assertTrue(syntool.isSiteSyndicationAllowed())

    def test_isProductInstalled(self):
        """Checking our component is installed"""
        from plone.base.utils import get_installer

        installer = get_installer(self.portal, self.request)
        self.assertTrue(installer.is_product_installed("aws.authrss"))

    def test_requiredActionsAreAvailable(self):
        """Checking the required actions are available"""
        from Products.CMFCore.utils import getToolByName

        portal_actions = getToolByName(self.portal, "portal_actions")
        self.assertIn("rss_token", portal_actions["user"].keys())
        self.assertIn("rss", portal_actions["document_actions"].keys())

    def test_use_cases(self):
        from plone.base.interfaces.syndication import IFeedSettings
        from zExceptions.unauthorized import Unauthorized

        setRoles(self.portal, TEST_USER_ID, ["Authenticated", "Member", "Reviewer"])
        portal_workflow = self.portal.portal_workflow

        mgr_browser = self.manager_browser()
        mgr_browser.open(f"{self.portal.absolute_url()}/syndication-controlpanel")
        mgr_browser.getControl(name="form.widgets.allowed:list").value = ["selected"]
        mgr_browser.getControl(name="form.widgets.default_enabled:list").value = [
            "selected"
        ]
        mgr_browser.getControl(
            name="form.widgets.show_syndication_button:list"
        ).value = ["selected"]
        submit = mgr_browser.getControl(name="form.buttons.save")
        submit.click()

        foo_folder_url = self.portal.foo.absolute_url()

        mgr_browser = self.manager_browser()
        mgr_browser.open(foo_folder_url)
        self.assertTrue(mgr_browser.url.endswith("/plone/foo"))
        mgr_browser.getLink("Syndication").click()
        mgr_browser.getControl(name="form.widgets.enabled:list").value = ["selected"]
        submit = mgr_browser.getControl(name="form.buttons.save")
        submit.click()

        feedsettings = IFeedSettings(self.portal.foo)
        self.assertTrue(feedsettings.enabled)

        # Because we don't have javascript enabled, we lost feed_types, configure it again
        feedsettings.feed_types = ("RSS",)

        # the anonymous should have the usual legacy RSS URL
        anon_browser = self.anonymous_browser()
        anon_browser.open(foo_folder_url)
        self.assertTrue(anon_browser.title.startswith("Foo"))

        anon_browser = self.anonymous_browser()
        anon_browser.open(foo_folder_url)
        tree = etree.HTML(anon_browser.contents)

        links = tree.xpath("//li[@id='document-action-rss']/a")
        self.assertEqual(1, len(links))
        anon_rss_url = links[0].attrib["href"]
        self.assertTrue(anon_rss_url.endswith("/plone/foo/RSS"))

        # An authenticated user could see the RSS link with his own private token
        member_browser = self.member_browser()
        member_browser.open(foo_folder_url)
        tree = etree.HTML(member_browser.contents)
        links = tree.xpath("//li[@id='document-action-rss']/a")
        self.assertEqual(1, len(links))
        member_rss_url = links[0].attrib["href"]
        self.assertIn("/plone/foo/AUTH-RSS?token=", member_rss_url)

        # Let's add some content
        # As the foo folder has no content, there's nothing to view in the RSS feeds,
        # either the anonymous one or the private RSS feed for the member.

        # Adding a public 'Title 1' document
        mgr_browser.open(f"{foo_folder_url}/++add++Document")
        mgr_browser.getControl(name="form.widgets.IDublinCore.title").value = "Title 1"
        mgr_browser.getControl(
            name="form.widgets.IDublinCore.description"
        ).value = "Description 1"
        mgr_browser.getControl(name="form.buttons.save").click()
        mgr_browser.getLink(id="workflow-transition-publish").click()

        title1_doc_url = self.portal.foo["title-1"].absolute_url()
        self.assertIn("title-1", self.portal.foo.keys())
        title1_doc = self.portal.foo["title-1"]

        # check as Manager
        setRoles(self.portal, TEST_USER_ID, ["Member", "Manager"])
        self.assertEqual(
            portal_workflow.getInfoFor(title1_doc, "review_state"), "published"
        )

        # switch back to Reviewer Role
        setRoles(self.portal, TEST_USER_ID, ["Member", "Reviewer"])

        # Adding a restricted 'Title 2' document
        # Same as above but users must be reviewers to see this one::

        mgr_browser.open(foo_folder_url + "/++add++Document")
        mgr_browser.getControl(name="form.widgets.IDublinCore.title").value = "Title 2"
        mgr_browser.getControl(
            name="form.widgets.IDublinCore.description"
        ).value = "Description 2"
        mgr_browser.getControl(name="form.buttons.save").click()
        mgr_browser.getLink(id="workflow-transition-submit").click()

        title2_doc_url = self.portal.foo["title-2"].absolute_url()
        self.assertIn("title-2", self.portal.foo.keys())
        title2_doc = self.portal.foo["title-2"]

        # check as Manager
        setRoles(self.portal, TEST_USER_ID, ["Member", "Manager"])
        self.assertEqual(
            portal_workflow.getInfoFor(title2_doc, "review_state"), "pending"
        )

        # switch back to Reviewer Role
        setRoles(self.portal, TEST_USER_ID, ["Member", "Reviewer"])

        # The anonymous may see the 'Title 1' document
        anon_browser.open(title1_doc_url)
        self.assertEqual(title1_doc_url, anon_browser.url)

        with self.assertRaises(Unauthorized):
            anon_browser.open(title2_doc_url)

        # The member may see both documents
        member_browser.open(title1_doc_url)
        self.assertEqual(title1_doc_url, member_browser.url)

        member_browser.open(title2_doc_url)
        self.assertEqual(title2_doc_url, member_browser.url)

        # Viewing the RSS feed of the Foo folder
        # Okay, we are now testing the main feature of this component and show that when
        # viewing a private feed as anonymous, this feed shows also the elements the
        # authenticated member is allowed to view

        anon_browser.open(member_rss_url)
        feed = anon_browser.contents
        feed_urls = self.rss_feed_urls(feed)

        self.assertListEqual(
            [
                f"{self.portal.absolute_url()}/foo/title-1",
                f"{self.portal.absolute_url()}/foo/title-2",
            ],
            feed_urls,
        )

        # But he cannot view the last URL of the feed
        with self.assertRaises(Unauthorized):
            anon_browser.open(feed_urls[-1])

        # Checking the syndication of a Topic / Collection

        # This works for a topic too. Let's make a topic for which these two documents
        # match, without workflow state criterion.

        # Creating the topic
        # We create a topic named 'foo-topic' and publish it.

        mgr_browser.open(f"{self.portal.absolute_url()}/++add++Collection")
        mgr_browser.getControl(
            name="form.widgets.IDublinCore.title"
        ).value = "Foo Topic"
        mgr_browser.getControl(name="form.buttons.save").click()
        mgr_browser.getLink(id="workflow-transition-publish").click()

        foo_topic_url = self.portal["foo-topic"].absolute_url()
        self.assertEqual(f"{self.portal.absolute_url()}/foo-topic", foo_topic_url)

        # We set this topic's criteria such both above created documents appear in it.
        # Note that I do this with the API and not with the browser (too noisy)

        topic = self.portal["foo-topic"]
        self.portal["foo-topic"].setQuery(
            [
                {
                    "i": "portal_type",
                    "o": "plone.app.querystring.operation.string.is",
                    "v": "Document",
                }
            ]
        )

        mgr_browser = self.manager_browser()
        mgr_browser.open(foo_topic_url)
        mgr_browser.getLink("Syndication").click()
        mgr_browser.getControl(name="form.widgets.enabled:list").value = ["selected"]
        submit = mgr_browser.getControl(name="form.buttons.save")
        submit.click()

        feedsettings = IFeedSettings(topic)
        self.assertTrue(feedsettings.enabled)

        # Because we don't have javascript enabled, we lost feed_types, configure it again
        feedsettings.feed_types = ("RSS",)

        # Viewing the Topic
        # We can now view that topic as Member

        member_browser.open(foo_topic_url)
        self.assertIn("Title 1", member_browser.contents)
        self.assertIn("Title 2", member_browser.contents)

        # This topic is also viewable by the anonymous user, but he should not see the
        # 'Title 2' document that's in "pending" workflow status
        anon_browser.open(foo_topic_url)
        self.assertIn("Title 1", anon_browser.contents)
        self.assertNotIn("Title 2", anon_browser.contents)

        # Checking the topic syndication link

        # For the anonymous user

        tree = etree.HTML(anon_browser.contents)
        links = tree.xpath("//li[@id='document-action-rss']/a")
        self.assertEqual(len(links), 1)

        anon_rss_url = links[0].attrib["href"]
        self.assertTrue(
            anon_rss_url.startswith(f"{self.portal.absolute_url()}/foo-topic/RSS")
        )

        # For the member::
        tree = etree.HTML(member_browser.contents)
        links = tree.xpath("//li[@id='document-action-rss']/a")
        self.assertEqual(len(links), 1)

        member_rss_url = links[0].attrib["href"]
        self.assertTrue(
            member_rss_url.startswith(
                f"{self.portal.absolute_url()}/foo-topic/AUTH-RSS?token="
            )
        )

        # Resetting the personal token

        # Checking the action link to the personal token
        # The anonymous cannot reset his token
        # Anyway, even if the anonymous knows the URL, he cannot go there::
        with self.assertRaises(Unauthorized):
            anon_browser.open(f"{self.portal.absolute_url()}/@@personal-rss-token")

        # When the member has this link in his personal actions
        member_browser.open(self.portal.absolute_url())
        link = member_browser.getLink("RSS Token")
        self.assertEqual(link.url, f"{self.portal.absolute_url()}/@@personal-rss-token")
