# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Modify by: Juan Carlos Hernandez Funes (juan@vauxoo.com)
############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import math
import openerp
from osv import osv, fields
from openerp import SUPERUSER_ID
import re
import tools
from tools.translate import _
import logging
import pooler
import pytz
from lxml import etree

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'street3': fields.char('Street3', size=128),
        'street4': fields.char('Street4', size=128),
        'city2': fields.char('City2', size=128),
    }
    
    def _get_address_field(self):
        res = super(res_partner, self)._get_address_field()
        res.extend(['street3','street4','city2'])
        return res
    
    def _get_default_country_id(self, cr, uid, context=None):
        country_obj = self.pool.get('res.country')
        #ids = country_obj.search(cr, uid, [ ( 'name', '=', 'México' ), ], limit=1)
        ids = country_obj.search(cr, uid, [ ( 'code', '=', 'MX' ), ], limit=1)
        id = ids and ids[0] or False
        return id

    def fields_view_get_address(self, cr, uid, arch, context={}):
        res = super(res_partner, self).fields_view_get_address(cr, uid, arch, context=context)
        user_obj = self.pool.get('res.users')
        fmt = user_obj.browse(cr, SUPERUSER_ID, uid, context).company_id.country_id
        fmt = fmt and fmt.address_format
        layouts = {
            '%(street3)s%(street4)s%(city2)s': """
                    <group>
                        <group>
                            <label for="type" attrs="{'invisible': [('parent_id','=', False)]}"/>
                            <div attrs="{'invisible': [('parent_id','=', False)]}" name="div_type">
                                <field class="oe_inline"
                                    name="type"/>
                                <label for="use_parent_address" class="oe_edit_only"/>
                                <field name="use_parent_address" class="oe_edit_only oe_inline"
                                    on_change="onchange_address(use_parent_address, parent_id)"/>
                            </div>

                            <label for="street" string="Address"/>
                            <div>
                                <field name="street" placeholder="Street..."/>
                                <field name="street2"/>
                                <field name="street3" placeholder="Street3..."/>
                                <field name="street4" placeholder="Street4..."/>
                                <div class="address_format">
                                    <field name="city" placeholder="City" style="width: 40%%"/>
                                    <field name="state_id" class="oe_no_button" placeholder="State" style="width: 37%%" options='{"no_open": True}' on_change="onchange_state(state_id)"/>
                                    <field name="zip" placeholder="ZIP" style="width: 20%%"/>
                                </div>
                                <field name="city2" placeholder="City2"/>
                                <field name="country_id" placeholder="Country" class="oe_no_button" options='{"no_open": True}'/>
                            </div>
                            <field name="website" widget="url" placeholder="e.g. www.openerp.com"/>
                        </group>
                        <group>
                            <field name="function" placeholder="e.g. Sales Director"
                                attrs="{'invisible': [('is_company','=', True)]}"/>
                            <field name="phone" placeholder="e.g. +32.81.81.37.00"/>
                            <field name="mobile"/>
                            <field name="fax"/>
                            <field name="email" widget="email"/>
                            <field name="title" domain="[('domain', '=', 'contact')]"
                                options='{"no_open": True}' attrs="{'invisible': [('is_company','=', True)]}" />
                        </group>
                    </group>
            """
        }
        for k,v in layouts.items():
            if fmt and (k in fmt):
                doc = etree.fromstring(res)
                for node in doc.xpath("//form/sheet/group"):
                    tree = etree.fromstring(v)
                    node.getparent().replace(node, tree)
                arch = etree.tostring(doc)
            else:
                arch = res
        return arch

    def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if (not view_id) and (view_type=='form') and context and context.get('force_email', False):
            view_id = self.pool.get('ir.model.data').get_object_reference(cr, user, 'base', 'view_partner_simple_form')[1]
        res = super(res_partner,self).fields_view_get(cr, user, view_id, view_type, context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            fields_get = self.fields_get(cr, user, ['street3','street4','city2'], context)
            res['fields'].update(fields_get)
        return res
    
    _defaults = {
        'country_id': _get_default_country_id,
    }


res_partner()
