import React, { useState } from 'react';
import './App.css';

export default function AgentInterface() {
  const [file, setFile] = useState<File | null>(null);
  const [candidatos, setCandidatos] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [Total, setTotal] = useState<number>(0);
  const [puesto, setPuesto] = useState("");
  const [formacion, setFormacion] = useState("");
  const [experiencia, setExperiencia] = useState("");
  const [conocimientos, setConocimientos] = useState("");
  const [competencias, setCompetencias] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      console.log(selectedFile);
    }
  };

  const handleEvaluar = async () => {
    if (!file) {
      alert("Por favor seleccione un archivo RAR o ZIPs para evaluar");
      return;
    }
    if (!puesto || !formacion || !experiencia || !conocimientos || !competencias) {
      alert("Por favor complete todos los campos de criterios");
      return;
    }

    setIsLoading(true);
    setCandidatos([]);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('puesto', puesto);
    formData.append('formacion', formacion);
    formData.append('experiencia', experiencia);
    formData.append('conocimientos', conocimientos);
    formData.append('competencias', competencias);

    try {
      const response = await fetch('http://localhost:8000/api/evaluate-cv-batch', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error("Error en la petición");
      }

      const data = await response.json();

      if (data.error) {
        alert(data.error);
      } else {
        setCandidatos(data.top5 || []);
        setTotal(data.total || 0);
      }
    } catch (error) {
      console.error('Error al evaluar candidatos:', error);
      alert('Error al evaluar candidatos');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelar = async () => {
    try {
      await fetch('http://localhost:8000/api/cancel', {
        method: 'POST'
      });
      setIsLoading(false);
      alert("Evaluación Cancelada Exitosamente");
    } catch (error) {
      console.error('Error al cancelar:', error);
      alert('Error al cancelar');
    }
  };

  return (
    <div className={`container ${candidatos.length > 0 ? 'expanded' : ''}`}>
      <h2 className="title-main">Evaluador de Candidatos IA</h2>

      <div className="content-layout">
        <div className="left-column">
          <div className="requirements-section">
            <h3 className="section-title">Definir el Perfil Buscado</h3>

            <div className="form-group">
              <label className="form-label">Puesto</label>
              <input type="text" className="form-input" placeholder="Ej. Desarrollador Frontend" value={puesto} onChange={(e) => setPuesto(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Formación Académica</label>
              <input type="text" className="form-input" placeholder="Títulos o carreras requeridas..." value={formacion} onChange={(e) => setFormacion(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Experiencia Comprobable</label>
              <textarea className="form-input form-textarea" placeholder="Años y tipo de experiencia..." value={experiencia} onChange={(e) => setExperiencia(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Conocimientos Específicos</label>
              <textarea className="form-input form-textarea" placeholder="Herramientas, lenguajes, etc..." value={conocimientos} onChange={(e) => setConocimientos(e.target.value)} />
            </div>

            <div className="form-group">
              <label className="form-label">Competencias (Habilidades Blandas)</label>
              <textarea className="form-input form-textarea" placeholder="Ej. Trabajo en equipo, proactividad..." value={competencias} onChange={(e) => setCompetencias(e.target.value)} />
            </div>
          </div>


          <div className="upload-section">
            <label className="file-input-wrapper">
              Subir Cvs (Archivos .zip o .rar)
              <input type="file" accept=".zip, .rar" onChange={handleFileChange} className='file-input' />
            </label>

            <div className="button-group">
              <button className='btn btn-primary' onClick={handleEvaluar} disabled={!file || isLoading}>
                {isLoading ? "Evaluando..." : "Evaluar"}
              </button>
              <button className='btn btn-danger' onClick={handleCancelar} disabled={!isLoading}>
                Cancelar
              </button>
            </div>

            {isLoading && (
              <div className="status-loading">
                Procesando archivos y analizando con Inteligencia Artificial...
              </div>
            )}
          </div>
        </div>

        {candidatos.length > 0 && (
          <div className="right-column">
            <div className="results-section">
              <h3 className="results-title">Mejores {candidatos.length} Candidatos (de {Total} procesados)</h3>
              <div className="candidates-list">
                {candidatos.map((candidato, index) => (
                  <div key={index} className="candidate-card">
                    <div className="candidate-header">
                      <div className="candidate-name">#{index + 1} - {candidato.nombre}</div>
                      <div className="candidate-filename">Archivo: {candidato.filename}</div>
                    </div>
                    <div className="candidate-stats">
                      <div className="stat-item">
                        <div className="stat-label">Experiencia</div>
                        <div className="stat-value">{candidato.experiencia}</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">Títulos</div>
                        <div className="stat-value">{candidato.Titulos}</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">Habilidades Blandas</div>
                        <div className="stat-value">{candidato.Habilidades_Blandas}</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">Conocimientos Específicos</div>
                        <div className="stat-value">{candidato.Cursos_perfiles}</div>
                      </div>
                      <div className="stat-item">
                        <div className="stat-label">Puntaje Total</div>
                        <div className="stat-value score">{candidato.puntaje_total}</div>
                      </div>
                    </div>
                    <div className="candidate-comments">
                      <strong>Comentarios:</strong> {candidato.comentarios}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
