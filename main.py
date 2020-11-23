import matplotlib.pyplot as plt
import pandas as pd
import scipy.signal as sc
import os


# ENCUENTRA LOS PICOS DE SEÑAL Y DEVUELVE LOS VALORES EN VOLTIOS Y SUS RESPECTIVOS SEGUNDOS
def encontrar_picos(valores_X, valores_Y):
    picos = sc.find_peaks(valores_Y, height=0.4)                # Encuentra todos los picos mayores a 0.4.
    valores_finales = [[], list(picos[1]['peak_heights'])]      # Lista para devolver valores en x, y.
    for idx in list(picos[0]):
        valores_finales[0].append(valores_X[idx])

    return valores_finales


# ACTIVIDAD DEL PACIENTE
def determinar_actividad(fr_cardiaca, edad, sexo, peso):                        # Se calculan los bpm del paciente.
    fr_max_paciente = (210 - (edad * 0.5)) - (0.01 * peso)
    if 'M' in sexo:
        fr_max_paciente += 4
    print(f'La frecuencia máxima para este paciente es de {fr_max_paciente} bpm')
    if fr_max_paciente < fr_cardiaca:
        print('ADVERTENCIA: El paciente tiene una frecuencia inusualmente alta')

    if edad < 1:                                                                # Se establecen las condiciones según
        fr_baja = 160                                                           # el rango etario del paciente.
        fr_media = 190
    elif 1 <= edad < 10:
        fr_baja = 90
        fr_media = 110
    else:
        fr_baja = 60
        fr_media = 100

    if fr_cardiaca <= fr_baja:                                                  # Se determina el estado del paciente.
        return "durmiendo."
    elif fr_cardiaca <= fr_media:
        return "en reposo."
    else:
        return "realizando ejercicio físico."


# GUARDA LOS RESULTADOS EN UN ARCHIVO TXT
def reportar(senal, lapsos, fr_cardiaca, estado):
    decorador = '-' * 50                                        # Define lo que se proyectará en la consola.
    resultados = f'La frecuencia cardíaca del paciente es de {fr_cardiaca} bpm. \n\n' \
                 f'Los picos de señal son los siguientes:  \n'

    for i in range(len(senal)):
        resultados += f'{senal[i]}eV ---- {round(lapsos[i], 3)}seg \n'
    resultados += f'\nEl paciente se encuentra actualmente {estado}'
    print(decorador, '\n' + resultados, '\n' + decorador)

    if not os.path.isdir('./exports'):
        os.mkdir('./exports')
    elif os.path.isfile('./exports/resultados.txt'):                            # Verifica si existe el archivo.
        sobreescribir = 'undefined'
        while sobreescribir.lower() not in ['si', 'no']:
            print('El archivo resultados.txt ya existe')
            sobreescribir = input('Desea sobreescribirlo? [Sí/No]: ')
        if sobreescribir.lower() == 'no':
            return                                                              # Sale de la funcion sin sobreescribir.

    with open('./exports/resultados.txt', 'w', encoding='utf-8') as f:          # Define el archivo a escribir.
        f.write(resultados)


# INICIA EL PROGRAMA
if __name__ == '__main__':
    plt.figure(num=None, figsize=(15, 6), dpi=120, facecolor='w', edgecolor='k')  # Define el canvas a plotear.

    # IMPORTA LOS DATOS DEL ECM
    while True:
        try:
            nombre = input('Ingrese el nombre del archivo .xlsx (por defecto "electrocardiograma"): ')
            if nombre == '':
                nombre = 'electrocardiograma'
            electro = pd.read_excel(f'./{nombre}.xlsx')
            electro = electro.to_dict('list')
            assert electro['tiempo']
            assert electro['señal']                                  # Verifica que existan los indices de senal/tiempo.
            assert len(electro['señal']) == len(electro['tiempo'])   # Verifica que tengan la misma longitud.
        except (KeyError, AssertionError) as error:
            print(error('Debe ingresar una tabla con una columna de "señal"'
                        ' y otra de "tiempo" de la misma longitud'))
        except FileNotFoundError:
            print(f'Debe haber un archivo "{nombre}.xlsx" dentro del directorio')
        else:
            print('Se cargaron los datos del electrocardiograma correctamente')
            del nombre
            break

    # INPUTS
    while True:
        try:
            # Se piden datos y se verifica que estén dentro de parametros específicos.
            edad_paciente = float(input("Ingrese la edad del paciente: "))
            assert 0 < edad_paciente <= 120, 'La edad del paciente debe estar entre los 0 y 120 años'
            sexo_paciente = input("Ingrese sexo del paciente [M̲asculino/F̲emenino]: ").upper()
            assert sexo_paciente in ['MASCULINO', 'FEMENINO', 'F', 'M'], 'El sexo debe ser Masculino o femenino'
            peso_paciente = float(input("Ingrese el peso del paciente: "))
            assert 0 < peso_paciente <= 250, 'El peso debe estar entre 0kg y 250kg'
        except AssertionError as error:
            print(error)        # Imprime el caso en el que alguno de los datos no cumpla con los requisitos.
        except ValueError:
            print('La edad y el peso deben ingresarse como numeros')
        else:
            paciente = [edad_paciente, sexo_paciente, peso_paciente]
            break
        print('Por favor, ingrese todos los datos nuevamente\n')

    # HACE EL REPORTE TXT
    tiempo_total = electro['tiempo']
    instantes, puntos_max = encontrar_picos(tiempo_total, electro['señal'])
    bpm = round((len(puntos_max) / tiempo_total[-1]) * 60, 2)                      # Saca el bpm a partir de los picos.
    actividad = determinar_actividad(bpm, *paciente)
    reportar(puntos_max, instantes, bpm, actividad)                                # Entra al reporte.

    # PLOTS
    plt.xlabel("TIEMPO (Seg)", fontsize=16)
    plt.ylabel("SEÑAL (V)", fontsize=16)
    plt.plot(tiempo_total, electro['señal'], 'c', label='Señal')                   # Dibuja el ECM.
    plt.plot(instantes, puntos_max, 'mx', label='Picos')                           # Marca los picos con una cruz.
    plt.plot([], [], ' ', label=f'BPM: {bpm}')                                     # Plot vacio para agregar los bpm.

    plt.savefig('./exports/ECG.png')                                               # Guarda el archivo.
    plt.legend()                                                                   # Imprime las etiquetas en el canvas.
    plt.show()
