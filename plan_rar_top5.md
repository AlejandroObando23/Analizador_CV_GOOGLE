# Plan de Implementación: Subida de RAR con múltiples CVs y Top 5 Visual

## Contexto del Proyecto

El proyecto actual evalúa **un solo CV en PDF** a la vez mediante:
- **`pdf_text.py`** → extrae texto del PDF con PyPDF2
- **`agent.py`** → agente Gemini que evalúa con un schema Pydantic (`informacion_candidato`)
- **`api.py`** → endpoint FastAPI `/api/evaluate-cv` que recibe un PDF y devuelve la evaluación
- **`Frontend/index.html`** → UI que sube un PDF y muestra el resultado de un candidato

El objetivo es: **aceptar un `.rar` con varios PDFs, evaluar todos, y mostrar el Top 5 ordenado por puntaje**.

---

## Cambios necesarios por archivo

### 1. `api.py` — Nuevo endpoint para RAR

**Qué debes hacer:**

Instala primero la librería `rarfile` (o `patool`) para extraer archivos `.rar` en Python:

```bash
pip install rarfile
```

> [!IMPORTANT]
> `rarfile` requiere que tengas **WinRAR** o **UnRAR** instalado en el sistema y accesible desde el PATH. Descarga `UnRAR.exe` desde https://www.rarlab.com/rar_add.htm y ponlo en una carpeta del PATH (ej. `C:\Windows\System32\`).

**Nuevo endpoint a agregar:** `POST /api/evaluate-rar`

La lógica del endpoint debe:

1. Recibir el archivo `.rar` como `UploadFile`.
2. Guardarlo temporalmente en disco (igual que ya haces con el PDF).
3. Extraer todos los archivos `.pdf` del `.rar` a una carpeta temporal.
4. Por cada PDF extraído:
   - Llamar a `pdf_text()` para extraer el texto.
   - Crear una sesión **nueva e independiente** con `InMemorySessionService` (sesión distinta por cada CV para evitar contaminación de estados).
   - Correr el `runner` con el texto del CV.
   - Recuperar `informacion_candidato` del estado de la sesión.
   - Agregar el resultado a una lista.
5. Ordenar la lista de resultados por `puntaje_total` de mayor a menor.
6. Retornar los **primeros 5** resultados (`lista[:5]`).
7. En el bloque `finally`, eliminar el archivo `.rar` temporal y la carpeta de extracción.

> [!WARNING]
> Cada CV debe tener su **propio `SESSION_ID`** único (p. ej. `f"session_{index}"` o `uuid4()`). Si reutilizas el mismo `SESSION_ID` para todos, el agente mezclará resultados entre candidatos.

**Esquema de respuesta esperado (JSON):**
```json
{
  "top5": [
    {
      "nombre": "...",
      "experiencia": 30,
      "Titulos": 20,
      "Habilidades_Blandas": 8,
      "Cursos_perfiles": 12,
      "puntaje_total": 70,
      "comentarios": "..."
    },
    ...
  ]
}
```

---

### 2. `pdf_text.py` — Sin cambios

La función `pdf_text()` ya funciona correctamente para leer un PDF individual. No necesita modificación.

---

### 3. `agent.py` — Sin cambios

El agente y su schema actual son suficientes. Lo único que cambia es cómo se invocan (múltiples veces desde el nuevo endpoint).

---

### 4. `req.py` — Sin cambios

El modelo Pydantic `informacion_candidato` ya define correctamente los campos de evaluación.

---

### 5. `Frontend/index.html` — Nuevas secciones visuales

**Qué debes hacer:**

#### a) Agregar un nuevo input de archivo para `.rar`

Añade un segundo `<input type="file">` que acepte únicamente `.rar`:

```html
<input type="file" id="rarFile" name="rarFile" accept=".rar">
```

O bien, convierte la UI a un modo de selección (PDF único vs. RAR múltiple) con dos secciones separadas o un toggle/tabs.

#### b) Nuevo bloque de JavaScript para manejar el envío del RAR

Al hacer submit con el archivo `.rar`:
1. Crear un `FormData` y agregar el archivo con `formData.append('file', rarFile.files[0])`.
2. Hacer `fetch` a `http://localhost:8000/api/evaluate-rar` con método `POST`.
3. Recibir el JSON con `{ top5: [...] }`.
4. Llamar a una función `renderTop5(data.top5)` que construya el HTML del ranking.

