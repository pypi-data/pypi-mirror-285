#
# Copyright (c) 2015-2024 Thierry Florac <tflorac AT ulthar.net>
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

"""PyAMS_*** module

"""

from datetime import date, datetime, timedelta

from hypatia.catalog import CatalogQuery
from hypatia.interfaces import ICatalog
from hypatia.query import And, Eq, Ge, Lt
from zope.intid.interfaces import IIntIds

from pyams_app_msc.feature.booking import IBookingContainer
from pyams_app_msc.feature.booking.interfaces import BOOKING_STATUS
from pyams_app_msc.feature.planning.interfaces import ISession
from pyams_app_msc.shared.theater import IMovieTheater
from pyams_catalog.query import CatalogResultSet
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import VIEW_SYSTEM_PERMISSION
from pyams_template.template import template_config
from pyams_utils.factory import get_interface_base_name
from pyams_utils.registry import get_utility
from pyams_utils.timezone import tztime
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import INavigationViewletManager
from pyams_zmi.view import InnerAdminView
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


@viewlet_config(name='today-program.menu',
                context=IMovieTheater, layer=IAdminLayer,
                manager=INavigationViewletManager, weight=10,
                permission=VIEW_SYSTEM_PERMISSION)
class TodayProgramMenu(NavigationMenuItem):
    """Today program menu"""

    label = _("Today program")
    icon_class = 'fas fa-tasks'
    href = '#today-program.html'


@pagelet_config(name='today-program.html',
                context=IMovieTheater, layer=IPyAMSLayer,
                permission=VIEW_SYSTEM_PERMISSION)
@template_config(template='templates/today-program.pt',
                 layer=IAdminLayer)
class TodayProgramView(InnerAdminView):
    """Today program view"""

    title = _("Sessions planned for today")

    def get_sessions(self):
        """Today sessions getter"""
        now = tztime(datetime.utcnow())
        today_start = tztime(datetime.combine(date.today(), datetime.min.time()))
        today_end = today_start + timedelta(days=1)
        catalog = get_utility(ICatalog)
        intids = get_utility(IIntIds)
        params = And(Eq(catalog['object_types'], get_interface_base_name(ISession)),
                     Eq(catalog['parents'], intids.register(self.context)),
                     Lt(catalog['planning_start_date'], today_end),
                     Ge(catalog['planning_end_date'], now))
        yield from CatalogResultSet(CatalogQuery(catalog).query(params, sort_index='planning_start_date'))

    @staticmethod
    def get_bookings(session):
        """Session bookings getter"""
        yield from filter(lambda x: x.status == BOOKING_STATUS.ACCEPTED.value,
                          IBookingContainer(session).values())

    def get_groups(self, booking):
        """Booking groups getter"""
        translate = self.request.localizer.translate
        if booking.nb_groups > 1:
            return translate(_("{} groups")).format(booking.nb_groups)
        return translate(_("1 group"))
