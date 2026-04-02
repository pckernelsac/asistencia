# -*- coding: utf-8 -*-
"""
Almacenamiento de archivos: disco local (dev) o Supabase Storage (produccion).
"""
from __future__ import annotations

import os
from io import BytesIO
from typing import Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
BUCKET = "photos"


def _use_supabase() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def _headers() -> dict:
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }


def _ensure_bucket():
    """Crea el bucket si no existe (ignora error si ya existe)."""
    import requests
    try:
        requests.post(
            f"{SUPABASE_URL}/storage/v1/bucket",
            headers={**_headers(), "Content-Type": "application/json"},
            json={"id": BUCKET, "name": BUCKET, "public": True},
            timeout=10,
        )
    except Exception:
        pass


def upload(file_data, filename: str, content_type: str = "image/jpeg") -> Optional[str]:
    """Sube archivo. Retorna la URL publica o None si falla."""
    if _use_supabase():
        import requests
        _ensure_bucket()
        if isinstance(file_data, BytesIO):
            data = file_data.read()
            file_data.seek(0)
        elif hasattr(file_data, "read"):
            data = file_data.read()
            file_data.seek(0)
        else:
            data = file_data

        resp = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}",
            headers={**_headers(), "Content-Type": content_type, "x-upsert": "true"},
            data=data,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
        return None
    else:
        # Local: guardar en UPLOAD_FOLDER
        from flask import current_app
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if hasattr(file_data, "save"):
            file_data.save(path)
        elif hasattr(file_data, "read"):
            with open(path, "wb") as f:
                f.write(file_data.read())
            file_data.seek(0)
        return filename


def delete(filename: str) -> bool:
    """Elimina archivo. Retorna True si ok."""
    if _use_supabase():
        import requests
        resp = requests.delete(
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}",
            headers=_headers(),
            timeout=10,
        )
        return resp.status_code in (200, 204)
    else:
        from flask import current_app
        path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False


def public_url(filename: str) -> Optional[str]:
    """Retorna URL publica del archivo."""
    if not filename:
        return None
    if _use_supabase():
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
    else:
        from flask import url_for
        return url_for("static", filename=f"uploads/{filename}")
