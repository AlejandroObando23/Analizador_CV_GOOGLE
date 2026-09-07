from pydantic import BaseModel, Field
from typing import List, Optional, Any

class informacion_candidato(BaseModel):
    nombre: str = Field(..., description='Nombre del candidato')
    experiencia: int = Field(..., description='Puntaje (0-35) de Experiencia evaluado estrictamente en base a los requisitos proporcionados por el usuario.')
    Titulos: int = Field(..., description="Puntaje (0-25) de Formación Académica evaluado según el perfil buscado.")
    Habilidades_Blandas: int = Field(..., description='Puntaje (0-10) de Habilidades Blandas evaluado según lo requerido.')
    Cursos_perfiles: int = Field(..., description='Puntaje (0-30) de Conocimientos Específicos evaluado según las herramientas o conocimientos técnicos solicitados.')
    puntaje_total: int = Field(..., description='Puntaje total sumado sobre 100')
    comentarios: str = Field(..., description='Justificación corta y precisa de la puntuación obtenida.')


    