# -*- coding: utf-8 -*-
# This file is part the pim-memos-module for Tryton from m-ds.de.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.exceptions import UserError


class PimMemoTestCase(ModuleTestCase):
    'Test memo module'
    module = 'pim_memos'

    @with_transaction()
    def test_pimmemo_create_item(self):
        """ create memo
        """
        pool = Pool()
        PimMemo = pool.get('pim_memos.note')

        m1, = PimMemo.create([{
            'name': 'name 1',
            'memo2': 'text 1',
            }])

        m_lst = PimMemo.search([])
        self.assertEqual(len(m_lst), 1)
        self.assertEqual(m_lst[0].memo2, 'text 1')
        self.assertEqual(m_lst[0].name, 'name 1')
        self.assertEqual(m_lst[0].rec_name, 'name 1: text 1')
        self.assertEqual(m_lst[0].memoshort, 'text 1')

        m2_lst = PimMemo.search([('memo2', '=', 'text 1')])
        self.assertEqual(len(m2_lst), 1)
        m2_lst = PimMemo.search([('memo2', 'ilike', '%text%')])
        self.assertEqual(len(m2_lst), 1)

        m2_lst = PimMemo.search([('rec_name', '=', 'text 1')])
        self.assertEqual(len(m2_lst), 1)

        m2_lst = PimMemo.search([('memoshort', '=', 'text 1')])
        self.assertEqual(len(m2_lst), 1)
        m2_lst = PimMemo.search([('memoshort', 'ilike', '%text%')])
        self.assertEqual(len(m2_lst), 1)

    @with_transaction()
    def test_pimmemo_create_item_tree(self):
        """ create memo, add sub-items
        """
        pool = Pool()
        PimMemo = pool.get('pim_memos.note')

        PimMemo.create([{
            'name': 'name 1',
            'memo2': 'text 1',
            'childs': [('create', [{
                'name': 'name 2',
                'memo2': 'text 2',
                }])],
            }])

        m_lst = PimMemo.search([], order=[('memo2', 'ASC')])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 1')
        self.assertEqual(m_lst[0].parent, None)
        self.assertEqual(len(m_lst[0].childs), 1)
        self.assertEqual(m_lst[0].childs[0].rec_name, 'name 2: text 2')

        self.assertEqual(m_lst[1].memo2, 'text 2')
        self.assertEqual(m_lst[1].parent.rec_name, 'name 1: text 1')
        self.assertEqual(len(m_lst[1].childs), 0)

        # delete root item, should fail
        self.assertRaisesRegex(
            UserError,
            "The note 'name 1: text 1' has subnotes and therefore " +
            "can not be deleted.",
            PimMemo.delete,
            [m_lst[0]])

    @with_transaction()
    def test_pimmemo_create_item_check_sequence(self):
        """ create memo2, check sequence
        """
        pool = Pool()
        PimMemo = pool.get('pim_memos.note')

        PimMemo.create([{
                'name': 'name 1',
                'memo2': 'text 1',
                'sequence': 1,
            }, {
                'name': 'name 2',
                'memo2': 'text 2',
                'sequence': 2,
            }])

        # default-order is 'by sequence'
        m_lst = PimMemo.search([])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 1')
        self.assertEqual(m_lst[1].memo2, 'text 2')

        PimMemo.write(*[
            [m_lst[0]],
            {
                'sequence': 3,
            }])

        m_lst = PimMemo.search([])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 2')
        self.assertEqual(m_lst[1].memo2, 'text 1')

        # order by memoshort
        m_lst = PimMemo.search([], order=[('memoshort', 'ASC')])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 1')
        self.assertEqual(m_lst[1].memo2, 'text 2')

        m_lst = PimMemo.search([], order=[('memoshort', 'DESC')])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 2')
        self.assertEqual(m_lst[1].memo2, 'text 1')

        # order by name
        m_lst = PimMemo.search([], order=[('name', 'ASC')])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 1')
        self.assertEqual(m_lst[1].memo2, 'text 2')

        m_lst = PimMemo.search([], order=[('name', 'DESC')])
        self.assertEqual(len(m_lst), 2)
        self.assertEqual(m_lst[0].memo2, 'text 2')
        self.assertEqual(m_lst[1].memo2, 'text 1')

    @with_transaction()
    def test_pimmemo_create_item_tree_with_recursion(self):
        """ create memo, add sub-items, add recursion
        """
        pool = Pool()
        PimMemo = pool.get('pim_memos.note')

        m1, = PimMemo.create([{
            'name': 'name 1',
            'memo2': 'text 1',
            'childs': [('create', [{
                'name': 'name 2',
                'memo2': 'text 2',
                }])],
            }])

        m_lst = PimMemo.search([], order=[('memo2', 'ASC')])
        self.assertEqual(len(m_lst), 2)

        self.assertRaisesRegex(
            UserError,
            'Recursion error: Record "name 1" with parent "name 1" was ' +
            'configured as ancestor of itself.',
            PimMemo.write,
            *[
                [m_lst[0]],
                {
                    'childs': [('add', [m_lst[0].id])],
                },
            ])

    @with_transaction()
    def test_pimmemo_create_item_with_category(self):
        """ create memo and category
        """
        pool = Pool()
        PimMemo = pool.get('pim_memos.note')
        PimCategory = pool.get('pim_memos.category')

        category, = PimCategory.create([{
            'name': 'cat 1',
            }])
        m1, = PimMemo.create([{
            'name': 'name 1',
            'memo2': 'text 1',
            'category': category.id,
            }])

        m_lst = PimMemo.search([])
        self.assertEqual(len(m_lst), 1)
        self.assertEqual(m_lst[0].memo2, 'text 1')
        self.assertEqual(m_lst[0].category.name, 'cat 1')

        c_lst = PimCategory.search([])
        self.assertEqual(len(c_lst), 1)

    @with_transaction()
    def test_pimmemo_create_category(self):
        """ create a category for memos
        """
        pool = Pool()
        PimCategory = pool.get('pim_memos.category')

        c1, = PimCategory.create([{
            'name': 'cat 1',
            }])

        c_lst = PimCategory.search([])
        self.assertEqual(len(c_lst), 1)

        c2_lst = PimCategory.search([('name', '=', 'cat 1')])
        self.assertEqual(len(c2_lst), 1)
        c2_lst = PimCategory.search([('name', 'ilike', '%cat%')])
        self.assertEqual(len(c2_lst), 1)

    @with_transaction()
    def test_pimmemo_create_category_tree(self):
        """ create a category for memos
        """
        pool = Pool()
        PimCategory = pool.get('pim_memos.category')

        c1, = PimCategory.create([{
            'name': 'cat 1',
            'childs': [('create', [{
                'name': 'cat 2',
                }])],
            }])

        c_lst = PimCategory.search([], order=[('name', 'ASC')])
        self.assertEqual(len(c_lst), 2)
        self.assertEqual(c_lst[0].name, 'cat 1')
        self.assertEqual(c_lst[0].parent, None)
        self.assertEqual(len(c_lst[0].childs), 1)
        self.assertEqual(c_lst[0].childs[0].name, 'cat 2')

        self.assertEqual(c_lst[1].name, 'cat 2')
        self.assertEqual(c_lst[1].parent.name, 'cat 1')
        self.assertEqual(len(c_lst[1].childs), 0)

        # delete root-category, should fail
        self.assertRaisesRegex(
            UserError,
            "The category 'cat 1' has subcategories and therefore " +
            "can not be deleted.",
            PimCategory.delete,
            [c1])

    @with_transaction()
    def test_pimmemo_report_optimize_tags(self):
        """ check replace of tags
        """
        MemoReport = Pool().get('pim_memos.reportodt', type='report')

        txt = '<div align="left"><font face="normal"><b>Lorem</b> ' + \
            '<u><i>ipsum</i> dolor</u> sit </font>' + \
            '<font face="sans" size="5">amet</font><font face="normal">,' +\
            ' </font><font face="serif">consectetur</font><font ' + \
            'face="normal"> </font><font face="monospace">adipisicing' + \
            '</font><font face="normal"> elit, </font></div><div ' + \
            'align="center"><font face="normal" size="6">sed</font>' + \
            '<font face="normal"> <font size="7">doeiusmod</font> ' + \
            '<font size="3">tempor</font> <font size="2">incididunt' + \
            '</font> ut labore </font></div><div><font face="normal">et ' + \
            'dolore magna aliqua.</font></div><div align="left">' + \
            '<font face="normal">Ut enimad <font color="#cc0000">minim' + \
            '</font> <b><font color="#204a87">veniam</font></b>, quis' + \
            ' nostrud exercitation ullamco laboris nisi utaliquip ex ea ' + \
            'commodo consequat. </font></div>'

        result = MemoReport.optimize_tags(txt, 'font', 'span', {
            'face': {
                'attrib': 'font-family',
                'normal': 'initial',
                'sans': 'sans-serif',
                'serif': 'serif',
                'monospace': 'monospace',
                },
            'color': {
                'attrib': 'color',
                },
            'size': {
                'attrib': 'font-size',
                '1': '70%',
                '2': '80%',
                '3': '90%',
                '4': '100%',
                '5': '110%',
                '6': '120%',
                '7': '130%',
                },
            })
        self.assertEqual(
            result,
            '<div align="left"><span ' +
            'style="font-family:initial;"><b>Lorem</b> <u><i>ipsum</i>' +
            ' dolor</u> sit </span><span style="font-family:sans-serif' +
            ';font-size:110%;">amet</span><span style="font-family:' +
            'initial;">, </span><span style="font-family:serif;">' +
            'consectetur</span><span style="font-family:initial;">' +
            ' </span><span style="font-family:monospace;">adipisicing' +
            '</span><span style="font-family:initial;"> elit, </span>' +
            '</div><div align="center"><span style="font-family:initial' +
            ';font-size:120%;">sed</span><span style="font-family:' +
            'initial;"> <span style="font-size:130%;">doeiusmod</span> ' +
            '<span style="font-size:90%;">tempor</span> <span style=' +
            '"font-size:80%;">incididunt</span> ut labore </span></div>' +
            '<div><span style="font-family:initial;">et dolore magna ' +
            'aliqua.</span></div><div align="left"><span style="' +
            'font-family:initial;">Ut enimad <span style="color:#cc0000;' +
            '">minim</span> <b><span style="color:#204a87;">veniam</span>' +
            '</b>, quis nostrud exercitation ullamco laboris nisi ' +
            'utaliquip ex ea commodo consequat. </span></div>')

# end PimMemoTestCase


del ModuleTestCase
