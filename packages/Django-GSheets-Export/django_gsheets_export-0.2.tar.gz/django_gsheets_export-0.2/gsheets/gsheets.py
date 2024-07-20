from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from django.conf import settings
from django.db.models.query import QuerySet
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
import json
from datetime import datetime, timedelta


class GoogleSheets:
    """
    GoogleSheets

    Class for working with Google Sheets API.

    It requires the following packages:
        - google-api-python-client
        - google-auth


    Attributes:
        SCOPES (list): List of authorization scopes required by Google Sheets and Google Drive API.
        sheet_service: Service object for interacting with Google Sheets API.
        drive_service: Service object for interacting with Google Drive API.
        spreadsheet_id (str): ID of the spreadsheet.
        spreadsheet: Spreadsheet object.
        url (str): URL of the spreadsheet.
        # valores (List[List[str]]): Values to be updated in the spreadsheet.

    Methods:
        __init__(): Initializes the GoogleSheets object.
        create(title: str) -> None: Creates a new spreadsheet.
        update_values(values: Union[QuerySet, Dict[str, Any], List[List[str]]], range_name: str = 'Sheet1',
          value_input_option: str = 'USER_ENTERED') -> None: Updates the values in the specified sheet and range.
        dict_to_list(dictionary: Dict[Any, str]) -> List[List[str]]: Converts a dictionary to a nested list.
        queryset_to_list(queryset: QuerySet) -> List[List[str]]: Converts a Django queryset to a nested list.
        share(email: str) -> str: Shares the spreadsheet with the specified email.
    """
    SCOPES = ['https://www.googleapis.com/auth/drive',
              'https://www.googleapis.com/auth/spreadsheets']
    roles = ['owner', 'organizer', 'fileOrganizer', 'writer', 'commenter', 'reader']
    types = ['user', 'group', 'domain']  # 'anyone'


    # valores = None

    def __init__(self):

        self.sheet_service = None
        self.drive_service = None
        self.spreadsheet_id = ''
        self.spreadsheet = None
        self.url = ''
        self.expiration_days = 15
        self.role = 'reader'
        self.type = 'user'

        cred_file = getattr(settings, "GOOGLE_APPLICATION_CREDENTIALS_PATH", None)

        if cred_file is None:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS_PATH must be set")

        creds = service_account.Credentials.from_service_account_file(cred_file,
                                                                      scopes=self.SCOPES)

        try:
            self.service = build('sheets', 'v4', credentials=creds)
        except Exception as e:
            raise Exception(f"Something bad happened: {e}")
        try:
            self.drive_service = build('drive', 'v3', credentials=creds)
        except Exception as e:
            raise Exception(f"Something bad happened: {e}")

    def create(self, title):
        """
        :param title: Spreadsheet title
        :return:

        Creation of Spreadsheet
        """

        try:
            body = {"properties": {"title": title}}
            self.spreadsheet = (
                self.service.spreadsheets().create(body=body, fields="spreadsheetId").execute()
            )
            # console print(f"Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
            self.spreadsheet_id = self.spreadsheet.get("spreadsheetId")
            self.url = f'https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit#gid=0'
        except HttpError as error:
            raise Exception(f"Something bad happened: {error}")

        return self.spreadsheet_id

    def update_values(self, values, range_name="Sheet1", value_input_option="USER_ENTERED"):  # "RAW"
        """
        :param values: The values to be updated in the spreadsheet. It can be a Django QuerySet, a dictionary or a list.
        :param range_name: The range in the spreadsheet where the values will be updated. Default value is "Sheet1".
        :param value_input_option: The input value option. Default value is "USER_ENTERED".
        :return: The result of the update operation.

        Add data to Sp
        """
        def dict_to_list(dictionary):
            """
            Converts a dictionary to a list of lists.

            :param dictionary: The input dictionary.
            :return: The converted list of lists.
            """
            datos = [[k for k in dictionary[0].keys()], [list(k.values()) for k in dictionary]]
            return datos

        def queryset_to_list(queryset):
            """
            Convert a Django queryset to a nested array.

            :param queryset: The Django queryset to be converted. type queryset: QuerySet :return: A nested array
            representation of the queryset, with the field names as the first row and the queryset data as the
            following rows. :rtype: list
            """
            fields = [f.name for f in queryset.model._meta.fields]
            fields_labels = [f.verbose_name for f in queryset.model._meta.fields]

            seria = serializers.serialize("json", queryset=queryset, cls=DjangoJSONEncoder,
                                          use_natural_foreign_keys=True,
                                          use_natural_primary_keys=True, fields=[*fields])

            j = json.loads(seria)
            data = [f['fields'] for f in j]
            titles = fields_labels  # list(datos[0].keys())
            returnlist = [list(k.values()) for k in data]
            returnlist.insert(0, titles)

            return data

        if isinstance(values, QuerySet):
            _values = queryset_to_list(values)
        elif isinstance(values, dict):
            _values = dict_to_list(values)
        elif isinstance(values, list):
            _values = values
        else:
            raise Exception(f"Format not supported")


        try:
            body = {"values": _values}
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

            return result
        except HttpError as error:

            return error

    def share(self, email):

        if self.role not in self.roles:
            raise Exception(f"Role {self.role} not supported")

        if self.type not in self.types:
            raise Exception(f"Type {self.type} not supported")

        user_permission = ({'type': self.type,
                            'role': self.role,
                            'emailAddress': email,

                            })

        if self.expiration_days > 0:
            expiration = (datetime.utcnow() + timedelta(days=self.expiration_days)).isoformat(timespec='seconds') + 'Z'
            user_permission['expirationTime'] = expiration

        content_restriction = {'copyRequiresWriterPermission': True,
                               # 'writersCanShare': True,
                               }

        self.drive_service.permissions().create(fileId=self.spreadsheet_id,
                                                body=user_permission,
                                                fields='id').execute()

        self.drive_service.files().update(fileId=self.spreadsheet_id,
                                          body={'contentRestrictions': [content_restriction]},
                                          fields="contentRestrictions").execute()

        return self.url


    def delete(self, file_id):
        body_value = {'trashed': True}

        response = self.drive_service.files().update(fileId=file_id, body=body_value).execute()