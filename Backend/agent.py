from google.adk.agents import LlmAgent
from google.genai import types
from dotenv import load_dotenv
from req import informacion_candidato


load_dotenv()

APP_NAME = 'evaluador_candidatos'
USER_ID = 'USER_1'

def crear_agente(puesto: str, formacion: str, experiencia: str, conocimientos: str, competencias: str) -> LlmAgent:
    instruction = f'''
    Eres un evaluador de candidatos profesional.
    El perfil que estamos buscando es un: {puesto}.
    
    Evalúa el CV basándote estrictamente en los siguientes criterios definidos por el reclutador:

    1. Formación Académica (Títulos) -> Hasta 25 puntos
       Criterio a evaluar: {formacion}

    2. Experiencia Comprobable -> Hasta 35 puntos
       Criterio a evaluar: {experiencia}

    3. Conocimientos Específicos -> Hasta 30 puntos
       Criterio a evaluar: {conocimientos}

    4. Competencias (Habilidades Blandas) -> Hasta 10 puntos
       Criterio a evaluar: {competencias}

    IMPORTANTE Y OBLIGATORIO: Tu única respuesta debe ser utilizar la herramienta (tool) o esquema JSON requerido para extraer la información. No respondas con texto libre. Extrae el "nombre", asigna la "experiencia", los "Titulos", "Habilidades_Blandas", "Cursos_perfiles", calcula el "puntaje_total" y añade tus "comentarios".'''

    return LlmAgent(
        name="Evaluador_candidatos",
        model="gemini-3.1-flash-lite",
        description='Agente de IA para evaluar las cv de los candidatos que se postulen a las respectivas areas',
        instruction=instruction,
        output_schema=informacion_candidato,
        generate_content_config=types.GenerateContentConfig(
            temperature=0.1
        ),
        output_key='informacion_candidato'
    )