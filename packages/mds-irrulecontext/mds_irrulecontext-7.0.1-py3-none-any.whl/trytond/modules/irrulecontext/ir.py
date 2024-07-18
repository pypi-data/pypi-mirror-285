# -*- coding: utf-8 -*-
# This file is part of the irrulecontext-module from m-ds.de for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

from trytond.transaction import Transaction
from trytond.pool import PoolMeta, Pool


class Rule(metaclass=PoolMeta):
    __name__ = 'ir.rule'

    @classmethod
    def __setup__(cls):
        super(Rule, cls).__setup__()
        cls.domain.help += (
            '\n- "user_id" id from the current user')

    @classmethod
    def _context_modelnames(cls):
        """ list of models to add 'user_id' to context,
            list all model-names to which you want to
            add you context-values

        Returns:
            set: model-names
        """
        try:
            result = super(Rule, cls)._context_modelnames()
        except Exception:
            result = set()
        return result

    @classmethod
    def _get_context_values(cls, model_name):
        """ get dict to add values to context of
            ir.rule

        Args:
            model_name (str): model_name for which keys/values
                should be inserted into context

        Returns:
            dict: values will be inserted into context
        """
        return {}

    @classmethod
    def _get_context(cls, model_name):
        """ add values to ir.rule-context

        Args:
            model_name (str): model_name to fill
            context of ir.rule with self-defined
            values

        Returns:
            dict: context of ir.rule if a rule is examined
        """
        context = super()._get_context(model_name)

        if model_name in cls._context_modelnames():
            context['user_id'] = Transaction().user
            context.update(cls._get_context_values(model_name))
        return context

    @classmethod
    def _get_cache_key(cls, model_name):
        key = super()._get_cache_key(model_name)

        if model_name in cls._context_modelnames():
            key = (*key, Transaction().user)

            values = cls._get_context_values(model_name)
            for item in values.keys():
                key = (*key, values[item])
        return key

# end Rule


class RuleCompany(metaclass=PoolMeta):
    __name__ = 'ir.rule'

    @classmethod
    def __setup__(cls):
        super(Rule, cls).__setup__()
        cls.domain.help += (
            '\n- "company" company-id from the current user'
            '\n- "employee" employee-id from the current user')

    @classmethod
    def _get_context(cls, model_name):
        """ add company + employee to ir.rule-context

        Args:
            model_name (str): model_name to add company+employee

        Returns:
            dict: context of ir.rule if a rule is examined
        """
        ResUser = Pool().get('res.user')

        context = super()._get_context(model_name)

        if model_name in cls._context_modelnames():
            key_todo = {'company', 'employee'}.difference(set(context.keys()))
            if key_todo:
                user = ResUser(Transaction().user)

                if 'company' in key_todo:
                    context['company'] = getattr(user.company, 'id', None)
                if 'employee' in key_todo:
                    context['employee'] = getattr(user.employee, 'id', None)
        return context

    @classmethod
    def _get_cache_key(cls, model_name):
        """ generate cache-key
        """
        ResUser = Pool().get('res.user')

        key = super()._get_cache_key(model_name)

        if model_name in cls._context_modelnames():
            user = ResUser(Transaction().user)
            key = (*key, getattr(user.company, 'id', None))
            key = (*key, getattr(user.employee, 'id', None))
        return key

# end RuleCompany
