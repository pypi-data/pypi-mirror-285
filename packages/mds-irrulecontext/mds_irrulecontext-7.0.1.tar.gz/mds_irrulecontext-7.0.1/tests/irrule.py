# -*- coding: utf-8 -*-
# This file is part of the irrulecontext-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.tests.test_tryton import with_transaction
from trytond.pool import Pool
from trytond.transaction import Transaction
from trytond.modules.company.tests.test_module import (
    create_company, create_employee, set_company)


class IrRuleTestCase(object):
    """ test context ir-rule
    """
    @with_transaction()
    def test_irrule_context_no_company(self):
        """ call _get_context() and _get_cache_key(), check result
        """
        pool = Pool()
        ResUser = pool.get('res.user')
        IrRule = pool.get('ir.rule')

        user = ResUser(Transaction().user)
        self.assertEqual(
            IrRule._get_context('model2_test'),
            {'groups': (1, 2, 3, 4, 5), 'companies': (), 'user_id': user.id,
             'key1': 'value1', 'company': None, 'employee': None})

        self.assertEqual(
            IrRule._get_context('model3_test'),
            {'groups': (1, 2, 3, 4, 5), 'companies': (), 'user_id': user.id,
             'key2': 'value2', 'company': None, 'employee': None})

        self.assertEqual(
            IrRule._get_context('model_not_defined'),
            {'groups': (1, 2, 3, 4, 5), 'companies': ()})

        self.assertEqual(
            IrRule._get_cache_key('model2_test'),
            (None, (1, 2, 3, 4, 5), (), user.id, 'value1', None, None))

        self.assertEqual(
            IrRule._get_cache_key('model3_test'),
            (None, (1, 2, 3, 4, 5), (), user.id, 'value2', None, None))

        self.assertEqual(
            IrRule._get_cache_key('model_not_defined'),
            (None, (1, 2, 3, 4, 5), ()))

    @with_transaction()
    def test_irrule_context_with_company(self):
        """ add company + employee,
            call _get_context() and _get_cache_key(), check result
        """
        pool = Pool()
        IrRule = pool.get('ir.rule')
        ResUser = pool.get('res.user')

        company = create_company()
        with set_company(company):
            employee = create_employee(company)
            user = ResUser(Transaction().user)
            ResUser.write(*[
                [user], {
                    'employee': employee.id,
                    'employees': [('add', [employee.id])]
                }])

            self.assertEqual(
                IrRule._get_context('model2_test'),
                {'groups': (1, 2, 3, 4, 5), 'companies': (company.id,),
                    'user_id': user.id, 'key1': 'value1',
                    'company': company.id, 'employee': employee.id})

            self.assertEqual(
                IrRule._get_context('model3_test'),
                {'groups': (1, 2, 3, 4, 5), 'companies': (company.id,),
                    'user_id': user.id, 'key2': 'value2',
                    'company': company.id, 'employee': employee.id})

            self.assertEqual(
                IrRule._get_context('model_not_defined'),
                {'groups': (1, 2, 3, 4, 5), 'companies': (company.id,)})

            self.assertEqual(
                IrRule._get_cache_key('model2_test'),
                (None, (1, 2, 3, 4, 5), (company.id,), user.id,
                    'value1', company.id, employee.id))
            self.assertEqual(
                IrRule._get_cache_key('model3_test'),
                (None, (1, 2, 3, 4, 5), (company.id,), user.id,
                    'value2', company.id, employee.id))
            self.assertEqual(
                IrRule._get_cache_key('model_not_defined'),
                (None, (1, 2, 3, 4, 5), (company.id,)))

# end IrRuleTestCase