#### c) Función `renderTop5(candidatos)` — HTML del ranking

Esta función debe generar dinámicamente las tarjetas del Top 5. Cada tarjeta debe mostrar:

| Campo | Descripción |
|---|---|
| Posición (🥇🥈🥉4°5°) | Puesto en el ranking |
| Nombre | `candidato.nombre` |
| Puntaje Total | `candidato.puntaje_total / 100` con barra de progreso |
| Experiencia | `/35` |
| Títulos | `/25` |
| Habilidades Blandas | `/10` |
| Cursos/Perfiles | `/30` |
| Comentarios | Texto del evaluador |

> [!TIP]
> Para la barra de progreso del puntaje puedes usar un `<div>` con `width: X%` usando el valor de `puntaje_total` directamente como porcentaje (ya es sobre 100).

**Ejemplo de estructura HTML a generar por tarjeta:**

```html
<div class="rank-card rank-1">
  <div class="rank-badge">🥇 #1</div>
  <h3>Nombre del Candidato</h3>
  <div class="score-bar">
    <div class="score-fill" style="width: 85%"></div>
  </div>
  <span class="score-label">85 / 100</span>
  <div class="breakdown">
    <span>Experiencia: 30/35</span>
    <span>Títulos: 20/25</span>
    <span>Hab. Blandas: 8/10</span>
    <span>Cursos: 27/30</span>
  </div>
  <p class="comments">"Excelente candidato con perfil completo..."</p>
</div>
```

#### d) Estilos CSS a agregar en `<style>` dentro del `<head>`

Agrega estilos para:
- `.rank-card` → tarjeta con borde, sombra, padding
- `.rank-1` → borde dorado / acento especial para el primero
- `.rank-2` → borde plateado
- `.rank-3` → borde bronce
- `.rank-badge` → insignia de posición (grande, centrada)
- `.score-bar` → contenedor gris de la barra de progreso
- `.score-fill` → relleno de la barra (gradiente verde→azul)
- `.breakdown` → grid de 2 columnas con los sub-puntajes
- `.comments` → texto en cursiva, color gris suave

---

## Orden de implementación recomendado

```
[ ] 1. Instalar dependencias: pip install rarfile
[ ] 2. Verificar que UnRAR.exe esté en el PATH del sistema
[ ] 3. Modificar api.py → agregar el endpoint /api/evaluate-rar
[ ] 4. Probar el endpoint con Postman o cURL enviando un .rar de prueba
[ ] 5. Modificar Frontend/index.html → agregar input de .rar + JS del fetch
[ ] 6. Implementar renderTop5() con las tarjetas visuales
[ ] 7. Agregar los estilos CSS del ranking
[ ] 8. Prueba completa end-to-end: subir .rar → ver Top 5 en pantalla
```

---

## Dependencias adicionales necesarias

| Librería | Comando | Para qué |
|---|---|---|
| `rarfile` | `pip install rarfile` | Extraer archivos `.rar` en Python |
| `UnRAR.exe` | Descarga manual desde rarlab.com | Requerido por `rarfile` en Windows |

> [!NOTE]
> Alternativa a `rarfile`: puedes usar `patool` (`pip install patool`) que soporta más formatos y puede usar el WinRAR que ya tengas instalado. El comando de extracción sería `patool.extract_archive("archivo.rar", outdir="carpeta_temporal")`.

---

## Flujo completo de datos

```
Usuario sube archivo.rar
        │
        ▼
[FastAPI] POST /api/evaluate-rar
        │
        ├─ Extrae PDF_1.pdf → pdf_text() → Agent (session_1) → resultado_1
        ├─ Extrae PDF_2.pdf → pdf_text() → Agent (session_2) → resultado_2
        ├─ Extrae PDF_3.pdf → pdf_text() → Agent (session_3) → resultado_3
        │         ...
        └─ Ordena por puntaje_total DESC → retorna top 5
                  │
                  ▼
        [Frontend] renderTop5(data.top5)
                  │
                  ▼
        🥇🥈🥉 Tarjetas visuales con ranking
```
