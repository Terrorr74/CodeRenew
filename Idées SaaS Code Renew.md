# CodeRenew — Repo de démarrage (MVP)

Ce document contient les fichiers essentiels pour démarrer un MVP de **Modernisation Automatique de Code Legacy** (CodeRenew). Copie/colle les fichiers dans ton projet, ou utilise ce doc comme blueprint.

---

## Arborescence proposée

```
/codecrenew-mvp
  /backend
    /app
      main.py
      routers/modernize.py
      services/claude_service.py
      utils/diff_utils.py
    requirements.txt
    Dockerfile
  /frontend
    package.json
    pages/
      index.jsx
      upload.jsx
    components/
      FileUploader.jsx
      CodeViewer.jsx
    utils/api.js
  README.md
```

---

## /backend/app/main.py
```python
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from routers.modernize import router as modernize_router

app = FastAPI(title="CodeRenew API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modernize_router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok"}
```

---

## /backend/app/routers/modernize.py
```python
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from starlette.responses import FileResponse
import uuid, os, shutil, json
from services.claude_service import modernize_code
from utils.diff_utils import make_diff

router = APIRouter()
TMP_DIR = "/tmp/codecrenew"
os.makedirs(TMP_DIR, exist_ok=True)

@router.post('/modernize-file')
async def modernize_file(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode('utf-8', errors='ignore')

    # Simple sync call — pour MVP on reste simple
    result = modernize_code(filename=file.filename, code=text)

    if not result:
        raise HTTPException(status_code=500, detail="Modernisation failed")

    # write outputs to temp folder
    task_id = str(uuid.uuid4())
    out_dir = os.path.join(TMP_DIR, task_id)
    os.makedirs(out_dir, exist_ok=True)

    modern_path = os.path.join(out_dir, file.filename)
    with open(modern_path, 'w', encoding='utf-8') as f:
        f.write(result['modernized'])

    diff_path = os.path.join(out_dir, f"{file.filename}.diff")
    with open(diff_path, 'w', encoding='utf-8') as f:
        f.write(result['diff'])

    meta_path = os.path.join(out_dir, 'meta.json')
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump({'explanation': result.get('explanation', '')}, f)

    return {"task_id": task_id, "download": f"/api/download/{task_id}"}

@router.get('/download/{task_id}')
async def download(task_id: str):
    out_dir = os.path.join(TMP_DIR, task_id)
    if not os.path.exists(out_dir):
        raise HTTPException(status_code=404, detail='Task not found')

    zip_path = out_dir + '.zip'
    shutil.make_archive(out_dir, 'zip', out_dir)
    return FileResponse(zip_path, filename=f"codecrenew_{task_id}.zip")
```

---

## /backend/app/services/claude_service.py
```python
import os

# Exemple d'implémentation simple — adapte selon le SDK/HTTP client Anthropic/Claude
# Ici on utilise des requêtes HTTP fictives pour illustrer la structure.

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
CLAUDE_API_URL = os.environ.get('CLAUDE_API_URL', 'https://api.anthropic.example/v1/complete')

PROMPT_TEMPLATE = '''Tu es un assistant expert en modernisation de code.

Tâches:
1) Modernise le code suivant en ciblant {target}.
2) Conserve le comportement fonctionnel.
3) Fourni une version finalisée du fichier, puis un diff git propre, puis une explication.

Réponds en JSON strict avec les champs: modernized, diff, explanation.

Code à moderniser:
```\n{code}\n```
'''

import requests, json


def modernize_code(filename: str, code: str, target: str = 'latest') -> dict:
    prompt = PROMPT_TEMPLATE.format(target=target, code=code)
    headers = {
        'Authorization': f'Bearer {CLAUDE_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'claude-3.5-sonnet',
        'messages': [
            {'role': 'system', 'content': 'You are an expert code modernization assistant.'},
            {'role': 'user', 'content': prompt}
        ],
        'max_tokens': 8000
    }

    r = requests.post(CLAUDE_API_URL, headers=headers, data=json.dumps(payload), timeout=120)
    if r.status_code != 200:
        print('Claude API error', r.status_code, r.text)
        return None

    data = r.json()
    # Le format dépendra de l'API réelle — ici on suppose data['completion'] contient le JSON demandé
    text = data.get('completion') or data.get('output') or data.get('text') or ''

    # Tentative simple de parse JSON si le modèle a renvoyé JSON
    try:
        parsed = json.loads(text)
        return parsed
    except Exception:
        # Si la réponse est mêlée, tenter d'extraire le JSON entre accolades
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            snippet = text[start:end+1]
            try:
                return json.loads(snippet)
            except Exception:
                return {'modernized': text, 'diff': '', 'explanation': ''}

    return {'modernized': text, 'diff': '', 'explanation': ''}
```

