from pathlib import Path
from typing import List
from pyconverters_ocrmypdf.ocrmypdf import OCRmyPDFConverter, OCRmyPDFParameters
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile


def test_ocrmypdf():
    converter = OCRmyPDFConverter()
    parameters = OCRmyPDFParameters()
    testdir = Path(__file__).parent
    source = Path(testdir, 'data/PB-Scanned.pdf')
    with source.open("rb") as fin:
        docs: List[Document] = converter.convert(UploadFile(source.name, fin, 'application/pdf'), parameters)
        assert len(docs) == 1
        assert docs[0].identifier
        assert docs[0].text
