"""
Contains the dataset for the network loader.
It also contains the validation logic for the network loader dataset.
"""

from typing import Optional

from ibims.bo4e import (
    Adresse,
    Bilanzierung,
    ConcessionFee,
    Geschaeftspartner,
    Marktlokation,
    Marktteilnehmer,
    Vertrag,
    Zaehler,
    ZaehlerGas,
    Zaehlpunkt,
)
from ibims.datasets import DataSetBaseModel


class TripicaNetworkLoaderDataSet(DataSetBaseModel):
    """
    This is a bo4e data set that consists of
    * two GeschaeftspartnerErweitert as customer
    * a Adresse
    * a Marktlokation
    * a Messlokation
    * two Marktteilnehmer
    * a Zaehler
    In the context of this package is may be used to create Tripica Network Data.
    """

    kunde: Geschaeftspartner
    """
    The following attributes need to be filled for this DataSet and is used for
    the customer that holds the contract:
    - name1 (Surname)
    - name2 (Firstname)
    - name3 (Title e.g. Dr.)
    - gewerbekennzeichnung
    - partneradresse
    """

    liefer_adresse: Adresse

    geschaeftspartner: Geschaeftspartner
    """
    This information is used for the customerMeterReadings part and
    is not a real business partner, so not all information of this object arte needed:
    - name1 (Surname)
    - name2 (Firstname)
    - partneradresse
    """
    # TODO: get a new table join with firstname and surname separated.
    # https://github.com/Hochfrequenz/powercloud2lynqtech/issues/818

    marktlokation: Marktlokation
    """
    The following attributes need to be filled for this DataSet:
    - marktlokations_id
    - sparte
    - bilanzierungsgebiet
    - unterbrechbar
    - gasqualitaet (if sparte is GAS)
    - netzbetreibercodenr
    - netzgebietsnr
    - kundengruppen
    - messtechnische_einordnung
    - ubertragungsnetzgebiet
    """

    netzbetreiber: Optional[Marktteilnehmer] = None
    """
    The following attributes need to be filled for this DataSet:
    - name1
    - rollencodetyp
    - rollencodenummer
    """

    zaehlpunkt: Zaehlpunkt

    messstellenbetreiber: Optional[Marktteilnehmer] = None
    """
    The following attributes need to be filled for this DataSet:
    - rollencodetyp
    - rollencodenummer
    """

    zaehler: Zaehler | ZaehlerGas
    """
    The following attributes need to be filled for this DataSet:
    - zaehlernummer
    - sparte
    - zaehlerauspraegung
    - zaehlertyp
    - zaehlergroeßeGas
    - tarifart
    - zaehlerauspraegung
    - zaehlwerke with each
    - zaehlwerk_id?
    - obis_kennzahl
    """

    vertrag: Vertrag
    """
    The following attributes need to be filled for this DataSet:
    - vertragsnummer (not mapped just for tracking)
    - vertragsbeginn
    - vertragsende
    """

    bilanzierung: Bilanzierung
    """
    The following attributes need to be filled for this DataSet:
    - bilanzkreis
    - bilanzierungsbeginn
    """

    concession_fees: list[ConcessionFee] | None
