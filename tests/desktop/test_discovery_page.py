#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re
from itertools import cycle

import pytest
from unittestzero import Assert

from pages.desktop.discovery import DiscoveryPane
from pages.desktop.home import Home


class TestDiscoveryPane:

    # Need to get this info before run
    def basepath(self, mozwebqa):
        return '/en-US/firefox/discovery/pane/%s/Darwin' % mozwebqa.selenium.capabilities['version']

    @pytest.mark.nondestructive
    def test_that_users_with_less_than_3_addons_get_what_are_addons(self, mozwebqa):
        """
        Since Selenium starts with a clean profile all the time this will always have
        less than 3 addons.
        """
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        what_are_addons_expected = "Add-ons are applications that let you personalize "
        what_are_addons_expected += "Firefox with extra functionality or style. Try a time-saving"
        what_are_addons_expected += " sidebar, a weather notifier, or a themed look to make "
        what_are_addons_expected += "Firefox your own.\nLearn More"

        Assert.equal(what_are_addons_expected, discovery_pane.what_are_addons_text)

    @pytest.mark.nondestructive
    def test_that_mission_statement_is_on_addons_home_page(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        expected_text = "Thanks for using Firefox and supporting Mozilla's mission!"

        mission_text = discovery_pane.mission_section
        Assert.true(expected_text in mission_text)
        Assert.true(discovery_pane.mozilla_org_link_visible())
        download_count_regex = "Add-ons downloaded: (.+)"
        Assert.true(re.search(download_count_regex, discovery_pane.download_count) is not None)

    @pytest.mark.nondestructive
    def test_that_featured_themes_is_present_and_has_5_item(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        Assert.true(discovery_pane.is_themes_section_visible)
        Assert.equal(5, discovery_pane.themes_count)
        Assert.true(discovery_pane.is_themes_see_all_link_visible)

    @pytest.mark.native
    @pytest.mark.nondestructive
    def test_that_featured_themes_go_to_their_landing_page_when_clicked(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        first_theme = discovery_pane.first_theme
        theme = discovery_pane.click_on_first_theme()
        Assert.contains(first_theme, theme.theme_title)

    @pytest.mark.nondestructive
    def test_that_more_ways_to_customize_section_is_available(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        Assert.true(discovery_pane.more_ways_section_visible)
        Assert.equal("Browse all add-ons", discovery_pane.browse_all_addons)
        Assert.equal("See all complete themes", discovery_pane.see_all_complete_themes)

    @pytest.mark.nondestructive
    def test_that_up_and_coming_is_present_and_had_5_items(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        Assert.equal(5, discovery_pane.up_and_coming_item_count)

    @pytest.mark.nondestructive
    @pytest.mark.login
    def test_the_logout_link_for_logged_in_users(self, mozwebqa):
        home_page = Home(mozwebqa)
        home_page.login()
        Assert.true(home_page.is_the_current_page)
        Assert.true(home_page.header.is_user_logged_in)

        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        home_page = discovery_pane.click_logout()
        Assert.true(home_page.is_the_current_page)
        Assert.false(home_page.header.is_user_logged_in)

    @pytest.mark.smoke
    @pytest.mark.nondestructive
    def test_that_carousel_works(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))

        # ensure the first panel is visible
        current_panel = discovery_pane.carousel_panels[1]
        Assert.true(current_panel.is_visible)
        first_heading = current_panel.heading

        # switch to the second panel
        discovery_pane.show_next_carousel_panel()
        current_panel = discovery_pane.carousel_panels[2]
        Assert.not_equal(current_panel.heading, first_heading)
        Assert.true(current_panel.is_visible)

        # switch back to the first panel
        discovery_pane.show_previous_carousel_panel()
        current_panel = discovery_pane.carousel_panels[1]
        Assert.equal(current_panel.heading, first_heading)
        Assert.true(current_panel.is_visible)

    @pytest.mark.nondestructive
    def test_that_cycles_through_all_panels_in_the_carousel(self, mozwebqa):
        discovery_pane = DiscoveryPane(mozwebqa, self.basepath(mozwebqa))
        carousel_panels = discovery_pane.carousel_panels

        # remove first and last panels, they are phantoms!
        carousel_panels.pop(0)
        carousel_panels.pop(-1)
        panels_count = len(carousel_panels)

        # create and init cycle
        panels = cycle(carousel_panels)
        first_heading = panels.next().heading

        # advance forward, check that current panel is visible
        # to ensure that panels are being switched
        for i in range(panels_count):
            discovery_pane.show_next_carousel_panel()
            current_panel = panels.next()
            current_panel.wait_for_next_promo()
            Assert.true(current_panel.heading)
            Assert.true(current_panel.is_visible)

        # now check that current panel has the same heading as
        # the first one to ensure that we have completed the cycle
        last_heading = current_panel.heading
        Assert.equal(first_heading, last_heading)
