# -*- coding: utf-8 -*-
# This file is part of the irrulecontext-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.pool import Pool
from .ir import Rule, RuleCompany


def register():
    Pool.register(
        Rule,
        module='irrulecontext', type_='model')
    Pool.register(
        RuleCompany,
        module='irrulecontext', type_='model', depends=['company'])
