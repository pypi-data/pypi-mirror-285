# -*- coding: utf-8 -*-
# This file is part the pim-memos-module for Tryton from m-ds.de.
# The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from trytond.report.report import Report, FORMAT2EXT
from slugify import slugify
from string import Template
import tempfile
import os
import time
import subprocess
import logging
import json

logger = logging.getLogger(__name__)


class ReportOdt(Report):
    __name__ = 'pim_memos.reportodt'

    @classmethod
    def optimize_tags(cls, html, from_tag, to_tag, attrs):
        """ replace tag 'font'
            attrs: {
                'from_attr': {
                    'attrib': 'to_attr',
                    'from_value': 'to_value',
                    ...
                    },
                }
        """
        # replace all end-tags
        result = html.replace('</%s>' % from_tag, '</%s>' % to_tag)

        while True:
            pos1 = result.find('<%s' % from_tag)

            if pos1 == -1:
                break
            end_pos = result.find('>', pos1)
            if end_pos == -1:
                break

            # prepare attrib to read into dict by json
            st1 = result[pos1:end_pos + 1].replace(from_tag, to_tag)
            st2 = '{%s}' % st1[len(to_tag) + 1:-1].\
                replace('=', ':').\
                strip().\
                replace(' ', ',')

            reverse_key = {}
            for key in attrs.keys():
                st2 = st2.replace(key, '"%s"' % attrs[key]['attrib'])
                reverse_key[attrs[key]['attrib']] = key

            # build new style
            st3_dict = json.loads(st2)
            attr2 = ';'.join([
                '%(key)s:%(value)s' % {
                    'key': x,
                    'value': attrs.get(
                        reverse_key[x], {}).get(st3_dict[x], st3_dict[x]),
                    }
                for x in st3_dict.keys()
                ])

            # replace begin-tag and its atributes
            result = ''.join([
                    result[:pos1],
                    '<%s style="%s;">' % (to_tag, attr2),
                    result[end_pos + 1:]
                ])
        return result

    @classmethod
    def render(cls, report, report_context):
        """ replace genshi-templating to optimize rich-text made html
        """
        record = report_context.get('record', None)
        if record:
            return Template(report.report_content.decode('utf8')).substitute({
                'title': record.name,
                'body': cls.optimize_tags(
                    record.memo2, 'font', 'span', {
                        'face': {
                            'attrib': 'font-family',
                            'normal': 'initial',
                            'sans': 'sans-serif',
                            'serif': 'serif',
                            'monospace': 'monospace'},
                        'color': {
                            'attrib': 'color'},
                        'size': {
                            'attrib': 'font-size',
                            '1': '5pt',
                            '2': '7pt',
                            '3': '9pt',
                            '4': '11pt',
                            '5': '13pt',
                            '6': '15pt',
                            '7': '17pt'},
                    }),
                }).encode('utf8')
        return b''

    @classmethod
    def convert(cls, report, data, timeout=5 * 60, retry=5):
        """ replace 'convert' because we add '--writer' to command line
            to create a writer-pdf (not a writer-web-pdf)
        """
        input_format = report.template_extension
        output_format = report.extension or report.template_extension

        dtemp = tempfile.mkdtemp(prefix='trytond_')
        path = os.path.join(
            dtemp, report.report_name + os.extsep + input_format)
        oext = FORMAT2EXT.get(output_format, output_format)
        mode = 'w+' if isinstance(data, str) else 'wb+'
        with open(path, mode) as fp:
            fp.write(data)
        try:
            cmd = [
                'soffice', '--writer',
                '--headless', '--nolockcheck', '--nodefault', '--norestore',
                '--convert-to', oext, '--outdir', dtemp, path]
            output = os.path.splitext(path)[0] + os.extsep + oext
            for count in range(retry, -1, -1):
                if count != retry:
                    time.sleep(0.02 * (retry - count))
                subprocess.check_call(cmd, timeout=timeout)
                if os.path.exists(output):
                    with open(output, 'rb') as fp:
                        return oext, fp.read()
            else:
                logger.error(
                    'fail to convert %s to %s', report.report_name, oext)
                return input_format, data
        finally:
            try:
                os.remove(path)
                os.remove(output)
                os.rmdir(dtemp)
            except OSError:
                pass

    @classmethod
    def execute(cls, ids, data):
        """ edit filename
        """
        pool = Pool()
        IrDate = pool.get('ir.date')
        Memo = pool.get('pim_memos.note')

        (ext1, cont1, dirprint, title) = super(
            ReportOdt, cls).execute(ids, data)

        return (
            ext1,
            cont1,
            dirprint,
            slugify('%(date)s-note-%(descr)s' % {
                'date': IrDate.today().isoformat().replace('-', ''),
                'descr': Memo(data['id']).rec_name[:50],
                },
                max_length=100, word_boundary=True, save_order=True),
            )

# ende ReportOdt
