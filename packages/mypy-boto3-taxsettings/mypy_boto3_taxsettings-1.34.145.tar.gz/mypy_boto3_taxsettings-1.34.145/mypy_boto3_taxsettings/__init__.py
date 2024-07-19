"""
Main interface for taxsettings service.

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_taxsettings import (
        Client,
        ListTaxRegistrationsPaginator,
        TaxSettingsClient,
    )

    session = Session()
    client: TaxSettingsClient = session.client("taxsettings")

    list_tax_registrations_paginator: ListTaxRegistrationsPaginator = client.get_paginator("list_tax_registrations")
    ```
"""

from .client import TaxSettingsClient
from .paginator import ListTaxRegistrationsPaginator

Client = TaxSettingsClient

__all__ = ("Client", "ListTaxRegistrationsPaginator", "TaxSettingsClient")
