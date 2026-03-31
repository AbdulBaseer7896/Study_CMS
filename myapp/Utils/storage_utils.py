# # myapp/Utils/storage_utils.py
# import os
# from django.conf import settings

# # ============================================================
# # STORAGE CONFIGURATION

# # myapp/Utils/storage_utils.py

# # Development
# # STORAGE_BACKEND = 'local'

# # Staging / launch
# STORAGE_BACKEND = 'cloudinary'

# # Production
# # STORAGE_BACKEND = 's3'


# def get_storage():
#     """
#     Returns the correct storage instance based on STORAGE_BACKEND.
#     Used in model FileField/ImageField as: storage=get_storage()
#     """
#     if STORAGE_BACKEND == 'cloudinary':
#         from cloudinary_storage.storage import MediaCloudinaryStorage
#         return MediaCloudinaryStorage()

#     elif STORAGE_BACKEND == 's3':
#         from storages.backends.s3boto3 import S3Boto3Storage
#         return S3Boto3Storage()

#     else:
#         # Default: local storage
#         from django.core.files.storage import FileSystemStorage
#         return FileSystemStorage(location=settings.MEDIA_ROOT)


# def upload_image(file, folder='general'):
#     """
#     Universal image upload function.
#     Works with local, Cloudinary, or S3 — no code change needed.

#     Usage:
#         url = upload_image(request.FILES['profile_pic'], folder='profile_pics')

#     Returns:
#         str: public URL of the uploaded image
#     """
#     print("This is the 111")
#     storage = get_storage()

#     # Build file path with folder
#     filename = file.name
#     print("this is the filename: ", filename)
#     filepath = f"{folder}/{filename}"

#     # Save the file
#     saved_path = storage.save(filepath, file)

#     # Return full URL
#     url = storage.url(saved_path)
#     return url


# def delete_image(file_path):
#     """
#     Universal image delete function.

#     Usage:
#         delete_image(user.profile_picture.name)
#     """
#     if not file_path:
#         return False

#     storage = get_storage()

#     try:
#         if storage.exists(file_path):
#             storage.delete(file_path)
#             return True
#         return False
#     except Exception as e:
#         print(f"Error deleting file: {e}")
#         return False


# def get_image_url(file_path):
#     """
#     Get public URL of any stored image.

#     Usage:
#         url = get_image_url(user.profile_picture.name)
#     """
#     if not file_path:
#         return None

#     storage = get_storage()
#     return storage.url(file_path)



# myapp/Utils/storage_utils.py
# No changes needed here - this file is not used for FileField uploads.
# DEFAULT_FILE_STORAGE in settings.py controls all FileField uploads.
import os
from django.conf import settings

STORAGE_BACKEND = 'cloudinary'


def get_storage():
    if STORAGE_BACKEND == 'cloudinary':
        from cloudinary_storage.storage import MediaCloudinaryStorage
        return MediaCloudinaryStorage()
    elif STORAGE_BACKEND == 's3':
        from storages.backends.s3boto3 import S3Boto3Storage
        return S3Boto3Storage()
    else:
        from django.core.files.storage import FileSystemStorage
        return FileSystemStorage(location=settings.MEDIA_ROOT)


def upload_image(file, folder='general'):
    storage = get_storage()
    filename = file.name
    filepath = f"{folder}/{filename}"
    saved_path = storage.save(filepath, file)
    url = storage.url(saved_path)
    return url


def delete_image(file_path):
    if not file_path:
        return False
    storage = get_storage()
    try:
        if storage.exists(file_path):
            storage.delete(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_image_url(file_path):
    if not file_path:
        return None
    storage = get_storage()
    return storage.url(file_path)