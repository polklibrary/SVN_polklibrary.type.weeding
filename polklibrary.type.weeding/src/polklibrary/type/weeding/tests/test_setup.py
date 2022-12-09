# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from polklibrary.type.weeding.testing import POLKLIBRARY_TYPE_WEEDING_INTEGRATION_TESTING  # noqa: E501

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that polklibrary.type.weeding is properly installed."""

    layer = POLKLIBRARY_TYPE_WEEDING_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if polklibrary.type.weeding is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'polklibrary.type.weeding'))

    def test_browserlayer(self):
        """Test that IPolklibraryTypeWeedingLayer is registered."""
        from polklibrary.type.weeding.interfaces import (
            IPolklibraryTypeWeedingLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IPolklibraryTypeWeedingLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = POLKLIBRARY_TYPE_WEEDING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['polklibrary.type.weeding'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if polklibrary.type.weeding is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'polklibrary.type.weeding'))

    def test_browserlayer_removed(self):
        """Test that IPolklibraryTypeWeedingLayer is removed."""
        from polklibrary.type.weeding.interfaces import \
            IPolklibraryTypeWeedingLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IPolklibraryTypeWeedingLayer,
            utils.registered_layers())
