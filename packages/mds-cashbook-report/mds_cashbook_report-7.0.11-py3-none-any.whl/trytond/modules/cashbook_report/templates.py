# -*- coding: utf-8 -*-
# This file is part of the cashbook-module from m-ds for Tryton.
# The COPYRIGHT file at the top level of this repository contains the
# full copyright notices and license terms.

cashbook_types = [
    'cashbooks', 'cashbooks_gldiff', 'cashbooks_glperc',
    'cashbooks_glvalue', 'cashbooks_glyield']
category_types = [
    'categories', 'categories_gldiff', 'categories_glvalue',
    'categories_glperc', 'categories_glyield']
booktype_types = [
    'types', 'types_gldiff', 'types_glvalue',
    'types_glperc', 'types_glyield']
currency_types = ['currencies']

template_view_line = '<field name="%(fname)s" fill="%(fill)s" ' + \
    'empty="0" string="%(string)s"/>'

template_view_graph = """<?xml version="1.0"?>
<graph type="%(type)s" legend="%(legend)s" %(colscheme)s %(bgcol)s>
    <x>
        <field name="name"/>
    </x>
    <y>
        %(lines)s
    </y>
</graph>
"""
