import pandas as pd
import os
from openai import OpenAI

# Carga la hoja de Excel
ruta = "/content/drive/MyDrive/BASE_DE_DATOS_RETO_2024.xlsx"
df = pd.read_excel(ruta)

# Configura tu clave de API
os.environ["OPENAI_API_KEY"] = "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"

# Crea una instancia del cliente OpenAI
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Define un prompt para estructurar el diagnóstico
def create_prompt(diagnosis):
    return f"""
    Toma el siguiente diagnóstico médico y organiza la información en columnas específicas:

    Diagnóstico: {diagnosis}

    Las columnas son:
    - Nodulos (0.No, 1.Si)
    - Morfología de los nódulos (1. Ovalado, 2. Redondo, 3. Irregular)
    - Márgenes Nódulos (1. Circunscritos, 2. Microlobulados, 3. Indistintos o mal definidos, 4. Obscurecidos, 5. Espiculados)
    - Densidad Nódulo (1. Densidad Grasa, 2. Baja Densidad (hipodenso), 3. Igual Densidad (isodenso), 4. Alta Densidad (hiperdenso))
    - Presencia Microcalcificaciones (0. No, 1. Si)
    - Calcificaciones típicamente benignas (1. Cutáneas, 2. Vasculares, 3. Gruesas o Pop Corn, 4. Leño o Vara, 5. Redondas o puntiformes, 6. Anulares, 7. Distroficas, 8. Leche de Calcio, 9. Suturas)
    - Calcificaciones morfología sospechosa (1. Gruesas heterogéneas, 2. Amorfas, 3. Finas pleomorficas, 4. Líneas finas o lineales ramificadas)
    - Distribución de las calcificaciones (1. Difusas, 2. Regionales, 3. Agrupadas (cúmulo), 4. Segmentaria, 5. Lineal)
    - Presencia de asimetrías (0. No, 1. Si)
    - Tipo de asimetría (1. Asimetría, 2. Asimetría global, 3. Asimetría focal, 4. Asimetría focal evolutiva)
    - Hallazgos asociados (1. Retracción de la piel, 2. Retracción del pezón, 3. Engrosamiento de la piel, 4. Engrosamiento trabecular, 5. Adenopatías axilares)
    - Lateralidad hallazgo (1. DERECHO, 2. IZQUIERDO, 3. BILATERAL)
    - BIRADS (0, 1, 2, 3, 4A, 4B, 4C, 5, 6)

    Devuelve solo la información en un formato de diccionario, sin ninguna introducción ni conclusión.
    El formato debe ser:
    {{
        'Nodulos': valor,
        'Morfologia de los nodulos': valor,
        'Margenes Nodulos': valor,
        'Densidad Nodulo': valor,
        'Presencia Microcalcificaciones': valor,
        'Calcificaciones tipicamente benignas': valor,
        'Calcificaciones morfologia sospechosa': valor,
        'Distribucion de las calcificaciones': valor,
        'Presencia de asimetrias': valor,
        'Tipo de asimetria': valor,
        'Hallazgos asociados': valor,
        'LATERALIDAD HALLAZGO': valor,
        'BIRADS': valor
    }}
    """

# Función para obtener la respuesta del modelo
def get_structured_diagnosis(diagnosis):
    prompt = create_prompt(diagnosis)

    # Realiza la llamada al modelo
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-4o-mini"  # Usa el modelo que prefieras
    )

    # Accede a la respuesta usando el método adecuado
    response = chat_completion.choices[0].message.content

    # Limpiar la respuesta
    cleaned_response = response.split('{' , 1)[-1]  # Asegúrate de obtener solo el diccionario
    cleaned_response = cleaned_response.split('}', 1)[0] + '}'  # Asegúrate de incluir la llave de cierre

    # Intentamos evaluar la respuesta como un diccionario
    try:
        structured_data = eval("{" + cleaned_response)  # Esto debe ser un diccionario
    except SyntaxError:
        print(f": {response}")
        structured_data = {}  # Manejo de error
    return structured_data

# Crear una lista para almacenar los resultados en formato de diccionario
resultados = []

# Iterar sobre cada diagnóstico en la columna "ESTUDIO"
for diagnosis in df["ESTUDIO"]:
    resultado = get_structured_diagnosis(diagnosis)
    resultados.append(resultado)

# Crear un nuevo DataFrame con los resultados estructurados
diagnosis_df = pd.DataFrame(resultados)

# Combinar el DataFrame original con el DataFrame de diagnósticos estructurados
df_final = pd.concat([df, diagnosis_df], axis=1)

# Guardar el DataFrame final en un nuevo archivo Excel
df_final.to_excel("/content/drive/MyDrive/Diagnosticos_Procesados.xlsx", index=False)

print("Diagnósticos procesados y guardados en el formato solicitado.")
