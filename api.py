from google.genai import types
import os
import zipfile
import rarfile
import tempfile
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from agent import crear_agente, APP_NAME, USER_ID
from pdf_text import pdf_text
from google.adk.sessions import InMemorySessionService
import shutil
import uvicorn
from fastapi.responses import JSONResponse
from google.adk.runners import Runner
import asyncio

app= FastAPI()
cancel_flag= {"cancelled":False}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/cancel")
async def cancel_evaluation():
    cancel_flag["cancelled"] = True
    return JSONResponse({"message": "Evaluación cancelada correctamente"})

    
@app.post("/api/evaluate-cv")
async def evaluate_cv(
    file: UploadFile=File(...),
    puesto: str = Form(...),
    formacion: str = Form(...),
    experiencia: str = Form(...),
    conocimientos: str = Form(...),
    competencias: str = Form(...)
):
    temp_file_path = f"temp_{file.filename}"
    try:
        with open(temp_file_path,"wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        texto_cv = pdf_text(temp_file_path)
        if not texto_cv:
            return JSONResponse({"error":"No se pudo extraer el texto del CV"},status_code=400)
        session_service = InMemorySessionService()
        session_id=str(uuid.uuid4())
        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=session_id
        )
        agente_dinamico = crear_agente(puesto, formacion, experiencia, conocimientos, competencias)
        runner = Runner(agent=agente_dinamico, app_name=APP_NAME, session_service=session_service)
        # pyrefly: ignore [not-async]
        response_generator = runner.run(new_message=types.Content(role="user", parts=[types.Part.from_text(text=texto_cv)]), user_id=USER_ID, session_id=session_id)
        for event in response_generator:
            pass  # consumir el generador
        session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
        resultado = session.state.get('informacion_candidato')
        if resultado is None:
            return JSONResponse({"error": "El agente no produjo resultado"}, status_code=500)
        return JSONResponse(resultado)
    except Exception as e:
        return JSONResponse({"error":str(e)},status_code=500)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

async def _evaluar_pdf(pdf_path: str, puesto: str, formacion: str, experiencia: str, conocimientos: str, competencias: str) -> dict | None:
    texto_cv=pdf_text(pdf_path)
    if not texto_cv:
        return None
    session_id=str(uuid.uuid4())
    session_service=InMemorySessionService()
    session=await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id
    )
    agente_dinamico = crear_agente(puesto, formacion, experiencia, conocimientos, competencias)
    runner = Runner(agent=agente_dinamico, app_name=APP_NAME, session_service=session_service)
        # pyrefly: ignore [not-async]
    response_generator = runner.run(new_message=types.Content(role="user", parts=[types.Part.from_text(text=texto_cv)]), user_id=USER_ID, session_id=session_id)
    for event in response_generator:
        pass  # consumir el generador
    session = await session_service.get_session(app_name=APP_NAME, user_id=USER_ID, session_id=session_id)
    resultado = session.state.get('informacion_candidato')
    if resultado is None:
        raise Exception("El modelo falló al devolver información (probablemente Rate Limit de Groq)")
    return resultado

@app.post("/api/evaluate-cv-batch")
async def evaluate_archive(
    file: UploadFile = File(...),
    puesto: str = Form(...),
    formacion: str = Form(...),
    experiencia: str = Form(...),
    conocimientos: str = Form(...),
    competencias: str = Form(...)
):
    cancel_flag["cancelled"] = False
    fname = file.filename.lower()
    
    if not (fname.endswith('.zip') or fname.endswith('.rar')):
        return JSONResponse({"error":"El archivo debe ser un .zip o .rar"},status_code=400)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir,fname)
        with open(zip_path, "wb") as f:
            f.write(await file.read())
        try:
            if fname.endswith('.zip'):
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(tmpdir)
            elif fname.endswith('.rar'):
                with rarfile.RarFile(zip_path, 'r') as r:
                    r.extractall(tmpdir)
            pdf_paths = []
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f.lower().endswith(".pdf"):
                        pdf_paths.append(os.path.join(root, f))
            results = []
            for pdf_path in pdf_paths:
                if cancel_flag["cancelled"]:
                    print("[INFO] Evaluación por lotes cancelada por el usuario.")
                    break
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        r = await _evaluar_pdf(pdf_path, puesto, formacion, experiencia, conocimientos, competencias)
                        if r is None:
                            break # PDF sin texto, salir del retry
                        
                        r["filename"] = os.path.basename(pdf_path)
                        results.append(r)
                        print(f"[OK] CV evaluado: {os.path.basename(pdf_path)}. Esperando 15s antes del siguiente...")
                        await asyncio.sleep(15)
                        break  # Éxito, salir del bucle de reintentos
                    except Exception as e:
                        print(f"[ERROR] Fallo al procesar {os.path.basename(pdf_path)} (Intento {attempt+1}/{max_retries}): {str(e)}")
                        if attempt < max_retries - 1:
                            print(f"[RETRY] Reintentando en 15s...")
                            await asyncio.sleep(15)
                        else:
                            print(f"[SKIP] Se omitió {os.path.basename(pdf_path)} tras {max_retries} intentos fallidos.")

            results.sort(key=lambda x: x["puntaje_total"], reverse=True)
            return JSONResponse({"top5": results, "total": len(results)})  
        except Exception as e:
            return JSONResponse({"error":f"No se puede comprimir el archivo {fname}, por favor compruebe que el archivo no esté dañado y que sea un archivo .zip o .rar: {str(e)}"},status_code=500)
            
if __name__ == "__main__":
    print("Iniciando servidor en http://localhost:8000 ...")
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)