---

## /backend/app/utils/diff_utils.py
```python
import difflib

def make_diff(old: str, new: str) -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='old', tofile='new')
    return ''.join(diff)
```

---

## /backend/requirements.txt
```
fastapi
uvicorn[standard]
requests
python-multipart
starlette
```

---

## /backend/Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./app /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## /frontend/package.json
```json
{
  "name": "codecrenew-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev -p 3000",
    "build": "next build",
    "start": "next start -p 3000"
  },
  "dependencies": {
    "next": "13.4.0",
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "axios": "1.4.0"
  }
}
```

---

## /frontend/pages/index.jsx
```jsx
import Link from 'next/link'

export default function Home(){
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold">CodeRenew — Modernisation de code legacy (MVP)</h1>
      <p className="mt-4">Upload un fichier legacy pour obtenir une version modernisée.</p>
      <Link href="/upload"><a className="mt-4 inline-block">→ Commencer</a></Link>
    </main>
  )
}
```

---

## /frontend/pages/upload.jsx
```jsx
import { useState } from 'react'
import axios from 'axios'

export default function UploadPage(){
  const [file, setFile] = useState(null)
  const [task, setTask] = useState(null)

  const onFileChange = (e) => setFile(e.target.files[0])

  const onSubmit = async (e) =>{
    e.preventDefault()
    if(!file) return
    const fd = new FormData()
    fd.append('file', file)
    const res = await axios.post('http://localhost:8000/api/modernize-file', fd, {headers: {'Content-Type': 'multipart/form-data'}})
    setTask(res.data)
  }

  return (
    <main className="p-8">
      <h2 className="text-xl">Uploader un fichier</h2>
      <form onSubmit={onSubmit} className="mt-4">
        <input type="file" onChange={onFileChange} />
        <button className="ml-4">Envoyer</button>
      </form>

      {task && (
        <div className="mt-6">
          <p>Task ID: {task.task_id}</p>
          <a href={`http://localhost:8000${task.download}`}>Télécharger le ZIP</a>
        </div>
      )}
    </main>
  )
}
```

---

## /frontend/components/FileUploader.jsx
```jsx
export default function FileUploader({onFile}){
  return (
    <input type="file" onChange={(e)=> onFile(e.target.files[0])} />
  )
}
```

---

## /frontend/components/CodeViewer.jsx
```jsx
export default function CodeViewer({code}){
  return (
    <pre style={{whiteSpace: 'pre-wrap', background: '#0f172a', color:'#e6eef8', padding: '1rem', borderRadius: 8}}>
      {code}
    </pre>
  )
}
```

---

## /frontend/utils/api.js
```js
import axios from 'axios'
export const api = axios.create({ baseURL: 'http://localhost:8000/api' })
```

---

## README.md (extrait d'installation)
```
# Démarrage local (MVP)

## Backend
cd backend
pip install -r requirements.txt
export CLAUDE_API_KEY=sk-xxx
uvicorn main:app --reload --port 8000

## Frontend
cd frontend
npm install
npm run dev

Visit http://localhost:3000
```

---

## Notes et prochaines étapes recommandées
- **Sécuriser la clé** : ne jamais hardcoder la clé Claude. Utiliser vault/secret management.
- **Robustesse** : ajouter file size limits, scanning, async tasks (Celery/RQ) pour gros projets.
- **Tests** : écrire tests unitaires pour le parsing des réponses IA.
- **Cost control** : batcher ou chunker les appels Claude sur de gros fichiers.

---

Si tu veux, je peux :
- générer ces fichiers en tant qu'archive téléchargeable,
- convertir le backend pour utiliser un SDK officiel Claude (Anthropic),
- ajouter la gestion des ZIP/projets entiers,
- générer un Docker Compose prêt à l'emploi.

Dis-moi ce que tu veux que je fasse ensuite.
