# -*- coding: utf-8 -*-
# This file is part of the routeapi-module for Tryton from m-ds.de.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool, PoolMeta


class IrRule(metaclass=PoolMeta):
    __name__ = 'ir.rule'

    @classmethod
    def _context_modelnames(cls):
        """ add test-model_name to context
        """
        result = super(IrRule, cls)._context_modelnames()
        result |= {'model2_test', 'model3_test'}
        return result

    @classmethod
    def _get_context_values(cls, model_name):
        """ add values to context
        """
        result = super(IrRule, cls)._get_context_values(model_name)

        if model_name == 'model2_test':
            result['key1'] = 'value1'
        elif model_name == 'model3_test':
            result['key2'] = 'value2'
        return result

# end IrRule


def register(module):
    Pool.register(
        IrRule,
        module=module, type_='model')
