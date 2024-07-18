from enum import StrEnum


class MediaTypes(StrEnum):
    APPLICATION_JSON = "application/json"
    SIREN = "application/vnd.siren+json"
    PROBLEM_DETAILS = "application/problem+json"
    MULTIPART_FORM_DATA = "multipart/form-data"
    OCTET_STREAM = "application/octet-stream"

    XML = "application/xml"
    ZIP = "application/zip"
    PDF = "application/pdf"
    TEXT = "text/plain"
    HTML = "text/html"
    CSV = "text/csv"
    SVG = "image/svg+xml"
    PNG = "image/png"
    JPEG = "image/jpeg"
    BMP = "image/bmp"


class SirenClasses(StrEnum):
    FileUploadAction = "FileUploadAction"
