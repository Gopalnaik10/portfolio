import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from backend.config import Config

class UploadService:
    @staticmethod
    def _init_cloudinary():
        """Initializes Cloudinary configuration dynamically from environment."""
        if Config.is_cloudinary_configured:
            import cloudinary
            cloudinary.config(
                cloud_name=Config.CLOUDINARY_CLOUD_NAME,
                api_key=Config.CLOUDINARY_API_KEY,
                api_secret=Config.CLOUDINARY_API_SECRET,
                secure=True
            )

    @staticmethod
    def save_file(file: FileStorage, subfolder: str, allowed_extensions: set) -> tuple[bool, str]:
        """
        Saves uploaded file into uploads/<subfolder> after strict validation (local fallback).
        Returns (success: bool, file_path_or_error: str)
        """
        if not file or not file.filename:
            return False, "No file selected for upload"

        original_filename = secure_filename(file.filename)
        if '.' not in original_filename:
            return False, "Invalid file format: missing extension"

        ext = original_filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return False, f"Unsupported file type .{ext}. Allowed: {', '.join(allowed_extensions)}"

        # Generate unique non-colliding filename
        unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

        target_dir = Config.UPLOAD_FOLDER / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)

        destination = target_dir / unique_name
        file.save(str(destination))

        relative_url = f"/uploads/{subfolder}/{unique_name}"
        return True, relative_url

    @staticmethod
    def upload_to_cloudinary(file: FileStorage, folder: str, allowed_extensions: set) -> tuple[bool, str]:
        """
        Uploads image file directly to Cloudinary folder.
        Returns (success: bool, secure_url_or_error: str)
        """
        if not file or not file.filename:
            return False, "No file selected for upload"

        original_filename = secure_filename(file.filename)
        if '.' not in original_filename:
            return False, "Invalid file format: missing extension"

        ext = original_filename.rsplit('.', 1)[1].lower()
        if ext not in allowed_extensions:
            return False, f"Unsupported file type .{ext}. Allowed: {', '.join(allowed_extensions)}"

        UploadService._init_cloudinary()
        import cloudinary.uploader

        try:
            # Upload stream directly to Cloudinary without creating temporary local files
            file.stream.seek(0)
            upload_result = cloudinary.uploader.upload(
                file.stream,
                folder=folder,
                resource_type="image",
                use_filename=False,
                unique_filename=True,
                overwrite=False
            )
            secure_url = upload_result.get('secure_url') or upload_result.get('url')
            if not secure_url:
                return False, "Failed to obtain secure URL from Cloudinary"
            return True, secure_url
        except Exception:
            # Return sanitized error message without exposing credentials or internal stack
            return False, "Image upload failed. Please verify your connection and try again."

    @staticmethod
    def save_profile_image(file: FileStorage) -> tuple[bool, str]:
        """Uploads profile image to Cloudinary (portfolio/profile) or falls back to local disk."""
        if Config.is_cloudinary_configured:
            return UploadService.upload_to_cloudinary(file, 'portfolio/profile', Config.ALLOWED_IMAGE_EXTENSIONS)
        return UploadService.save_file(file, 'profile', Config.ALLOWED_IMAGE_EXTENSIONS)

    @staticmethod
    def save_project_image(file: FileStorage) -> tuple[bool, str]:
        """Uploads project screenshot to Cloudinary (portfolio/projects) or falls back to local disk."""
        if Config.is_cloudinary_configured:
            return UploadService.upload_to_cloudinary(file, 'portfolio/projects', Config.ALLOWED_IMAGE_EXTENSIONS)
        return UploadService.save_file(file, 'projects', Config.ALLOWED_IMAGE_EXTENSIONS)

    @staticmethod
    def delete_cloudinary_asset(asset_url: str) -> bool:
        """
        Safely deletes an existing Cloudinary asset if it belongs to this portfolio.
        Guarantees bundled local assets and external URLs are never deleted.
        Supports images and PDF documents.
        """
        if not asset_url or not Config.is_cloudinary_configured:
            return False
        if not (asset_url.startswith("https://res.cloudinary.com/") or asset_url.startswith("http://res.cloudinary.com/")):
            return False

        # Only delete assets in our portfolio folders (portfolio/profile, portfolio/projects, portfolio/resume)
        if "/portfolio/" not in asset_url:
            return False

        try:
            UploadService._init_cloudinary()
            import cloudinary.uploader

            parts = asset_url.split("/portfolio/")
            if len(parts) == 2:
                sub_path = parts[1]
                public_id_with_ext = "portfolio/" + sub_path
                res_type = "raw" if "/raw/upload/" in asset_url else "image"
                public_id = public_id_with_ext if res_type == "raw" else public_id_with_ext.rsplit(".", 1)[0]

                # Attempt deletion with determined resource type, and fallback if needed
                res = cloudinary.uploader.destroy(public_id, resource_type=res_type, invalidate=True)
                if res.get('result') != 'ok':
                    # Fallback attempt with opposite resource type (image vs raw)
                    alt_type = "image" if res_type == "raw" else "raw"
                    alt_id = public_id_with_ext.rsplit(".", 1)[0] if alt_type == "image" else public_id_with_ext
                    cloudinary.uploader.destroy(alt_id, resource_type=alt_type, invalidate=True)
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def save_resume_pdf(file: FileStorage) -> tuple[bool, str, str, int]:
        """
        Saves PDF resume to Cloudinary (portfolio/resume) or local disk.
        Returns (success: bool, url_or_path: str, original_name: str, file_size: int)
        """
        if not file or not file.filename:
            return False, "No resume file selected", "", 0

        original_name = secure_filename(file.filename)
        ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
        if ext not in Config.ALLOWED_DOC_EXTENSIONS:
            return False, "Only PDF documents are accepted for resume upload", "", 0

        # Calculate file size from stream
        file.stream.seek(0, os.SEEK_END)
        file_size = file.stream.tell()
        file.stream.seek(0)

        # Upload to Cloudinary if configured
        if Config.is_cloudinary_configured:
            UploadService._init_cloudinary()
            import cloudinary.uploader
            try:
                upload_result = cloudinary.uploader.upload(
                    file.stream,
                    folder="portfolio/resume",
                    resource_type="auto",
                    use_filename=False,
                    unique_filename=True,
                    overwrite=False
                )
                secure_url = upload_result.get('secure_url') or upload_result.get('url')
                if not secure_url:
                    return False, "Failed to obtain secure URL from Cloudinary", "", 0
                return True, secure_url, original_name, file_size
            except Exception:
                return False, "Resume upload failed. Please verify your connection and try again.", "", 0

        # Fallback to local storage (e.g. local dev without Cloudinary)
        unique_name = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.pdf"
        target_dir = Config.UPLOAD_FOLDER / 'resume'
        target_dir.mkdir(parents=True, exist_ok=True)

        destination = target_dir / unique_name
        file.save(str(destination))
        actual_size = os.path.getsize(str(destination))

        relative_url = f"/uploads/resume/{unique_name}"
        return True, relative_url, original_name, actual_size
