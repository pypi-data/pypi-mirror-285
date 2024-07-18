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

from datetime import datetime, time, timedelta

from pyramid.events import subscriber
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config
from zope.copy import copy
from zope.interface import Invalid
from zope.lifecycleevent import ObjectModifiedEvent

from pyams_app_msc.feature.booking import IBookingContainer
from pyams_app_msc.feature.planning.interfaces import IPlanning, IPlanningTarget, ISession, IWfPlanningTarget
from pyams_app_msc.interfaces import MANAGE_PLANNING_PERMISSION, VIEW_BOOKING_PERMISSION, VIEW_PLANNING_PERMISSION
from pyams_app_msc.shared.catalog.interfaces import ICatalogEntryInfo, IWfCatalogEntry
from pyams_app_msc.shared.theater.interfaces import IMovieTheater, IMovieTheaterSettings
from pyams_app_msc.shared.theater.interfaces.room import ICinemaRoomContainer
from pyams_content_api.feature.json.interfaces import IJSONExporter
from pyams_form.ajax import ajax_form_config
from pyams_form.button import Buttons, handler
from pyams_form.field import Fields
from pyams_form.interfaces.form import IAJAXFormRenderer, IDataExtractedEvent
from pyams_layer.interfaces import IPyAMSLayer
from pyams_skin.interfaces.view import IModalEditForm
from pyams_skin.schema.button import ActionButton, SubmitButton
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.timezone import tztime
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_workflow.interfaces import IWorkflowVersions
from pyams_zmi.form import AdminModalAddForm, AdminModalEditForm
from pyams_zmi.interfaces import IAdminLayer, TITLE_SPAN_BREAK
from pyams_zmi.interfaces.form import IFormTitle, IModalEditFormButtons
from pyams_zmi.utils import get_object_label

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


@ajax_form_config(name='add-session.html',
                  context=IWfPlanningTarget, layer=IPyAMSLayer,
                  permission=MANAGE_PLANNING_PERMISSION)
class SessionAddForm(AdminModalAddForm):
    """Session add form"""

    subtitle = _("New session")
    legend = _("New session properties")

    fields = Fields(ISession).omit('duration', 'archived')
    content_factory = ISession

    _edit_permission = MANAGE_PLANNING_PERMISSION

    def update_widgets(self, prefix=None):
        entry_info = IWfCatalogEntry(self.context, None)
        if entry_info is not None:
            audiences = self.request.params.get(f'{self.prefix}widgets.audiences')
            if audiences is None:
                for audience in (entry_info.audiences or ()):
                    self.request.GET.add(f'{self.prefix}widgets.audiences', audience)
        super().update_widgets(prefix)
        widgets = self.widgets
        params = self.request.params
        theater = get_parent(self.context, IMovieTheater)
        room = None
        if theater is not None:
            room = ICinemaRoomContainer(theater).get(params.get('room'))
        start_date = widgets.get('start_date')
        if start_date is not None:
            if 'start' in params:
                value = datetime.fromisoformat(params.get('start'))
            elif room is not None:
                start_time = room.start_time
                value = datetime.utcnow().replace(hour=start_time.hour, minute=start_time.minute)
            else:
                value = datetime.utcnow()
            if (value.time() == time(0, 0, 0)) and (room is not None):  # month mode
                start_time = room.start_time
                value = value.replace(hour=start_time.hour, minute=start_time.minute)
            start_date.value = tztime(value).isoformat()
        end_date = widgets.get('end_date')
        if (end_date is not None) and not end_date.value:
            entry = IWfCatalogEntry(self.context, None)
            if start_date is not None:
                settings = IMovieTheaterSettings(theater, None)
                if entry is not None:
                    entry_info = ICatalogEntryInfo(entry)
                    end = datetime.fromisoformat(start_date.value) + timedelta(minutes=entry_info.duration)
                    if settings is not None:
                        end += timedelta(minutes=settings.session_duration_delta)
                    end_date.value = end.isoformat()
                else:
                    if settings is not None:
                        end = datetime.fromisoformat(start_date.value) + \
                            timedelta(minutes=settings.default_session_duration)
                        end_date.value = end.isoformat()
            if room is not None:
                room_widget = widgets.get('room')
                if room_widget is not None:
                    room_widget.value = room.__name__
                capacity = widgets.get('capacity')
                if capacity is not None:
                    capacity.value = room.capacity

    def add(self, obj):
        IPlanning(self.context).add_session(obj)


@adapter_config(required=(IPlanningTarget, IAdminLayer, SessionAddForm),
                provides=IFormTitle)
