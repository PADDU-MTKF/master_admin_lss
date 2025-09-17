import io
import os
import ast
import json
import datetime
import secrets
from django import forms
from django.core.cache import cache
from django.http import HttpResponse
from django.core.files.uploadedfile import InMemoryUploadedFile
from . import data as db

# Note: Pillow (PIL) is imported lazily inside compress_image to avoid import-time errors.

def generate_token():
    """Generate a secure random token."""
    return secrets.token_urlsafe(32)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, datetime.datetime):
            return str(z)
        return super().default(z)


def update_cache(cache_key, db_id, doc_id, queries=None):
    """Update the cache with a new document."""
    document, _ = db.getDocument(db_id, doc_id, queries)
    cache.set(cache_key, document, timeout=None)
    return document


def refresh_cache():
    """Refresh each cache entry (extend as needed)."""
    # Example usage (commented):
    # update_cache("address_data", os.getenv("DB_ID"), os.getenv("ADDRESS_ID"))
    return HttpResponse("Cache refreshed successfully.")


def updateSite():
    try:
        refresh_cache()
        print("Cache refreshed")
    except Exception as e:
        print(f"Failed to update site cache: {e}")


def clean_form_data(form):
    """Process form fields and return cleaned dictionary."""
    new_det = {}
    for field_name, field_value in form.cleaned_data.items():
        field_name = field_name.replace(" ", "_")

        # Decimal Field
        if isinstance(form.fields[field_name], forms.DecimalField):
            new_det[field_name] = float(field_value) if field_value not in ("", None) else 0.0

        # DateTime Field
        elif isinstance(form.fields[field_name], forms.DateTimeField):
            try:
                raw = json.dumps(field_value, cls=DateTimeEncoder).strip('"')
                new_det[field_name] = raw if raw != "null" else None
            except Exception:
                new_det[field_name] = None

        # Default
        else:
            new_det[field_name] = field_value or None

    return new_det


'''

# -----------------------
# Image helpers (restored from your original commented code)
# -----------------------
def compress_image(uploaded_file, quality=60, output_format='JPEG'):
    """
    Compress an uploaded image (UploadedFile) and return an InMemoryUploadedFile.
    - lazy-imports PIL (Pillow). Install pillow if missing: pip install pillow
    - converts to RGB to avoid some format issues
    - returns InMemoryUploadedFile whose .file is a BytesIO ready for storage upload
    """
    try:
        from PIL import Image
    except ImportError:
        raise RuntimeError("Pillow is required for image compression. Install with `pip install pillow`")

    # Reset pointer and open
    uploaded_file.seek(0)
    img = Image.open(uploaded_file)

    # Convert to RGB for JPEG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    img_io = io.BytesIO()
    img.save(img_io, format=output_format, quality=quality, optimize=True)
    img_io.seek(0)
    size = img_io.getbuffer().nbytes

    field_name = getattr(uploaded_file, "field_name", None)
    name = getattr(uploaded_file, "name", "upload.jpg")

    compressed = InMemoryUploadedFile(
        img_io, field_name, name,
        f"image/{output_format.lower()}", size, None
    )
    return compressed


def remove_old_img(data, field_name, storage_id=None):
    """
    Remove an old image given the stored data (dict or stringified dict) and field_name.
    Returns True on success, False otherwise.
    """
    try:
        # allow a string representation (legacy) or a dict
        if isinstance(data, str):
            try:
                data = ast.literal_eval(data)
            except Exception:
                # if data is a JSON string
                try:
                    data = json.loads(data)
                except Exception:
                    return False

        if not isinstance(data, dict):
            return False

        old_img_url = data.get(field_name)
        if not old_img_url:
            return False

        storage_id = storage_id or os.getenv('STORAGE_ID')
        if not storage_id:
            return False

        r = db.deleteStorage(storage_id, old_img_url)
        return bool(r)
    except Exception:
        return False


'''