# -*- coding: utf-8 -*-
# This file is part of the irrulecontext-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.


import unittest
from trytond.tests.test_tryton import activate_module, drop_db
from .irrule import IrRuleTestCase
from . import addonvalues


class RuleTestCase(IrRuleTestCase, unittest.TestCase):
    'Test rule module'
    module = 'irrulecontext'

    @classmethod
    def setUpClass(cls):
        """ register
        """
        drop_db()
        addonvalues.register('irrulecontext')
        activate_module(['ir', 'res', 'company', 'irrulecontext'], 'en')
        super(RuleTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(RuleTestCase, cls).tearDownClass()
        drop_db()

# end RuleTestCase
