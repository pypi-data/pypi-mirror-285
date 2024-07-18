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

from datetime import datetime

from hypatia.catalog import CatalogQuery
from hypatia.interfaces import ICatalog
from hypatia.query import And, Any, Eq, Ge, Le
from zope.interface import Interface
from zope.schema import Bool, Choice
from zope.schema.vocabulary import getVocabularyRegistry

from pyams_app_msc.feature.booking import IBookingInfo
from pyams_app_msc.feature.booking.interfaces import BOOKING_STATUS, BOOKING_STATUS_VOCABULARY
from pyams_app_msc.feature.booking.zmi.dashboard import BookingStatusTable, get_booking_element
from pyams_app_msc.feature.booking.zmi.interfaces import IBookingDashboardMenu
from pyams_app_msc.interfaces import VIEW_BOOKING_PERMISSION
from pyams_app_msc.shared.theater import IMovieTheater
from pyams_app_msc.shared.theater.interfaces.room import ROOMS_VOCABULARY
from pyams_catalog.query import CatalogResultSet
from pyams_form.field import Fields
from pyams_form.interfaces.form import IFormFields
from pyams_layer.interfaces import IPyAMSLayer
from pyams_pagelet.pagelet import pagelet_config
from pyams_security.schema import PrincipalField
from pyams_skin.interfaces.viewlet import IHeaderViewletManager
from pyams_table.interfaces import IValues
from pyams_utils.adapter import ContextRequestViewAdapter, adapter_config
from pyams_utils.factory import get_interface_base_name
from pyams_utils.list import unique_iter
from pyams_utils.registry import get_utility
from pyams_utils.schema import DatesRangeField
from pyams_utils.timezone import tztime
from pyams_viewlet.viewlet import EmptyViewlet, viewlet_config
from pyams_zmi.interfaces import IAdminLayer
from pyams_zmi.search import SearchForm, SearchResultsView, SearchView
from pyams_zmi.zmi.viewlet.menu import NavigationMenuItem

__docformat__ = 'restructuredtext'

from pyams_app_msc import _


@viewlet_config(name='advanced-booking-search.menu',
                context=IMovieTheater, layer=IAdminLayer,
                manager=IBookingDashboardMenu, weight=40,
                permission=VIEW_BOOKING_PERMISSION)
class BookingAdvancedSearchMenu(NavigationMenuItem):
    """Booking advanced search menu"""

    label = _("Advanced search")
    href = '#booking-advanced-search.html'


class IBookingAdvancedSearchQuery(Interface):
    """Booking advanced search query interface"""

    recipient = PrincipalField(title=_("Recipient"),
                               required=False)

    status = Choice(title=_("Status"),
                    vocabulary=BOOKING_STATUS_VOCABULARY,
                    required=False)

    session = DatesRangeField(title=_("Session date"),
                              required=False)

    created = DatesRangeField(title=_("Creation date"),
                              required=False)

    modified = DatesRangeField(title=_("Modification date"),
                               required=False)

    include_archives = Bool(title=_("Include archives"),
                            required=False,
                            default=False)


class BookingAdvancedSearchForm(SearchForm):
    """Booking advanced search form"""

    title = _("Bookings search form")

    ajax_form_handler = 'booking-advanced-search-results.html'
    _edit_permission = VIEW_BOOKING_PERMISSION


@adapter_config(required=(Interface, IAdminLayer, BookingAdvancedSearchForm),
                provides=IFormFields)
def booking_advanced_search_form_fields(context, request, form):
    """Booking advanced search form fields"""
    return Fields(IBookingAdvancedSearchQuery)


@pagelet_config(name='booking-advanced-search.html',
                context=IMovieTheater, layer=IPyAMSLayer,
                permission=VIEW_BOOKING_PERMISSION)
class BookingAdvancedSearchView(SearchView):
    """Booking advanced search view"""

    title = _("Bookings search form")
    header_label = _("Advanced search")
    search_form = BookingAdvancedSearchForm


class BookingAdvancedSearchResultsTable(BookingStatusTable):
    """Booking advanced search form results table"""


@adapter_config(required=(IMovieTheater, IPyAMSLayer, BookingAdvancedSearchResultsTable),
                provides=IValues)
class BookingAdvancedSearchResultsValues(ContextRequestViewAdapter):
    """Booking advanced search results values"""

    def get_params(self, data):
        catalog = get_utility(ICatalog)
        vocabulary = getVocabularyRegistry().get(self.context, ROOMS_VOCABULARY)
        params = And(Eq(catalog['object_types'], get_interface_base_name(IBookingInfo)),
                     Any(catalog['planning_room'], vocabulary.by_value.keys()),
                     Eq(catalog['booking_status'], [status.value for status in BOOKING_STATUS]))
        if data.get('recipient'):
            params &= Eq(catalog['booking_recipient'], data['recipient'])
        if data.get('status'):
            params &= Eq(catalog['booking_status'], data['status'])
        session_after, session_before = data.get('session', (None, None))
        if session_after:
            params &= Ge(catalog['planning_start_date'],
                         tztime(datetime.fromisoformat(session_after.isoformat())))
        if session_before:
            params &= Le(catalog['planning_end_date'],
                         tztime(datetime.fromisoformat(session_before.isoformat())))
        created_after, created_before = data.get('created', (None, None))
        if created_after:
            params &= Ge(catalog['created_date'],
                         tztime(datetime.fromisoformat(created_after.isoformat())))
        if created_before:
            params &= Le(catalog['created_date'],
                         tztime(datetime.fromisoformat(created_before.isoformat())))
        modified_after, modified_before = data.get('modified', (None, None))
        if modified_after:
            params &= Ge(catalog['modified_date'],
                         tztime(datetime.fromisoformat(modified_after.isoformat())))
        if modified_before:
            params &= Le(catalog['modified_date'],
                         tztime(datetime.fromisoformat(modified_before.isoformat())))
        return params

    @property
    def values(self):
        """Booking advanced search results values getter"""

        def true_filter(item):
            return True

        def archives_filter(item):
            return not item.booking.archived

        form = BookingAdvancedSearchForm(self.context, self.request)
        form.update()
        data, _errors = form.extract_data()
        params = self.get_params(data)
        catalog = get_utility(ICatalog)
        if data.get('include_archives'):
            booking_filter = true_filter
        else:
            booking_filter = archives_filter
        yield from filter(booking_filter,
                          map(get_booking_element,
                              unique_iter(CatalogResultSet(CatalogQuery(catalog).query(params)))))


@pagelet_config(name='booking-advanced-search-results.html',
                context=IMovieTheater, layer=IPyAMSLayer,
                permission=VIEW_BOOKING_PERMISSION, xhr=True)
class BookingAdvancedSearchResultsView(SearchResultsView):
    """Booking advanced search results view"""

    table_label = _("Search results")
    table_class = BookingAdvancedSearchResultsTable


@viewlet_config(name='pyams.content_header',
                layer=IAdminLayer, view=BookingAdvancedSearchResultsView,
                manager=IHeaderViewletManager, weight=10)
class BookingAdvancedSearchResultsViewHeaderViewlet(EmptyViewlet):
    """Booking advanced search results view header viewlet"""

    def render(self):
        return '<h1 class="mt-3"></h1>'
