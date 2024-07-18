# -*- coding: utf-8 -*-
# This file is part the pim-memos-module for Tryton from m-ds.de.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import PoolMeta


class Rule(metaclass=PoolMeta):
    __name__ = 'ir.rule'

    @classmethod
    def _context_modelnames(cls):
        """

        Returns:
            set: model-names
        """
        result = super(Rule, cls)._context_modelnames()
        return result | {
            'pim_memos.note',
            'pim_memos.category',
            }

# end Rule
