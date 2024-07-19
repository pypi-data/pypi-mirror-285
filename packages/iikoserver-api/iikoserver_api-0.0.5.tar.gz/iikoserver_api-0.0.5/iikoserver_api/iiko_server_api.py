import hashlib
from datetime import datetime, timedelta
import re
from typing import Optional

import requests
import xmltodict

from iikoserver_api.schemas.incoming_invoice import IncomingInvoiceItem, IncomingInvoice
from iikoserver_api.schemas.outgoing_invoice import OutgoingInvoice


class IikoServerApi:
    _default_headers = {'Content-Type': 'application/xml'}

    def __init__(self, url, login, password):
        self.url = url
        self.login = login
        self.password = hashlib.sha1(password.encode()).hexdigest()
        self.token = None
        self.connected = False

    def send(self,
             action: str,
             method: str = 'GET',
             params: dict = None,
             headers: dict = None,
             data: any = None,
             json=None):
        if headers is None:
            headers = self._default_headers
        url = f'{self.url}{action}/'
        response = requests.request(method=method, url=url, params=params, headers=headers, data=data, json=json)

        if response.ok:
            return response.content
        else:
            error_info = {
                "response_status": response.status_code,
                "response_info": response.content.decode()
            }
            if action not in ['logout', 'auth']:
                self.logout()
            raise ConnectionError(error_info)

    def auth(self):
        params = {
            'login': self.login,
            'pass': self.password,
        }
        response = self.send(action='auth', params=params)
        data = response.decode()
        print(data)
        self.token = data
        self.connected = True

    def logout(self):
        params = {
            'key': self.token
        }
        data = self.send(action='logout', params=params)
        print(data.decode())
        self.token = None
        self.connected = False

    def export_outgoing_invoice(self, from_datetime: datetime,
                                to_datetime: datetime) -> Optional[list[OutgoingInvoice]]:
        params = {
            'key': self.token,
            'from': from_datetime.strftime('%Y-%m-%d'),
            'to': to_datetime.strftime('%Y-%m-%d'),
        }
        data = self.send(action='documents/export/outgoingInvoice', params=params)
        xml_dict_data = xmltodict.parse(data.decode())
        documents = xml_dict_data['outgoingInvoiceDtoes']
        if documents:
            documents = [documents['document']] if type(documents['document']) is dict else documents['document']
        else:
            return
        result = []
        for document in documents:
            document_items = document['items']['item']
            if document_items:
                document_items = [document['items']['item']] \
                    if type(document['items']['item']) is dict else document['items']['item']
            else:
                continue
            dict_data = {'items': []}
            for key, value in document.items():
                if key == 'items':
                    continue
                key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
                dict_data[key] = value

            for item in document_items:
                new_item = {}
                for key, value in item.items():
                    key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
                    new_item[key] = value

                dict_data['items'].append(new_item)

            result.append(OutgoingInvoice(**dict_data))

        return result

    def export_incoming_invoice(self, from_datetime: datetime,
                                to_datetime: datetime) -> Optional[list[IncomingInvoice]]:
        params = {
            'key': self.token,
            'from': from_datetime.strftime('%Y-%m-%d'),
            'to': to_datetime.strftime('%Y-%m-%d'),
        }
        data = self.send(action='documents/export/incomingInvoice', params=params)
        xml_dict_data = xmltodict.parse(data.decode())
        documents = xml_dict_data['incomingInvoiceDtoes']
        if documents:
            documents = [documents['document']] if type(documents['document']) is dict else documents['document']
        else:
            return
        result = []
        for document in documents:
            document_items = document['items']['item']
            if document_items:
                document_items = [document['items']['item']] \
                    if type(document['items']['item']) is dict else document['items']['item']
            else:
                continue
            dict_data = {'items': []}
            for key, value in document.items():
                if key == 'items':
                    continue
                key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
                dict_data[key] = value

            for item in document_items:
                new_item = {}
                for key, value in item.items():
                    key = re.sub(r'(?<!^)(?=[A-Z])', '_', key).lower()
                    new_item[key] = value

                dict_data['items'].append(new_item)

            result.append(IncomingInvoice(**dict_data))

        return result

    def __enter__(self):
        self.auth()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