def planning_add_form_title(context, request, form):
    theater = get_parent(context, IMovieTheater)
    if theater is context:
        return get_object_label(theater, request, form)
    return TITLE_SPAN_BREAK.format(
        get_object_label(theater, request, form),
        get_object_label(context, request, form))


@adapter_config(required=(IPlanningTarget, IAdminLayer, SessionAddForm),
                provides=IAJAXFormRenderer)
class SessionAddFormAJAXRenderer(ContextRequestViewAdapter):
    """Session add form AJAX renderer"""

    def render(self, changes):
        if changes is None:
            return None
        exporter = self.request.registry.getMultiAdapter((changes, self.request), IJSONExporter)
        return {
            'status': 'success',
            'callbacks': [{
                'callback': 'MyAMS.msc.calendar.addEventCallback',
                'options': {
                    'event': exporter.to_json(with_edit_info=True,
                                              edit_context=IPlanning(self.context))
                }
            }]
        }


def can_view_bookings(form):
    """Check if session bookings can be viewed"""
    return form.request.has_permission(VIEW_BOOKING_PERMISSION, context=form.context)

    
def can_delete_session(form):
    """Check if session can be deleted or modified"""
    return form.request.has_permission(MANAGE_PLANNING_PERMISSION, context=form.context)


class ISessionPropertiesEditFormButtons(IModalEditFormButtons):
    """Session properties edit form buttons"""

    bookings = ActionButton(name='bookings',
                            title=_("Bookings"),
                            condition=can_view_bookings)

    delete = SubmitButton(name='delete',
                          title=_("Delete"),
                          condition=can_delete_session)


@ajax_form_config(name='properties.html',
                  context=ISession, layer=IPyAMSLayer,
                  permission=VIEW_PLANNING_PERMISSION)
class SessionPropertiesEditForm(AdminModalEditForm):
    """Session properties edit form"""

    subtitle = _("Session planning")
    legend = _("Session properties")

    fields = Fields(ISession).omit('duration')
    buttons = Buttons(ISessionPropertiesEditFormButtons).select('bookings', 'apply',
                                                                'delete', 'close')

    def update_actions(self):
        super().update_actions()
        bookings = self.actions.get('bookings')
        if bookings is not None:
            if self.context.bookable:
                bookings.add_class('btn-info mr-auto')
                bookings.href = absolute_url(self.context, self.request, 'bookings.html')
                bookings.modal_target = True
            else:
                bookings.add_class('hidden')
        delete = self.actions.get('delete')
        if delete is not None:
            delete.add_class('btn-danger')
            bookings = IBookingContainer(self.context)
            if len(bookings.values()) > 0:
                delete.href = 'MyAMS.msc.session.confirmDelete'

    @handler(buttons['delete'])
    def handle_delete(self, action):
        event_id = self.context.__name__
        planning = IPlanning(self.context)
        del planning[event_id]
        self.finished_state.update({
            'action': action,
            'changes': self.context,
            'event_id': event_id,
            'status': 'deleted'
        })

    @handler(buttons['apply'])
    def handle_apply(self, action):
        super().handle_apply(self, action)


@adapter_config(required=(ISession, IAdminLayer, IModalEditForm),
                provides=IFormTitle)
def session_edit_form_title(context, request, form):
    """Session edit form title"""
    theater = get_parent(context, IMovieTheater)
    target = get_parent(context, IPlanningTarget)
    if target is theater:
        translate = request.localizer.translate
        return TITLE_SPAN_BREAK.format(
            get_object_label(theater, request, form),
            translate(_("Out of catalog activity")))
    versions = IWorkflowVersions(target, None)
    if versions is not None:
        target = versions.get_version(-1)
    return TITLE_SPAN_BREAK.format(
        get_object_label(theater, request, form),
        get_object_label(target, request, form))


@subscriber(IDataExtractedEvent, form_selector=SessionAddForm)
@subscriber(IDataExtractedEvent, form_selector=SessionPropertiesEditForm)
def handle_properties_session_data(event):
    """Handle properties session data"""
    data = event.data
    form = event.form
    context = form.context
    theater = get_parent(context, IMovieTheater)
    # check room capacity
    capacity = data.get('capacity')
    if capacity:
        room = ICinemaRoomContainer(theater).get(data.get('room'))
        if (room is not None) and (capacity > room.capacity):
            form.widgets.errors += (Invalid(_("You can't define a session gauge higher than "
                                              "the room's capacity!")),)
        # check session validated seats
        booking = IBookingContainer(context, None)
        if (booking is not None) and (capacity < booking.get_confirmed_seats()):
            form.widgets.errors += (Invalid(_("The number of validated seats is already higher "
                                              "than this gauge!")),)


