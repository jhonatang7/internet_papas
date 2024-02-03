import pandas as pd
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import locale
import requests

class Message:
    column_client_code = 'CUENTA'
    column_client_name = 'NOMBRE_CLIENTE'
    column_client_service = 'SERVICIO'
    column_client_date_instalation = 'FECHA_INSTALACION_INS'
    column_client_phone = 'MEDIO_CONTACTO'
    column_client_period = 'PERIODO'
    column_client_amount = 'MONTO_FACTURA'
    COMPANY_NAME = 'DISTRIBUIDO GUILLERMO'
    users_with_response_failed = []
    COUNTRY_CODE = '591'

    def __init__(self) -> None:
        pass

    def getFirstPhone(self, phoneString):
        #print(phoneString)
        patron = re.compile(r'\b\d{8}\b')

        coincidencias = patron.findall(phoneString)

        # Devolver el primer número de celular encontrado o None si no se encontró ninguno
        return coincidencias[0] if coincidencias else None

    def verifyDateInstalation(self, date_instalation_str):
        current_date = datetime.now()
        date_instalation = datetime.strptime(date_instalation_str, '%Y-%m-%d %H:%M:%S.%f')

        month_difference = current_date - relativedelta(months=9)

        isLater = date_instalation < month_difference
        return isLater

    def post_Message(self, index, phone, message, instance_API, access_token):
        try:
            phone = self.COUNTRY_CODE + phone
            requestJson = { "number" : phone, "type": "text", "message": message, "instance_id": instance_API, "access_token": access_token}
            response = requests.post("https://whatsapp.toolhero.tech/api/send", requestJson)
            if response.status_code != 200:
                self.users_with_response_failed.append("Busca el indice:"+str(index))
        except Exception:
            pass

    def create_file_txt(self, data, file_name="NoRecibieronMensajes.txt"):
        with open(file_name, "w") as file:
            for value in data:
                file.write(str(value) + "\n")

    def send_Messages(self, df, instace_API, access_token):
        locale.setlocale(locale.LC_TIME, 'es_ES')
        for index, row in df.iterrows():
            message = ""
            code = row[self.column_client_code]
            name = row[self.column_client_name]
            services = row[self.column_client_service]
            date_instalation = row[self.column_client_date_instalation]
            phone = row[self.column_client_phone]
            periods = row[self.column_client_period]
            amounts = row[self.column_client_amount]
            totalAmount = 0

            #print(index)
            if(self.verifyDateInstalation(date_instalation)):
                continue

            if(pd.isna(phone)):
                #print(phone)
                continue

            phone = self.getFirstPhone(phone)
            #print(phone)

            message = f"""Señ@r {name}
De Parte de {self.COMPANY_NAME}, le mandamos un reporte sobre el estado de su cuenta de internet, para no sufrir cortes por parte de ENTEL.
        
Usted al momento de registrarse en Entel, se le proporciona un código unico el cual esta vinculado al servicio adquirido, el código único que se le atribuye es: {code}
        
Este es el reporte:\n"""
            
            for period, amount, serviceList in zip(periods, amounts, services):
                #print(period)
                totalAmount += amount
                period_obj = datetime.strptime(period, '%Y-%m')
                # Formatea la fecha como 'Abril de 2023'
                formatted_period = period_obj.strftime('%B de %Y').capitalize()

                if (len(serviceList) == 1):
                    formatted_services = serviceList[0]
                else:
                    formatted_services = (lambda lst: ', '.join(lst[:-1]) + (' y ' if lst else '') + lst[-1])(serviceList)

                message += f"   Periodo: {formatted_period} debe {amount}Bs. por los servicios: {formatted_services}\n"
            formatted_total_amount = round(totalAmount, 2)
            message += f"""
El total es de: {formatted_total_amount}Bs.\n"""
            message += "Gracias por su atención!"
            self.post_Message(index, phone, message, instace_API, access_token)
            #print(message)
            # if(index == 849):
            #     print(name)
            #     print(message)
        locale.setlocale(locale.LC_TIME, 'C')
        self.create_file_txt(self.users_with_response_failed)
        self.users_with_response_failed = []
        #print(self.users_with_response_failed)

    