"""
Type annotations for taxsettings service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_taxsettings/type_defs/)

Usage::

    ```python
    from mypy_boto3_taxsettings.type_defs import TaxInheritanceDetailsTypeDef

    data: TaxInheritanceDetailsTypeDef = ...
    ```
"""

import sys
from typing import Dict, List, Sequence

from .literals import (
    AddressRoleTypeType,
    IndustriesType,
    IsraelCustomerTypeType,
    IsraelDealerTypeType,
    MalaysiaServiceTaxCodeType,
    PersonTypeType,
    RegistrationTypeType,
    SaudiArabiaTaxRegistrationNumberTypeType,
    SectorType,
    TaxRegistrationNumberTypeType,
    TaxRegistrationStatusType,
    TaxRegistrationTypeType,
    UkraineTrnTypeType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "TaxInheritanceDetailsTypeDef",
    "AddressTypeDef",
    "JurisdictionTypeDef",
    "CanadaAdditionalInfoTypeDef",
    "EstoniaAdditionalInfoTypeDef",
    "GeorgiaAdditionalInfoTypeDef",
    "IsraelAdditionalInfoTypeDef",
    "ItalyAdditionalInfoTypeDef",
    "KenyaAdditionalInfoTypeDef",
    "MalaysiaAdditionalInfoTypeDef",
    "PolandAdditionalInfoTypeDef",
    "RomaniaAdditionalInfoTypeDef",
    "SaudiArabiaAdditionalInfoTypeDef",
    "SouthKoreaAdditionalInfoTypeDef",
    "SpainAdditionalInfoTypeDef",
    "TurkeyAdditionalInfoTypeDef",
    "UkraineAdditionalInfoTypeDef",
    "BrazilAdditionalInfoTypeDef",
    "IndiaAdditionalInfoTypeDef",
    "MalaysiaAdditionalInfoOutputTypeDef",
    "BatchDeleteTaxRegistrationErrorTypeDef",
    "BatchDeleteTaxRegistrationRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "BatchPutTaxRegistrationErrorTypeDef",
    "DeleteTaxRegistrationRequestRequestTypeDef",
    "DestinationS3LocationTypeDef",
    "TaxDocumentMetadataTypeDef",
    "GetTaxRegistrationRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListTaxRegistrationsRequestRequestTypeDef",
    "SourceS3LocationTypeDef",
    "AccountMetaDataTypeDef",
    "AdditionalInfoRequestTypeDef",
    "AdditionalInfoResponseTypeDef",
    "BatchDeleteTaxRegistrationResponseTypeDef",
    "GetTaxRegistrationDocumentResponseTypeDef",
    "PutTaxRegistrationResponseTypeDef",
    "BatchPutTaxRegistrationResponseTypeDef",
    "GetTaxRegistrationDocumentRequestRequestTypeDef",
    "ListTaxRegistrationsRequestListTaxRegistrationsPaginateTypeDef",
    "TaxRegistrationDocumentTypeDef",
    "TaxRegistrationTypeDef",
    "TaxRegistrationWithJurisdictionTypeDef",
    "VerificationDetailsTypeDef",
    "GetTaxRegistrationResponseTypeDef",
    "AccountDetailsTypeDef",
    "TaxRegistrationEntryTypeDef",
    "ListTaxRegistrationsResponseTypeDef",
    "BatchPutTaxRegistrationRequestRequestTypeDef",
    "PutTaxRegistrationRequestRequestTypeDef",
)

