"""Módulo que contiene que se encarga de crear
un registro de correo electrónico para ser enviado por Appsheet"""
from os import environ, path
from datetime import datetime
import re
from enum import Enum, auto
from .google_services import GoogleServices
from .appsheet_service import AppsheetService

ENV_VAR_NAMES = ["EMAIL_APPSHEET_ID", "EMAIL_APPSHEET_TOKEN",
                 "EMAIL_APPSHEET_DESTINATION_FOLDER_ID"]


class EmailServiceError(Exception):
    """Excepción personalizada para errores en EmailService"""

    def __init__(self, message: str):
        super().__init__(f"EmailServiceError: {message}")


class EmailDestination:
    """Destino de un correo electrónico"""
    to: list[str]
    cc: list[str]
    bcc: list[str]

    def _is_valid_email(self, email: str) -> bool:
        email = str(email)
        email_regex = re.compile(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        )
        return re.match(email_regex, email) is not None

    def _validate_email_attribute(self, attribute_name: str):
        attribute_name = str(attribute_name)
        if not hasattr(self, attribute_name):
            raise EmailServiceError(
                f"EmailDestination instance has no attribute '{attribute_name}'")
        email_list = getattr(self, attribute_name)
        for email in email_list:
            if not self._is_valid_email(email):
                raise EmailServiceError(
                    f"Invalid email address '{email}' in list of attribute '{attribute_name}'")

    def __init__(self, to: list[str] | str, cc: list[str] | str = None, bcc: list[str] | str = None):
        if not to:
            raise EmailServiceError(
                "EmailDestination 'to' attribute must have at least one email address")
        if isinstance(to, list):
            self.to = to
        else:
            self.to = [to]
        self._validate_email_attribute('to')
        if cc:
            if isinstance(cc, list):
                self.cc = cc
            else:
                self.cc = [cc]
            self._validate_email_attribute('cc')
        else:
            self.cc = []
        if bcc:
            if isinstance(bcc, list):
                self.bcc = bcc
            else:
                self.bcc = [bcc]
            self._validate_email_attribute('bcc')
        else:
            self.bcc = []

    def add_to(self, to_email: str):
        """Agrega un destinatario"""
        self.to.append(to_email)
        self._validate_email_attribute('to')

    def add_cc(self, cc_email: str):
        """Agrega un destinatario en copia"""
        self.cc.append(cc_email)
        self._validate_email_attribute('cc')

    def add_bcc(self, bcc_email: str):
        """Agrega un destinatario en copia oculta"""
        self.bcc.append(bcc_email)
        self._validate_email_attribute('bcc')

    def get_to(self) -> list[str]:
        """Getter para el destinatario"""
        return self.to

    def get_cc(self) -> list[str]:
        """Getter para el destinatario en copia"""
        return self.cc

    def get_bcc(self) -> list[str]:
        """Getter para el destinatario en copia oculta"""
        return self.bcc


class AttachmentFileType(Enum):
    """Result type of DB select queries and Google API read functions"""
    XLS = auto()
    PDF = auto()


