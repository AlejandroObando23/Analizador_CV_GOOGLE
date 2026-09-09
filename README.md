# 📄 Analizador de CVs con Inteligencia Artificial

Sistema de evaluación automatizada de currículums (CVs) impulsado por **Google ADK** (Agent Development Kit) y el modelo **Gemini**. Permite a un reclutador definir el perfil buscado y obtener un ranking de los mejores candidatos evaluados por IA.

---

## 🚀 Características

- **Evaluación individual** de un CV en formato PDF.
- **Evaluación por lotes** subiendo un archivo `.zip` o `.rar` con múltiples CVs.
- **Ranking automático** de candidatos ordenados por puntaje total.
- **Criterios personalizables** por el reclutador: formación académica, experiencia, conocimientos técnicos y competencias blandas.
- **Cancelación de evaluaciones** en curso.
- **Reintentos automáticos** ante fallos de la API (hasta 3 intentos por CV).

---

## 🛠️ Tecnologías

| Componente | Tecnología |
|---|---|
| **Backend** | Python, FastAPI, Uvicorn |
| **Agente IA** | Google ADK (`google-adk`), Gemini 3.1 Flash Lite |
| **Extracción de texto** | PyPDF2 |
| **Frontend** | React + TypeScript (Vite) |
| **Archivos comprimidos** | `zipfile` (stdlib), `rarfile` |

---

## 📁 Estructura del Proyecto

```
├── Backend/          # Servidor y API (FastAPI)
│   ├── agent.py      # Definición del agente evaluador con Google ADK
│   ├── api.py        # API REST con FastAPI (endpoints de evaluación)
│   ├── req.py        # Modelo Pydantic con el esquema de evaluación
│   ├── pdf_text.py   # Extracción de texto de archivos PDF
│   └── models.py     # Modelos adicionales de datos
├── Docs/             # Documentos del proyecto
│   └── FORMULARIO TECNICO ESPECIALIZADO_APC (1).docx
├── Frontend/         # Aplicación React + Vite
│   ├── src/
│   │   ├── App.tsx   # Componente principal de la interfaz
│   │   ├── App.css   # Estilos de la aplicación
│   │   ├── index.css # Estilos base
│   │   └── main.tsx  # Punto de entrada de React
│   ├── package.json
│   └── vite.config.ts
├── .env              # Variables de entorno (API Keys) — NO subir a Git
├── .gitignore        # Archivos ignorados por Git
└── README.md
```

---

## ⚙️ Requisitos Previos

- **Python 3.12+**
- **Node.js 18+**
- **UnRAR** (solo si se van a procesar archivos `.rar`):
  - Windows: Descargar `UnRAR.exe` desde [rarlab.com](https://www.rarlab.com/rar_add.htm) y agregarlo al PATH del sistema.

---

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/AlejandroObando23/Analizador_CV_GOOGLE.git
cd Analizador_CV_GOOGLE
```

### 2. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto con las siguientes claves:

```env
GEMINI_API_KEY="tu_api_key_de_google"
GROQ_API_KEY="tu_api_key_de_groq"
```

### 3. Instalar dependencias del Backend

```bash
cd Backend
pip install fastapi uvicorn google-adk google-genai python-dotenv PyPDF2 rarfile pydantic
```

### 4. Instalar dependencias del Frontend

```bash
cd Frontend
npm install
```

---

## ▶️ Ejecución

### Iniciar el Backend (API)

Desde el directorio `Backend`:

```bash
cd Backend
python api.py
```

El servidor se iniciará en `http://localhost:8000`.

### Iniciar el Frontend

En una terminal separada:

```bash
cd Frontend
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`.

---

## 🔗 Endpoints de la API

### `POST /api/evaluate-cv`

Evalúa un único CV en PDF.

**Parámetros (FormData):**

| Campo | Tipo | Descripción |
|---|---|---|
| `file` | PDF | Archivo del currículum |
| `puesto` | string | Nombre del puesto buscado |
| `formacion` | string | Criterios de formación académica |
| `experiencia` | string | Criterios de experiencia laboral |
| `conocimientos` | string | Criterios de conocimientos técnicos |
| `competencias` | string | Criterios de habilidades blandas |

**Respuesta:**
```json
{
  "nombre": "Juan Pérez",
  "experiencia": 30,
  "Titulos": 20,
  "Habilidades_Blandas": 8,
  "Cursos_perfiles": 25,
  "puntaje_total": 83,
  "comentarios": "Candidato con sólida experiencia..."
}
```

---

### `POST /api/evaluate-cv-batch`

Evalúa múltiples CVs desde un archivo `.zip` o `.rar`.

**Parámetros (FormData):** Idénticos al endpoint individual, pero `file` debe ser un `.zip` o `.rar` que contenga los PDFs.

**Respuesta:**
```json
{
  "top5": [ ... ],
  "total": 10
}
```

---

### `POST /api/cancel`

Cancela una evaluación por lotes que esté en curso.

---

## 📊 Criterios de Evaluación

El agente evalúa cada CV en 4 categorías con un puntaje máximo de **100 puntos**:

| Categoría | Puntaje Máximo |
|---|---|
| Formación Académica (Títulos) | 25 |
| Experiencia Comprobable | 35 |
| Conocimientos Específicos | 30 |
| Competencias (Habilidades Blandas) | 10 |
| **Total** | **100** |

---

## 👤 Autor

**Alejandro Obando**

---