TaxInheritanceDetailsTypeDef = TypedDict(
    "TaxInheritanceDetailsTypeDef",
    {
        "inheritanceObtainedReason": NotRequired[str],
        "parentEntityId": NotRequired[str],
    },
)
AddressTypeDef = TypedDict(
    "AddressTypeDef",
    {
        "addressLine1": str,
        "city": str,
        "countryCode": str,
        "postalCode": str,
        "addressLine2": NotRequired[str],
        "addressLine3": NotRequired[str],
        "districtOrCounty": NotRequired[str],
        "stateOrRegion": NotRequired[str],
    },
)
JurisdictionTypeDef = TypedDict(
    "JurisdictionTypeDef",
    {
        "countryCode": str,
        "stateOrRegion": NotRequired[str],
    },
)
CanadaAdditionalInfoTypeDef = TypedDict(
    "CanadaAdditionalInfoTypeDef",
    {
        "canadaQuebecSalesTaxNumber": NotRequired[str],
        "canadaRetailSalesTaxNumber": NotRequired[str],
        "isResellerAccount": NotRequired[bool],
        "provincialSalesTaxId": NotRequired[str],
    },
)
EstoniaAdditionalInfoTypeDef = TypedDict(
    "EstoniaAdditionalInfoTypeDef",
    {
        "registryCommercialCode": str,
    },
)
GeorgiaAdditionalInfoTypeDef = TypedDict(
    "GeorgiaAdditionalInfoTypeDef",
    {
        "personType": PersonTypeType,
    },
)
IsraelAdditionalInfoTypeDef = TypedDict(
    "IsraelAdditionalInfoTypeDef",
    {
        "customerType": IsraelCustomerTypeType,
        "dealerType": IsraelDealerTypeType,
    },
)
ItalyAdditionalInfoTypeDef = TypedDict(
    "ItalyAdditionalInfoTypeDef",
    {
        "cigNumber": NotRequired[str],
        "cupNumber": NotRequired[str],
        "sdiAccountId": NotRequired[str],
        "taxCode": NotRequired[str],
    },
)
KenyaAdditionalInfoTypeDef = TypedDict(
    "KenyaAdditionalInfoTypeDef",
    {
        "personType": PersonTypeType,
    },
)
MalaysiaAdditionalInfoTypeDef = TypedDict(
    "MalaysiaAdditionalInfoTypeDef",
    {
        "serviceTaxCodes": Sequence[MalaysiaServiceTaxCodeType],
    },
)
PolandAdditionalInfoTypeDef = TypedDict(
    "PolandAdditionalInfoTypeDef",
    {
        "individualRegistrationNumber": NotRequired[str],
        "isGroupVatEnabled": NotRequired[bool],
    },
)
RomaniaAdditionalInfoTypeDef = TypedDict(
    "RomaniaAdditionalInfoTypeDef",
    {
        "taxRegistrationNumberType": TaxRegistrationNumberTypeType,
    },
)
SaudiArabiaAdditionalInfoTypeDef = TypedDict(
    "SaudiArabiaAdditionalInfoTypeDef",
    {
        "taxRegistrationNumberType": NotRequired[SaudiArabiaTaxRegistrationNumberTypeType],
    },
)
SouthKoreaAdditionalInfoTypeDef = TypedDict(
    "SouthKoreaAdditionalInfoTypeDef",
    {
        "businessRepresentativeName": str,
        "itemOfBusiness": str,
        "lineOfBusiness": str,
    },
)
SpainAdditionalInfoTypeDef = TypedDict(
    "SpainAdditionalInfoTypeDef",
    {
        "registrationType": RegistrationTypeType,
    },
)
TurkeyAdditionalInfoTypeDef = TypedDict(
    "TurkeyAdditionalInfoTypeDef",
    {
        "industries": NotRequired[IndustriesType],
        "kepEmailId": NotRequired[str],
        "secondaryTaxId": NotRequired[str],
        "taxOffice": NotRequired[str],
    },
)
UkraineAdditionalInfoTypeDef = TypedDict(
    "UkraineAdditionalInfoTypeDef",
    {
        "ukraineTrnType": UkraineTrnTypeType,
    },
)
BrazilAdditionalInfoTypeDef = TypedDict(
    "BrazilAdditionalInfoTypeDef",
    {
        "ccmCode": NotRequired[str],
        "legalNatureCode": NotRequired[str],
    },
)
IndiaAdditionalInfoTypeDef = TypedDict(
    "IndiaAdditionalInfoTypeDef",
    {
        "pan": NotRequired[str],
    },
)
MalaysiaAdditionalInfoOutputTypeDef = TypedDict(
    "MalaysiaAdditionalInfoOutputTypeDef",
    {
        "serviceTaxCodes": List[MalaysiaServiceTaxCodeType],
    },
)
BatchDeleteTaxRegistrationErrorTypeDef = TypedDict(
    "BatchDeleteTaxRegistrationErrorTypeDef",
    {
        "accountId": str,
        "message": str,
        "code": NotRequired[str],
    },
)
BatchDeleteTaxRegistrationRequestRequestTypeDef = TypedDict(
    "BatchDeleteTaxRegistrationRequestRequestTypeDef",
    {
        "accountIds": Sequence[str],
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
        "HostId": NotRequired[str],
    },
)
BatchPutTaxRegistrationErrorTypeDef = TypedDict(
    "BatchPutTaxRegistrationErrorTypeDef",
    {
        "accountId": str,
        "message": str,
        "code": NotRequired[str],
    },
)
DeleteTaxRegistrationRequestRequestTypeDef = TypedDict(
    "DeleteTaxRegistrationRequestRequestTypeDef",
    {
        "accountId": NotRequired[str],
    },
)
DestinationS3LocationTypeDef = TypedDict(
    "DestinationS3LocationTypeDef",
    {
        "bucket": str,
        "prefix": NotRequired[str],
    },
)
TaxDocumentMetadataTypeDef = TypedDict(
    "TaxDocumentMetadataTypeDef",
    {
        "taxDocumentAccessToken": str,
        "taxDocumentName": str,
    },
)
GetTaxRegistrationRequestRequestTypeDef = TypedDict(
    "GetTaxRegistrationRequestRequestTypeDef",
    {
        "accountId": NotRequired[str],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
ListTaxRegistrationsRequestRequestTypeDef = TypedDict(
    "ListTaxRegistrationsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SourceS3LocationTypeDef = TypedDict(
    "SourceS3LocationTypeDef",
    {
        "bucket": str,
        "key": str,
    },
)
AccountMetaDataTypeDef = TypedDict(
    "AccountMetaDataTypeDef",
    {
        "accountName": NotRequired[str],
        "address": NotRequired[AddressTypeDef],
        "addressRoleMap": NotRequired[Dict[AddressRoleTypeType, JurisdictionTypeDef]],
        "addressType": NotRequired[AddressRoleTypeType],
        "seller": NotRequired[str],
    },
)
AdditionalInfoRequestTypeDef = TypedDict(
    "AdditionalInfoRequestTypeDef",
    {
        "canadaAdditionalInfo": NotRequired[CanadaAdditionalInfoTypeDef],
        "estoniaAdditionalInfo": NotRequired[EstoniaAdditionalInfoTypeDef],
        "georgiaAdditionalInfo": NotRequired[GeorgiaAdditionalInfoTypeDef],
        "israelAdditionalInfo": NotRequired[IsraelAdditionalInfoTypeDef],
        "italyAdditionalInfo": NotRequired[ItalyAdditionalInfoTypeDef],
        "kenyaAdditionalInfo": NotRequired[KenyaAdditionalInfoTypeDef],
        "malaysiaAdditionalInfo": NotRequired[MalaysiaAdditionalInfoTypeDef],
        "polandAdditionalInfo": NotRequired[PolandAdditionalInfoTypeDef],
        "romaniaAdditionalInfo": NotRequired[RomaniaAdditionalInfoTypeDef],
        "saudiArabiaAdditionalInfo": NotRequired[SaudiArabiaAdditionalInfoTypeDef],
        "southKoreaAdditionalInfo": NotRequired[SouthKoreaAdditionalInfoTypeDef],
        "spainAdditionalInfo": NotRequired[SpainAdditionalInfoTypeDef],
        "turkeyAdditionalInfo": NotRequired[TurkeyAdditionalInfoTypeDef],
        "ukraineAdditionalInfo": NotRequired[UkraineAdditionalInfoTypeDef],
    },
)
AdditionalInfoResponseTypeDef = TypedDict(
    "AdditionalInfoResponseTypeDef",
    {
        "brazilAdditionalInfo": NotRequired[BrazilAdditionalInfoTypeDef],
        "canadaAdditionalInfo": NotRequired[CanadaAdditionalInfoTypeDef],
        "estoniaAdditionalInfo": NotRequired[EstoniaAdditionalInfoTypeDef],
        "georgiaAdditionalInfo": NotRequired[GeorgiaAdditionalInfoTypeDef],
        "indiaAdditionalInfo": NotRequired[IndiaAdditionalInfoTypeDef],
        "israelAdditionalInfo": NotRequired[IsraelAdditionalInfoTypeDef],
        "italyAdditionalInfo": NotRequired[ItalyAdditionalInfoTypeDef],
        "kenyaAdditionalInfo": NotRequired[KenyaAdditionalInfoTypeDef],
        "malaysiaAdditionalInfo": NotRequired[MalaysiaAdditionalInfoOutputTypeDef],
        "polandAdditionalInfo": NotRequired[PolandAdditionalInfoTypeDef],
        "romaniaAdditionalInfo": NotRequired[RomaniaAdditionalInfoTypeDef],
        "saudiArabiaAdditionalInfo": NotRequired[SaudiArabiaAdditionalInfoTypeDef],
        "southKoreaAdditionalInfo": NotRequired[SouthKoreaAdditionalInfoTypeDef],
        "spainAdditionalInfo": NotRequired[SpainAdditionalInfoTypeDef],
        "turkeyAdditionalInfo": NotRequired[TurkeyAdditionalInfoTypeDef],
        "ukraineAdditionalInfo": NotRequired[UkraineAdditionalInfoTypeDef],
    },
)
BatchDeleteTaxRegistrationResponseTypeDef = TypedDict(
    "BatchDeleteTaxRegistrationResponseTypeDef",
    {
        "errors": List[BatchDeleteTaxRegistrationErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetTaxRegistrationDocumentResponseTypeDef = TypedDict(
    "GetTaxRegistrationDocumentResponseTypeDef",
    {
        "destinationFilePath": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutTaxRegistrationResponseTypeDef = TypedDict(
    "PutTaxRegistrationResponseTypeDef",
    {
        "status": TaxRegistrationStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchPutTaxRegistrationResponseTypeDef = TypedDict(
    "BatchPutTaxRegistrationResponseTypeDef",
    {
        "errors": List[BatchPutTaxRegistrationErrorTypeDef],
        "status": TaxRegistrationStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetTaxRegistrationDocumentRequestRequestTypeDef = TypedDict(
    "GetTaxRegistrationDocumentRequestRequestTypeDef",
    {
        "destinationS3Location": DestinationS3LocationTypeDef,
        "taxDocumentMetadata": TaxDocumentMetadataTypeDef,
    },
)
ListTaxRegistrationsRequestListTaxRegistrationsPaginateTypeDef = TypedDict(
    "ListTaxRegistrationsRequestListTaxRegistrationsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
TaxRegistrationDocumentTypeDef = TypedDict(
    "TaxRegistrationDocumentTypeDef",
    {
        "s3Location": SourceS3LocationTypeDef,
    },
)
TaxRegistrationTypeDef = TypedDict(
    "TaxRegistrationTypeDef",
    {
        "legalAddress": AddressTypeDef,
        "legalName": str,
        "registrationId": str,
        "registrationType": TaxRegistrationTypeType,
        "status": TaxRegistrationStatusType,
        "additionalTaxInformation": NotRequired[AdditionalInfoResponseTypeDef],
        "certifiedEmailId": NotRequired[str],
        "sector": NotRequired[SectorType],
        "taxDocumentMetadatas": NotRequired[List[TaxDocumentMetadataTypeDef]],
    },
)
TaxRegistrationWithJurisdictionTypeDef = TypedDict(
    "TaxRegistrationWithJurisdictionTypeDef",
    {
        "jurisdiction": JurisdictionTypeDef,
        "legalName": str,
        "registrationId": str,
        "registrationType": TaxRegistrationTypeType,
        "status": TaxRegistrationStatusType,
        "additionalTaxInformation": NotRequired[AdditionalInfoResponseTypeDef],
        "certifiedEmailId": NotRequired[str],
        "sector": NotRequired[SectorType],
        "taxDocumentMetadatas": NotRequired[List[TaxDocumentMetadataTypeDef]],
    },
)
VerificationDetailsTypeDef = TypedDict(
    "VerificationDetailsTypeDef",
    {
        "dateOfBirth": NotRequired[str],
        "taxRegistrationDocuments": NotRequired[Sequence[TaxRegistrationDocumentTypeDef]],
    },
)
GetTaxRegistrationResponseTypeDef = TypedDict(
    "GetTaxRegistrationResponseTypeDef",
    {
        "taxRegistration": TaxRegistrationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AccountDetailsTypeDef = TypedDict(
    "AccountDetailsTypeDef",
    {
        "accountId": NotRequired[str],
        "accountMetaData": NotRequired[AccountMetaDataTypeDef],
        "taxInheritanceDetails": NotRequired[TaxInheritanceDetailsTypeDef],
        "taxRegistration": NotRequired[TaxRegistrationWithJurisdictionTypeDef],
    },
)
TaxRegistrationEntryTypeDef = TypedDict(
    "TaxRegistrationEntryTypeDef",
    {
        "registrationId": str,
        "registrationType": TaxRegistrationTypeType,
        "additionalTaxInformation": NotRequired[AdditionalInfoRequestTypeDef],
        "certifiedEmailId": NotRequired[str],
        "legalAddress": NotRequired[AddressTypeDef],
        "legalName": NotRequired[str],
        "sector": NotRequired[SectorType],
        "verificationDetails": NotRequired[VerificationDetailsTypeDef],
    },
)
ListTaxRegistrationsResponseTypeDef = TypedDict(
    "ListTaxRegistrationsResponseTypeDef",
    {
        "accountDetails": List[AccountDetailsTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchPutTaxRegistrationRequestRequestTypeDef = TypedDict(
    "BatchPutTaxRegistrationRequestRequestTypeDef",
    {
        "accountIds": Sequence[str],
        "taxRegistrationEntry": TaxRegistrationEntryTypeDef,
    },
)
PutTaxRegistrationRequestRequestTypeDef = TypedDict(
    "PutTaxRegistrationRequestRequestTypeDef",
    {
        "taxRegistrationEntry": TaxRegistrationEntryTypeDef,
        "accountId": NotRequired[str],
    },
)
