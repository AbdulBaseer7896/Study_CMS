# cloudinary_utils.py

import cloudinary
import cloudinary.uploader
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True  # always use https
)


# ── Upload ───────────────────────────────────────────────────────────────────
def upload_file(file_path: str, folder: str = "uploads") -> dict:
    """
    Upload an image or PDF to Cloudinary.

    Args:
        file_path : Local path to the file (image or PDF)
        folder    : Cloudinary folder to store it in

    Returns:
        dict with keys:
            - url          → direct viewable URL
            - public_id    → Cloudinary public ID
            - resource_type→ 'image' or 'raw'
            - format       → file extension
            - bytes        → file size
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = path.suffix.lower()

    # PDFs must use resource_type="image" so Cloudinary renders them
    # (raw uploads work too but won't generate a preview URL)
    if ext == ".pdf":
        resource_type = "image"   # enables PDF page rendering
        extra = {"format": "pdf"}
    elif ext in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".tiff"}:
        resource_type = "image"
        extra = {}
    else:
        # fallback – store as raw (no preview)
        resource_type = "raw"
        extra = {}

    result = cloudinary.uploader.upload(
        str(path),
        folder=folder,
        resource_type=resource_type,
        use_filename=True,       # keep the original filename
        unique_filename=True,    # avoid collisions
        overwrite=False,
        **extra
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "resource_type": result["resource_type"],
        "format": result.get("format", ext.lstrip(".")),
        "bytes": result["bytes"],
    }


# ── View helpers ─────────────────────────────────────────────────────────────
def get_image_url(public_id: str, **transformations) -> str:
    """
    Build a viewable URL for an uploaded image.
    Pass any Cloudinary transformation kwargs, e.g.:
        get_image_url("uploads/photo", width=800, crop="scale")
    """
    from cloudinary.utils import cloudinary_url
    url, _ = cloudinary_url(public_id, **transformations)
    return url


def get_pdf_url(public_id: str, page: int = 1, as_image: bool = False) -> str:
    """
    Build a viewable URL for an uploaded PDF.

    Args:
        public_id : Cloudinary public ID of the PDF
        page      : Which page to preview (1-indexed), used when as_image=True
        as_image  : If True, returns a PNG preview of that page instead of the PDF

    Returns:
        A secure URL string
    """
    from cloudinary.utils import cloudinary_url

    if as_image:
        # renders the PDF page as a PNG – great for thumbnails/previews
        url, _ = cloudinary_url(
            public_id,
            format="png",
            page=page,
            resource_type="image",
        )
    else:
        # direct PDF download/view URL
        url, _ = cloudinary_url(public_id, resource_type="image", format="pdf")

    return url


# ── Upload an image ──────────────────────────────────────────────────────────
result = upload_file(
    file_path=r"D:\Bitnext\Study_CMS\Backend\images\domicile_pic.webp",
    folder="study_cms/images"   # this is the Cloudinary folder name, not a local path
)
print(result["url"])

# ── Upload a PDF ─────────────────────────────────────────────────────────────
result = upload_file(
    file_path=r"D:\Bitnext\Study_CMS\Backend\images\MY Resume MDR Pharmacist 09-2023 (1).pdf",
    folder="study_cms/pdfs"     # Cloudinary folder name
)
print(result["url"])

# ── View image with resize transform ─────────────────────────────────────────
url = get_image_url(result["public_id"], width=600, crop="scale")
print(url)

# ── View PDF as page-1 PNG preview ───────────────────────────────────────────
preview = get_pdf_url(result["public_id"], page=1, as_image=True)
print(preview)

# ── Direct PDF URL ────────────────────────────────────────────────────────────
pdf_url = get_pdf_url(result["public_id"])
print(pdf_url)