class AttachmentFile:
    """File attachment for an email"""
    file_path: str
    file_name: str
    file_type: AttachmentFileType
    gdrive_mime_type: str

    def _infer_file_type(self):
        if self.file_path.endswith('.xls') or self.file_path.endswith('.xlsx'):
            self.file_type: AttachmentFileType = AttachmentFileType.XLS
        elif self.file_path.endswith('.pdf'):
            self.file_type: AttachmentFileType = AttachmentFileType.PDF
        else:
            raise EmailServiceError(
                f"Attachment file extension not supported yet. Allowed extensions are: '{','.join([file_type.name for file_type in AttachmentFileType])}'")

    def _infer_gdrive_mime_type(self):
        if self.file_type == AttachmentFileType.XLS:
            self.gdrive_mime_type: str = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif self.file_type == AttachmentFileType.PDF:
            self.gdrive_mime_type: str = 'application/pdf'
        else:
            raise EmailServiceError(
                f"Attachment file type '{self.file_type}' is not supported")

    def __init__(self, file_path: str, file_type: AttachmentFileType = None):
        if path.exists(file_path) and path.isfile(file_path):
            self.file_path: str = file_path
            file_name, file_extension = path.splitext(path.basename(file_path))
            if not file_extension:
                raise EmailServiceError(
                    "Attachment file does not have an extension")
            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            self.file_name: str = f"{file_name}_{timestamp}{file_extension}"
        else:
            raise EmailServiceError(
                f"AttachmentFile '{file_path}' does not exist")
        if file_type is None:
            self._infer_file_type()
        elif not isinstance(file_type, AttachmentFileType):
            raise EmailServiceError(
                "Attachment file_type parameter must be an instance of AttachmentFileType")
        else:
            self.file_type: AttachmentFileType = file_type
        self._infer_gdrive_mime_type()

    def get_file_path(self) -> str:
        """Getter para la ruta del archivo"""
        return self.file_path

    def get_file_type(self) -> AttachmentFileType:
        """Getter para el tipo de archivo"""
        return self.file_type

    def get_file_name(self) -> str:
        """Getter para el nombre del archivo"""
        return self.file_name if hasattr(self, 'file_name') else None

    def get_gdrive_mime_type(self) -> str:
        """Getter para el tipo MIME de Google Drive"""
        return self.gdrive_mime_type if hasattr(self, 'gdrive_mime_type') else None


class EmailService():
    """Servicio para envío de mails utilizando Appsheet"""

    def __init__(self):
        try:
            for env_var_name in ENV_VAR_NAMES:
                value = environ.get(env_var_name)
                if value is not None:
                    globals()[env_var_name] = value
                else:
                    raise EnvironmentError(
                        f'Environment variable "{env_var_name}" is NOT set')
            self.email_appsheet_service = AppsheetService(
                EMAIL_APPSHEET_ID, EMAIL_APPSHEET_TOKEN)  # pylint:disable=undefined-variable
            self.email_destination_folder_id = EMAIL_APPSHEET_DESTINATION_FOLDER_ID  # pylint:disable=undefined-variable
            self.email_appsheet_table_name = 'Mails'
            self.email_appsheet_folder_name = GoogleServices.get_file_name_by_file_id(
                self.email_destination_folder_id)
        except Exception as error:
            raise EmailServiceError(
                f"Cannot initialize EmailService: {error}") from error

    def _validate_email_destination(self, destination: EmailDestination):
        """Valida que el destino del correo sea válido"""
        if not isinstance(destination, EmailDestination):
            raise EmailServiceError(
                "destination parameter must be an instance of EmailDestination")

    def _validate_email_attachments(self, attachments: list[AttachmentFile]):
        if attachments and isinstance(attachments, list):
            for i, attachment in enumerate(attachments):
                if not isinstance(attachment, AttachmentFile):
                    raise EmailServiceError(
                        f"Element at index {i} in attachments parameter must be an instance of AttachmentFile")
        else:
            raise EmailServiceError(
                "attachments parameter must be a list of AttachmentFile")

    def send_email(self, destination: EmailDestination, subject: str, body: str, attachments: list[AttachmentFile] = None):
        """Crea un registro de correo electrónico para ser enviado por Appsheet"""
        self._validate_email_destination(destination)
        appsheet_post_data = [{
            "destinatario/s": ','.join(destination.get_to()) if destination.get_to() else '',
            "asunto": str(subject),
            "cuerpo": str(body),
            "cc": ','.join(destination.get_cc()) if destination.get_cc() else '',
            "bcc": ','.join(destination.get_bcc()) if destination.get_bcc() else ''
        }]
        if attachments is not None:
            self._validate_email_attachments(attachments)
            attachments_names = []
            for attachment in attachments:
                uploaded_file_id: str = GoogleServices.upload_file_to_drive(
                    attachment.get_file_path(), attachment.get_file_name(),
                    self.email_destination_folder_id, attachment.get_gdrive_mime_type())
                uploaded_file_name: str = GoogleServices.get_file_name_by_file_id(
                    uploaded_file_id)
                attachments_names.append(
                    f"{self.email_appsheet_folder_name}/{uploaded_file_name}")
            appsheet_post_data[0]['file'] = ','.join(attachments_names)
        self.email_appsheet_service.add_registers_to_table(
            appsheet_post_data, self.email_appsheet_table_name)
