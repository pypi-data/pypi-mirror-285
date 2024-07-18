# -*- coding: utf-8 -*-
# This file is part the pim-memos-module for Tryton from m-ds.de.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.model import ModelView, ModelSQL, fields, tree, Index
from sql import Null
from sql.conditionals import Case
from sql.functions import DateTrunc, Function
from trytond.transaction import Transaction
import html2text
from trytond.exceptions import UserError
from trytond.i18n import gettext


class Concat2(Function):
    """ concat columns
    """
    __slots__ = ()
    _function = 'concat'

# end Concat2


class Replace(Function):
    """ replace substrings
    """
    __slots__ = ()
    _function = 'replace'

# end Replace


class PimMemo(tree(separator=' / '), ModelSQL, ModelView):
    "Note"
    __name__ = "pim_memos.note"

    name = fields.Char(
        string='Title', required=True, help='Title for the note')
    memo2 = fields.Text(string='Note', required=True)    # richtext
    memoshort = fields.Function(fields.Text(
        string='Memo', readonly=True),
        'on_change_with_memoshort', searcher='search_memoshort')
    category = fields.Many2One(
        model_name='pim_memos.category', string='Category',
        ondelete='RESTRICT')
    sequence = fields.Integer(string='Sequence')

    # hierarchy
    parent = fields.Many2One(model_name='pim_memos.note', string='Parent')
    childs = fields.One2Many(
        model_name='pim_memos.note', field='parent', string='Children')

    # info
    datecreated = fields.Function(fields.Date(
        string='created', readonly=True),
        'get_info', searcher='search_datecreated')
    datechanged = fields.Function(fields.Date(
        string='changed', readonly=True),
        'get_info', searcher='search_datechanged')

    @classmethod
    def __register__(cls, module_name):
        super(PimMemo, cls).__register__(module_name)
        cls.migrate_name_title(module_name)

    @classmethod
    def __setup__(cls):
        super(PimMemo, cls).__setup__()
        cls._order.insert(0, ('sequence', 'ASC'))
        t = cls.__table__()
        cls._sql_indexes.update({
            Index(
                t,
                (t.sequence, Index.Range(order='ASC'))),
            Index(
                t,
                (t.memo2, Index.Similarity())),
            Index(
                t,
                (DateTrunc('day', t.create_date), Index.Range()),
                where=t.create_date != None),
            Index(
                t,
                (DateTrunc('day', t.write_date), Index.Range()),
                where=t.write_date != None),
            })

    @classmethod
    def migrate_name_title(cls, module_name):
        """ column 'title' --> 'name', memo --> memo2
        """
        table = cls.__table_handler__(module_name)
        cursor = Transaction().connection.cursor()
        tab_memo = cls.__table__()

        if table.column_exist('title'):
            query = tab_memo.update(
                    columns=[tab_memo.name, tab_memo.memo2],
                    values=[tab_memo.title, Concat2(
                        '<div>',
                        Replace(tab_memo.memo, '\n', '</div><div>'),
                        '</div>'
                    )],
                    where=(tab_memo.name == None) &
                    (tab_memo.memo2 == None),
                )
            cursor.execute(*query)
            table.drop_column('title')
            table.drop_column('memo')

    @classmethod
    def validate(cls, memos):
        super(PimMemo, cls).validate(memos)
        cls.check_recursion(memos)

    @staticmethod
    def order_sequence(tables):
        table, _ = tables[None]
        return [Case((table.sequence == Null, 0), else_=1), table.sequence]

    @staticmethod
    def order_memoshort(tables):
        table, _ = tables[None]
        return [table.memo2]

    @staticmethod
    def order_datecreated(tables):
        table, _ = tables[None]
        return [table.create_date]

    @staticmethod
    def order_datechanged(tables):
        table, _ = tables[None]
        return [table.write_date]

    def get_rec_name(self, name=None):
        """ generate record-name
        """

        return '%(title)s: %(text)s' % {
            'title': self.name,
            'text': (self.memoshort or ''),
            }

    @fields.depends('memo2')
    def on_change_with_memoshort(self, name=None):
        """ get short text, without html
        """
        if self.memo2:
            o1 = html2text.HTML2Text()
            o1.ignore_links = True
            o1.ignore_tables = True
            o1.bypass_tables = False
            o1.single_line_break = True
            o1.body_width = 0
            short_text = '; '.join(
                o1.handle(self.memo2 or '').strip().split('\n'))
            del o1
            return short_text[:100]

    @classmethod
    def search_memoshort(cls, name, clause):
        """ search in memo + title
        """
        return [
            'OR',
            ('name',) + tuple(clause[1:]),
            ('memo2',) + tuple(clause[1:])]

    @classmethod
    def get_info_sql(cls):
        """ sql-code for query of title
        """
        tab_memo = cls.__table__()

        qu1 = tab_memo.select(
            tab_memo.id.as_('id_memo'),
            DateTrunc('day', tab_memo.create_date).as_('created'),
            DateTrunc('day', tab_memo.write_date).as_('changed'))
        return qu1

    @classmethod
    def search_datecreated(cls, name, clause):
        """ search in created
        """
        tab_name = cls.get_info_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_name.select(
                tab_name.id_memo,
                where=Operator(tab_name.created, clause[2]))
        return [('id', 'in', qu1)]

    @classmethod
    def search_datechanged(cls, name, clause):
        """ search in changed
        """
        tab_name = cls.get_info_sql()
        Operator = fields.SQL_OPERATORS[clause[1]]

        qu1 = tab_name.select(
                tab_name.id_memo,
                where=Operator(tab_name.changed, clause[2]))
        return [('id', 'in', qu1)]

    @classmethod
    def search_rec_name(cls, name, clause):
        """ search in memo + title
        """
        return cls.search_memoshort(name, clause)

    @classmethod
    def get_info(cls, memos, names):
        """ get dates, name for memo, from title or content
        """
        cursor = Transaction().connection.cursor()
        tab_memo = cls.get_info_sql()
        result = {x: {y.id: None for y in memos} for x in names}

        # query
        qu1 = tab_memo.select(
                tab_memo.id_memo, tab_memo.created, tab_memo.changed,
                where=tab_memo.id_memo.in_([x.id for x in memos])
            )
        cursor.execute(*qu1)
        records = cursor.fetchall()

        for record in records:
            values = {
                'datecreated': record[1].date()
                if record[1] is not None else None,
                'datechanged': record[2].date()
                if record[2] is not None else None,
                }

            for name in names:
                result[name][record[0]] = values[name]
        return result

    @classmethod
    def delete(cls, records):
        """ deny delete if there are sub-records
        """
        for record in records:
            if len(record.childs) > 0:
                raise UserError(gettext(
                    'pim_memos.msg_memo_delete',
                    notename=record.rec_name))
        return super(PimMemo, cls).delete(records)

# ende PimMemo
