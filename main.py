import pandas as pd
from datetime import datetime
from send_message import Message
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import requests

excel_output_file_path = 'Resultado_Facturas.xlsx'
column_client_code = 'CUENTA'
column_client_name = 'NOMBRE_CLIENTE'
column_client_service = 'SERVICIO'
column_client_date_instalation = 'FECHA_INSTALACION_INS'
column_client_phone = 'MEDIO_CONTACTO'
column_client_period = 'PERIODO'
column_client_amount = 'MONTO_FACTURA'
# access_token = '6566335f23ffe'
# instance_API = ''
group_by_client = pd.DataFrame()

#DR doesn't refer to a data row, is a value from row[].iloc[0] Example for servicesDR: 
#['FIBRA TV 30', 'TV INICIAL', 'FIBRA TV 30', 'TV INICIAL', 'TV INICIAL', 'FIBRA TV 30', 'FIBRA TV 30', 'TV INICIAL']

def combine_lists(row):
    periods = row[column_client_period]
    services = []
    servicesDR = []
    new_periods = []
    amounts = []

    uniquies_values = list(set(periods.iloc[0]))

    indexesByValues = {value: [] for value in uniquies_values}

    for i, valor in enumerate(periods.iloc[0]):
        indexesByValues[valor].append(i)
    
    phonesDR = row[column_client_phone].iloc[0]
    phone = phonesDR[0] # Take first value for phone
    
    for valor, indices in indexesByValues.items():
        servicieSubList = []
        new_periods.append(valor)
        
        sublist = [elemento for elemento in indices]
        servicesDR = row[column_client_service].iloc[0]

        for element in sublist:
            servicieSubList.append(servicesDR[element])
        services.append(servicieSubList)

        amountsDR = row[column_client_amount].iloc[0]
        amounts.append(amountsDR[sublist[0]])

    return pd.DataFrame({column_client_period: [new_periods], column_client_service: [services], column_client_amount: [amounts], column_client_phone: phone})

def orderAscending(row):
    periods = row[column_client_period].iloc[0]
    amounts = row[column_client_amount].iloc[0]
    services = row[column_client_service].iloc[0]

    periods_ordered, amounts_ordered, services_ordered = map(list, zip(*sorted(zip(periods, amounts, services), key=lambda x: datetime.strptime(x[0], '%Y-%m'))))

    return pd.DataFrame({column_client_period: [periods_ordered], column_client_amount: [amounts_ordered], column_client_service: [services_ordered]})



#print(group_by_client)
#group_by_client.to_excel('Salida_Facturas111.xlsx')

#send_Messages(group_by_client)


def upload_excel():
    try:
        buttonUploadExcel.config(state="disabled")
        global group_by_client
        # Abrir el explorador de archivos y obtener la ruta del archivo seleccionado
        excel_file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx;*.xls")])

        # Verificar si se seleccionó un archivo
        if excel_file_path:
            # Leer el archivo Excel usando pandas
            df = pd.read_excel(excel_file_path)

            group_by_client = df.sort_values(by=[column_client_period]).groupby(column_client_code).agg({column_client_name: 'first', column_client_date_instalation: 'first', column_client_phone: list, column_client_amount: list, column_client_service: list, column_client_period: list}).reset_index()

            aggregated_df = group_by_client.groupby(column_client_code).apply(combine_lists).reset_index(drop=True)

            group_by_client[[column_client_period, column_client_service, column_client_amount, column_client_phone]] = aggregated_df

            order_periods_ascending = group_by_client.groupby(column_client_code).apply(orderAscending).reset_index(drop=True)

            group_by_client[[column_client_period, column_client_amount, column_client_service]] = order_periods_ascending

            #print(group_by_client)
            labelIsUpload.config(text=f"Se cargó y analizo el archivo: {excel_file_path}\n Ahora puedes enviar los mensajes!")
    except:
        labelIsUpload.config(text=f"No se pudo cargar el archivo, intentalo otra vez!")
    finally:
        buttonUploadExcel.config(state="normal")

def send_messages_to_my_Users():
    global group_by_client
    instance_API = entryIDInstance.get()
    access_token = entryAccessToken.get()
    print(instance_API)
    if len(instance_API) == 0:
        messagebox.showerror("La instancia esta vacía", "Debe colocar su ID instancia")
        return
    if len(access_token) == 0:
        messagebox.showerror("El token esta vacía", "Debe colocar su Token de accesso")
        return
    group_by_client.to_excel(excel_output_file_path)
    #print(group_by_client)
    if group_by_client.empty:
        labelIsEmpty.config(text="El dataframe se encuentra vacio.\nPrimero debe cargarlo!")
        return
    labelIsEmpty.config(text="Este proceso tardara, le notificaremos cuando termine!")
    sendMessages.send_Messages(group_by_client, instance_API, access_token)
    labelIsEmpty.config(text="Termino el proceso!")

# def getInstanceAPI():
#     try:
#         # Intenta hacer una solicitud a un sitio web (por ejemplo, google.com)
#         response = requests.get(f"https://whatsapp.toolhero.tech/api/create_instance?access_token={access_token}", timeout=5)
#         if response.status_code == 200:
#             values = response.json()
#             global instance_API
#             instance_API = values['instance_id']
#             print(instance_API)
#             messagebox.showinfo("Conexión a Internet", "Conexión exitosa a con la API Tool Hero")
#             isIntaceExists.config(text="Existe una instancia")
#         else:
#             messagebox.showerror("Conexión a Internet", "No se pudo conectar a la API.")
#     except requests.ConnectionError:
#         messagebox.showerror("Conexión a Internet", "No hay conexión a Internet.")


# Crear la windowMessages principal
windowMessages = tk.Tk()
windowMessages.title("Enviar mensajes")
windowMessages.geometry("720x640")
#windowMessages.after(1000, getInstanceAPI)

sendMessages = Message()

labelAccessToken = tk.Label(windowMessages, text="Coloque su ID de instancia")
labelAccessToken.pack(pady=10)
entryIDInstance = tk.Entry(windowMessages, width=30)
entryIDInstance.pack(pady=10)

labelAccessToken = tk.Label(windowMessages, text="Coloque su Token de acceso")
labelAccessToken.pack(pady=10)
entryAccessToken = tk.Entry(windowMessages, width=30)
entryAccessToken.pack(pady=10)

labelIsUpload = tk.Label(windowMessages, text="Suba algún archivo")
labelIsUpload.pack(pady=10)

buttonUploadExcel = tk.Button(windowMessages, text="Cargar y analizar excel", command=upload_excel)
buttonUploadExcel.pack(pady=10)

buttonSendMessage = tk.Button(windowMessages, text="Enviar mensajes a usuarios", command=send_messages_to_my_Users)
buttonSendMessage.pack(pady=10)

labelIsEmpty = tk.Label(windowMessages, text="")
labelIsEmpty.pack(pady=10)

# isIntaceExists = tk.Label(windowMessages, text="")
# isIntaceExists.pack(side="bottom")

# buttonCreateInstance = tk.Button(windowMessages, text="Crear instancia", command=getInstanceAPI)
# buttonCreateInstance.pack(side="bottom")

# Ejecutar el bucle principal de la aplicación
windowMessages.mainloop()