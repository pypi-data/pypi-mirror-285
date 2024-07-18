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

__docformat__ = 'restructuredtext'

from pyramid_mailer.message import Attachment
from zope.dublincore.interfaces import IZopeDublinCore

from pyams_app_msc.feature.planning.interfaces import ISession
from pyams_app_msc.shared.catalog.interfaces import ICatalogEntry
from pyams_app_msc.shared.theater.interfaces import IMovieTheater
from pyams_app_msc.shared.theater.interfaces.mail import IMailTemplates
from pyams_file.interfaces.thumbnail import IThumbnails
from pyams_i18n.interfaces import II18n
from pyams_mail.interfaces import IPrincipalMailInfo
from pyams_mail.message import HTMLMessage
from pyams_security.interfaces import ISecurityManager
from pyams_utils.date import format_date, format_datetime
from pyams_utils.registry import get_utility
from pyams_utils.traversing import get_parent
from pyams_utils.url import absolute_url
from pyams_workflow.interfaces import IWorkflowVersions
from pyams_zmi.utils import get_object_label


def get_booking_message_values(context, request, view):
    """Booking message values getter"""
    theater = get_parent(context, IMovieTheater)
    # generate templates values
    session = ISession(context)
    entry = get_parent(session, ICatalogEntry)
    if entry is not None:
        versions = IWorkflowVersions(entry, None)
        if versions is not None:
            entry = versions.get_version(-1)
    values = {
        'theater_name': II18n(theater).query_attribute('title', request=request),
        'theater_email': theater.contact_email or '',
        'theater_phone': theater.phone_number or '',
        'theater_logo': '',
        'sender_name': request.principal.title,
        'sender_email': '',
        'booking_date': format_date(IZopeDublinCore(session).created),
        'session': get_object_label(session, request, view, name='short-text'),
        'session_title': get_object_label(entry, request, view),
        'session_date': format_datetime(session.start_date)
    }
    logo = theater.logo
    if logo:
        thumbnail = IThumbnails(logo).get_thumbnail('h160')
        values['theater_logo'] = (f'<img src="{absolute_url(thumbnail, request)}"'
                                  f' alt="Logo" />')
    mail_info = IPrincipalMailInfo(request.principal, None)
    if mail_info is not None:
        values['sender_email'] = next(mail_info.get_addresses())
    return values


def get_booking_message(subject, data, context, request, settings):
    """Booking notification message getter"""
    sm = get_utility(ISecurityManager)
    principal = sm.get_raw_principal(context.recipient)
    mail_info = IPrincipalMailInfo(principal, None)
    if mail_info is None:
        return
    mail_addresses = [
        f'{name} <{address}>'
        for name, address in mail_info.get_addresses()
    ]
    translate = request.localizer.translate
    subject = data.get('notify_subject') or translate(subject)
    cc = None
    theater = get_parent(context, IMovieTheater)
    templates = IMailTemplates(theater)
    if templates.send_copy_to_sender:
        principal = request.principal
        if principal is not None:
            mail_info = IPrincipalMailInfo(principal, None)
            if mail_info is not None:
                cc = [
                    f'{name} <{address}>'
                    for name, address in mail_info.get_addresses()
                ]
    message = HTMLMessage(f'{settings.subject_prefix} {subject}',
                          from_addr=f'{settings.source_name} <{settings.source_address}>',
                          to_addr=mail_addresses,
                          cc=cc,
                          html=data.get('notify_message'))
    if data.get('include_quotation'):
        quotation = context.get_quotation()
        if quotation is not None:
            message.attach(Attachment(content_type='application/pdf',
                                      data=quotation.data,
                                      filename=f'{context.quotation_number}.pdf'))
    return message
