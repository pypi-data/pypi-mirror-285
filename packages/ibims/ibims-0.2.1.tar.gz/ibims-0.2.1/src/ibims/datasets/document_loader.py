"""
Contains the dataset for the document loader.
It also contains the validation logic for the document loader dataset.
"""

from typing import Optional

from ibims.bo4e import Dokument, File, Geschaeftspartner, Rechnung, Vertrag
from ibims.datasets import DataSetBaseModel


class TripicaDocumentLoaderDataSet(DataSetBaseModel):
    """
    This is a bo4e data set that consists of
    * a GeschaeftspartnerErweitert
    * a Vertrag
    * a document
    * optionally a Rechnung
    * optionally a File
    In the context of this package is may be used to create Tripica Document Data.
    """

    doc_id: str
    """
    a unique id identifying a document in the tripica data loader set (typically a filename)
    """

    geschaeftspartner: Geschaeftspartner
    """
    The following attribute needs to be filled for this DataSet:
    - externe_referenzen
    especially the customerID
    """

    vertrag: Vertrag
    """
    Each Vertrag needs the following Attribute:
    - vertragsnummer
    """

    rechnung: Optional[Rechnung] = None
    """
    The following attribute needs to be filled for this DataSet:
    - rechnungsnummer
    """

    dokument: Dokument
    """
    A reference to a document
    """

    file: Optional[File] = None
    """
    A reference to a file object
    """
