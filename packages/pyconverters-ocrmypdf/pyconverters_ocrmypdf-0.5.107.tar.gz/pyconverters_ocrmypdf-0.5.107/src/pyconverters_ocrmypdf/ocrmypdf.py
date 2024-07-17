from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile, SpooledTemporaryFile
from typing import List, cast, Type

import ocrmypdf as OCRmyPDF
from pydantic import Field, BaseModel
from pymultirole_plugins.v1.converter import ConverterParameters, ConverterBase
from pymultirole_plugins.v1.schema import Document
from starlette.datastructures import UploadFile


# _home = os.path.expanduser('~')
# xdg_cache_home = os.environ.get('XDG_CACHE_HOME') or os.path.join(_home, '.cache')
class TesseractOcrLanguage(str, Enum):
    eng = 'eng'
    fra = 'fra'
    deu = 'deu'
    spa = 'spa'


class OCRmyPDFParameters(ConverterParameters):
    lang: TesseractOcrLanguage = Field(TesseractOcrLanguage.eng, description="""OCR language for Tesseract.
    Language packs must be installed for all languages specified""")


class OCRmyPDFConverter(ConverterBase):
    """Convert OCRized PDF to text using [OCRmyPDF](https://github.com/ocrmypdf/OCRmyPD
    """

    def convert(self, source: UploadFile, parameters: ConverterParameters) \
            -> List[Document]:
        params: OCRmyPDFParameters = \
            cast(OCRmyPDFParameters, parameters)

        doc: Document = None
        try:
            OCRmyPDF.configure_logging(verbosity=0)
            input_file = source.file._file if isinstance(source.file, SpooledTemporaryFile) else source.file
            sidecar_path: Path = None
            with NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as tmp:
                sidecar_path = Path(tmp.name)
            with NamedTemporaryFile(mode="wb", delete=True, suffix=".pdf") as output:
                OCRmyPDF.ocr(input_file, output.name, language=params.lang.value,
                             sidecar=sidecar_path, force_ocr=True, output_type=None)
            with sidecar_path.open("r", encoding="utf-8") as fin:
                doc = Document(identifier=source.filename, title=source.filename, text=fin.read())
                doc.properties = {"fileName": source.filename}
        finally:
            if sidecar_path:
                sidecar_path.unlink()
        return [doc]

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return OCRmyPDFParameters
