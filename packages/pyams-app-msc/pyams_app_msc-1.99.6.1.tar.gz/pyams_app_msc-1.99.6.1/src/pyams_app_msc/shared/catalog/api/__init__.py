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

__docformat__ = 'restructuredtext'

from pyams_app_msc.shared.catalog import ICatalogEntryInfo, IWfCatalogEntry
from pyams_content_api.shared.common.interfaces import IContentAPIInfo
from pyams_utils.adapter import adapter_config


@adapter_config(name='catalog_entry',
                required=IWfCatalogEntry,
                provides=IContentAPIInfo)
def catalog_entry_api_info(context):
    """Catalog entry API info"""
    info = ICatalogEntryInfo(context)
    return {
        'duration': info.duration
    }
