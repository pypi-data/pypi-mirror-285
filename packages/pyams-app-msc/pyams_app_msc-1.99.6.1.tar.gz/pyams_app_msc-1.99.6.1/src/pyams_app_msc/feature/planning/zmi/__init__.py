#
# Copyright (c) 2015-2023 Thierry Florac <tflorac AT ulthar.net>
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

import json
from datetime import datetime, timedelta

from hypatia.catalog import CatalogQuery
from hypatia.interfaces import ICatalog
from hypatia.query import And, Eq, Ge, Le
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config

from pyams_app_msc.feature.planning import IPlanning, IWfPlanningTarget
from pyams_app_msc.feature.planning.interfaces import ISession
from pyams_app_msc.interfaces import MANAGE_PLANNING_PERMISSION, VIEW_BOOKING_PERMISSION, \
    VIEW_PLANNING_PERMISSION
from pyams_app_msc.shared.theater import IMovieTheaterSettings
from pyams_app_msc.shared.theater.interfaces import IMovieTheater
from pyams_app_msc.shared.theater.interfaces.room import ICinemaRoomContainer
from pyams_catalog.query import CatalogResultSet
from pyams_content_api.feature.json.interfaces import IJSONExporter
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.interfaces.base import USE_INTERNAL_API_PERMISSION
from pyams_skin.viewlet.actions import JsContextAction
from pyams_template.template import template_config
from pyams_utils.factory import get_interface_base_name
from pyams_utils.registry import get_utility
from pyams_utils.timezone import tztime
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_viewlet.viewlet import viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.interfaces.viewlet import IContentManagementMenu, ISecondaryActionsViewletManager
from pyams_zmi.view import InnerAdminView
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


@viewlet_config(name='planning.menu',
                context=IWfPlanningTarget, layer=IAdminLayer,
                manager=IContentManagementMenu, weight=20,
                permission=VIEW_PLANNING_PERMISSION)
class PlanningMenu(NavigationMenuItem):
    """Planning menu"""

    label = _("Planning")
    icon_class = 'fas fa-calendar-week'
    href = '#planning.html'


@pagelet_config(name='planning.html',
                context=IWfPlanningTarget, layer=IPyAMSLayer,
                permission=VIEW_PLANNING_PERMISSION)
@template_config(template='templates/planning.pt', layer=IPyAMSLayer)
class PlanningView(InnerAdminView):
    """Planning view"""

    title = _("Sessions planning")

    @reify
    def theater(self):
        """Theater getter"""
        return get_parent(self.context, IMovieTheater)

    @property
    def rooms(self):
        """Theater rooms iterator getter"""
        theater = self.theater
        if theater is not None:
            yield from ICinemaRoomContainer(theater).get_active_items()

    def get_context(self):
        """View context getter"""
        return IPlanning(self.context)

    @property
    def can_view_bookings(self):
        """Bookings access checker"""
        return bool(self.request.has_permission(VIEW_BOOKING_PERMISSION, context=self.context))

    @property
    def can_edit_planning(self):
        """Calendar editor checker"""
        return bool(self.request.has_permission(MANAGE_PLANNING_PERMISSION, context=self.context))

    def get_calendar_options(self, room):
        """Calendar options getter"""
        context = self.get_context()
        request = self.request
        settings = IMovieTheaterSettings(self.theater)
        can_edit = request.has_permission(MANAGE_PLANNING_PERMISSION, context=context)
        now = tztime(datetime.utcnow())
        week_day = now.weekday()
        next_wednesday = now + timedelta(days=abs(week_day - 2))
        translate = request.localizer.translate
        options = {
            'editable': can_edit,
            'droppable': can_edit,
            'eventSources': [{
                'url': absolute_url(context, request, 'get-planning-events.json'),
                'extraParams': {
                    'room': room.__name__
                }
            }],
            'height': '100%',
            'initialDate': next_wednesday.date().isoformat(),
            'firstDay': settings.calendar_first_day,
            'dateClick': 'MyAMS.msc.calendar.addEvent',
            'initialView': 'timeGridWeek',
            'headerToolbar': {
                'center': 'today',
                'right': 'prev,next dayGridMonth,timeGridWeek,timeGridDay,listMonth'
            },
            'allDaySlot': False,
            'slotDuration': f'00:{settings.calendar_slot_duration:#02}:00',
            'slotMinTime': room.start_time.isoformat(),
            'slotMaxTime': room.end_time.isoformat(),
            'buttonText': {
                'today': translate(_("Today")),
                'month': translate(_("Month")),
                'week': translate(_("Week")),
                'day': translate(_("Day")),
                'list': translate(_("List")),
                'all-day': translate(_("All-day")),
                'prev': " « ",
                'next': " » "
            }
        }
        return json.dumps(options)


@view_config(name='get-planning-events.json',
             context=IPlanning, request_type=IPyAMSLayer,
             permission=USE_INTERNAL_API_PERMISSION,
             renderer='json')
def get_planning_events(request):
    """Planning events getter"""
    params = request.params
    room = params.get('room')
    start = params.get('start')
    end = params.get('end')
    if not (room and start and end):
        raise HTTPBadRequest()
    theater = get_parent(request.context, IMovieTheater)
    if theater is None:
        raise HTTPNotFound()
    container = ICinemaRoomContainer(theater, None)
    if (container is None) or (room not in container):
        raise HTTPNotFound()
    catalog = get_utility(ICatalog)
    query = And(Eq(catalog['object_types'], get_interface_base_name(ISession)),
                Eq(catalog['planning_room'], room),
                Le(catalog['planning_start_date'], datetime.fromisoformat(end)),
                Ge(catalog['planning_end_date'], datetime.fromisoformat(start)))
    events = []
    for session in CatalogResultSet(CatalogQuery(catalog).query(query)):
        exporter = request.registry.queryMultiAdapter((session, request), IJSONExporter)
        if exporter is not None:
            events.append(exporter.to_json(with_edit_info=True, edit_context=request.context))
    return events


@viewlet_config(name='planning.transpose',
                layer=IAdminLayer, view=PlanningView,
                manager=ISecondaryActionsViewletManager, weight=10)
class PlanningTransposeAction(JsContextAction):
    """Planning transpose action"""

    icon_class = 'fas fa-recycle'
    hint = _("Transpose calendars")
    hint_placement = 'bottom'

    href = 'MyAMS.msc.calendar.transpose'


@viewlet_config(name='planning.synchronize',
                layer=IAdminLayer, view=PlanningView,
                manager=ISecondaryActionsViewletManager, weight=20)
class PlanningSynchronizeAction(JsContextAction):
    """Planning synchronize action"""

    icon_class = 'fas fa-sync-alt'
    hint = _("Synchronize calendars views")
    hint_placement = 'bottom'

    href = 'MyAMS.msc.calendar.synchronize'


@viewlet_config(name='planning.scroll',
                layer=IAdminLayer, view=PlanningView,
                manager=ISecondaryActionsViewletManager, weight=30)
class PlanningScrollAction(JsContextAction):
    """Planning scrolling action"""

    icon_class = 'fas fa-arrows-alt-v'
    hint = _("Synchronize calendars scrolling")
    hint_placement = 'bottom'

    href = 'MyAMS.msc.calendar.scroll'
