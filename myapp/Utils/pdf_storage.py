# myapp/Utils/pdf_storage.py
# 
# Set this as DEFAULT_FILE_STORAGE in settings.py:
#   DEFAULT_FILE_STORAGE = 'myapp.Utils.pdf_storage.PDFAwareCloudinaryStorage'
#
from cloudinary_storage.storage import MediaCloudinaryStorage


class PDFAwareCloudinaryStorage(MediaCloudinaryStorage):
    """
    Drop-in replacement for MediaCloudinaryStorage.
    
    Cloudinary strips file extensions from public_id for image resource type.
    This class detects PDF uploads and:
      1. Uploads them as resource_type='raw' (preserves extension on Cloudinary)
      2. Ensures the path saved to the DB ends with '.pdf'
    
    All non-PDF files behave exactly as before.
    """

    def _get_resource_type(self, name):
        if name.lower().endswith('.pdf'):
            return 'raw'
        return super()._get_resource_type(name)

    def _save(self, name, content):
        public_id = super()._save(name, content)

        # Safety net: if Cloudinary still dropped .pdf, add it back
        if name.lower().endswith('.pdf') and not public_id.lower().endswith('.pdf'):
            public_id = public_id + '.pdf'

        return public_id