@adapter_config(required=(ISession, IAdminLayer, SessionPropertiesEditForm),
                provides=IAJAXFormRenderer)
class SessionPropertiesEditFormAJAXRenderer(ContextRequestViewAdapter):
    """Session properties edit form AJAX renderer"""

    def render(self, changes):
        if not changes:
            return
        exporter = self.request.registry.getMultiAdapter((self.context, self.request), IJSONExporter)
        result = {
            'status': self.request.localizer.translate(self.view.success_message),
            'callbacks': [{
                'callback': 'MyAMS.msc.calendar.editEventCallback',
                'options': {
                    'event': exporter.to_json(with_edit_info=True)
                }
            }]
        }
        return result


@view_config(name='clone-event.json',
             context=ISession, request_type=IPyAMSLayer,
             permission=MANAGE_PLANNING_PERMISSION,
             renderer='json')
def clone_event(request):
    """Clone event"""
    old_session = request.context
    new_session = copy(old_session)
    planning = get_parent(old_session, IPlanning)
    planning.add_session(new_session)
    exporter = request.registry.getMultiAdapter((new_session, request), IJSONExporter)
    return {
        'status': 'success',
        'event': exporter.to_json(with_edit_info=True)
    }


@adapter_config(name='delete',
                required=(ISession, IAdminLayer, SessionPropertiesEditForm),
                provides=IAJAXFormRenderer)
class SessionPropertiesEditFormDeleteActionRenderer(ContextRequestViewAdapter):
    """Session properties edit form delete action renderer"""

    def render(self, changes):
        event_id = self.view.finished_state.get('event_id')
        if not event_id:
            return None
        return {
            'status': 'success',
            'message': self.request.localizer.translate(self.view.success_message),
            'handle_json': True,
            'callbacks': [{
                'callback': 'MyAMS.msc.calendar.deleteEventCallback',
                'options': {
                    'event_id': event_id,
                    'room': self.context.room
                }
            }]
        }


@view_config(name='update-event.json',
             context=ISession, request_type=IPyAMSLayer,
             permission=MANAGE_PLANNING_PERMISSION,
             renderer='json')
def update_event(request):
    """Update event duration after calendar resize"""
    params = request.params
    room = params.get('room')
    start = params.get('start')
    end = params.get('end')
    if not (room and start):
        raise HTTPBadRequest()
    session = request.context
    # check gauge and room seats
    translate = request.localizer.translate
    theater = IMovieTheater(session)
    target_room = ICinemaRoomContainer(theater, {}).get(room)
    if target_room is None:
        request.response.status_code = HTTPNotFound.code
        return {
            'status': 'error',
            'message': translate(_("Unknown room!"))
        }
    container = IBookingContainer(session)
    if target_room.capacity < container.get_confirmed_seats():
        request.response.status_code = HTTPBadRequest.code
        return {
            'status': 'error',
            'messagebox': translate(_("Target room doesn't have enough capacity "
                                      "for confirmed seats of this session!"))
        }
    try:
        # check start date
        start_date = datetime.fromisoformat(start)
        if start_date.time() == time(0, 0):
            # drop in month view -> just set time
            start_date = start_date.replace(hour=session.start_date.hour,
                                            minute=session.start_date.minute)
        # check end date
        if end:
            end_date = datetime.fromisoformat(end)
        else:
            end_date = start_date + session.duration
        # set session attributes
        reduced_capacity = False
        increased_capacity = False
        session.start_date = tztime(start_date)
        session.end_date = tztime(end_date)
        if room != session.room:
            session.room = room
            if target_room.capacity < session.capacity:
                session.capacity = target_room.capacity
                reduced_capacity = True
            elif target_room.capacity > session.capacity:
                session.capacity = target_room.capacity
                increased_capacity = True
        request.registry.notify(ObjectModifiedEvent(session))
    except ValueError:
        request.response.status_code = HTTPBadRequest.code
        return {
            'status': 'error',
            'message': translate(_("Bad parameters"))
        }
    else:
        exporter = request.registry.getMultiAdapter((session, request), IJSONExporter)
        result = {
            'status': 'success',
            'event': exporter.to_json(with_edit_info=True)
        }
        if reduced_capacity:
            result['messagebox'] = {
                'status': 'warning',
                'title': translate(_("Session updated")),
                'message': translate(_("Session capacity has been reduced due to "
                                       "lower room capacity!"))
            }
        elif increased_capacity:
            result['messagebox'] = {
                'status': 'warning',
                'title': translate(_("Session updated")),
                'message': translate(_("Session capacity has been increased to match new room "
                                       "capacity; please check session properties if capacity "
                                       "has to be reduced!"))
            }
        return result
