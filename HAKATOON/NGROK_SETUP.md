# Configuración de ngrok para HAKATOON

Esta configuración permite exponer el frontend y el backend del proyecto `HAKATOON` a través de túneles accesibles desde Internet.

## Pasos

1. Instala `ngrok` y crea una cuenta en https://ngrok.com.
2. Asegúrate de haber agregado tu token en `HAKATOON/ngrok.yml`. El archivo ya contiene el `authtoken`.
3. Arranca tu aplicación localmente:
   - Frontend Vite: `npm run dev` dentro de `HAKATOON/frontend` (por defecto en `http://localhost:5173`)
   - Backend FastAPI: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` dentro de `HAKATOON/backend`
4. Inicia ngrok desde la carpeta `HAKATOON`:
   ```powershell
   cd HAKATOON
   ngrok start --config ngrok.yml --all
   ```
   O usa el script de ayuda:
   ```powershell
   .\start-ngrok.ps1
   ```
5. ngrok mostrará URLs públicos para `frontend` y `backend`.

## Túneles configurados

- `frontend` → `localhost:5173`
- `backend` → `localhost:8000`

## Uso recomendado

- Accede al frontend con la URL pública que genere ngrok.
- El frontend Vite ya está configurado para transparentemente reenviar `/api` al backend local.
- Si abres el frontend remoto, las llamadas a `/api/...` funcionarán a través del proxy de Vite.

## Atajos útiles

- Para arrancar solo el frontend: `ngrok http 5173`
- Para arrancar solo el backend: `ngrok http 8000`

## Consejos

- Si necesitas una URL HTTPS, utiliza la dirección que ngrok provea; el túnel seguirá enviando tráfico a tu `http://localhost:5173` y `http://localhost:8000`.
