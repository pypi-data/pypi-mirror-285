mds-irrulecontext
=================
Tryton module to add values to context of ir.rule.

Install
=======

pip install mds-irrulecontext

How To
======

Add your ``model_names`` using *_context_modelnames()*, the module will then add the
value ``user_id`` to the context of ir.rule. If *company* is installed, the ``ID`` of
``company`` and ``employee`` will be in the context. Use *_get_context_values()* to
add additional values to context of ir.rule::

    class IrRule(metaclass=PoolMeta):
        __name__ = 'ir.rule'

        @classmethod
        def _context_modelnames(cls):
            """ add model_name to context
            """
            result = super(IrRule, cls)._context_modelnames()
            result |= {'modelname1', 'modelname2'}
            return result

        @classmethod
        def _get_context_values(cls, model_name):
            """ add values to context
            """
            result = super(IrRule, cls)._get_context_values(model_name)

            if model_name == 'modelname1':
                result['key1'] = 'value1'
            elif model_name == 'modelname2':
                result['key2'] = 'value2'
            return result


Requires
========
- Tryton 7.0


Changes
=======

*7.0.1 - 05.07.2024*

- works
