import os
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from backend.config import Config

class UploadService:
    @staticmethod
    def save_file(file: FileStorage, subfolder: str, allowed_extensions: set) -> tuple[bool, str]:
        """
        Saves uploaded file into uploads/<subfolder> after strict validation.
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
    def save_profile_image(file: FileStorage) -> tuple[bool, str]:
        return UploadService.save_file(file, 'profile', Config.ALLOWED_IMAGE_EXTENSIONS)

    @staticmethod
    def save_project_image(file: FileStorage) -> tuple[bool, str]:
        return UploadService.save_file(file, 'projects', Config.ALLOWED_IMAGE_EXTENSIONS)

    @staticmethod
    def save_resume_pdf(file: FileStorage) -> tuple[bool, str, str, int]:
        """
        Saves PDF resume and returns (success, relative_url, original_name, size)
        """
        if not file or not file.filename:
            return False, "No resume file selected", "", 0

        original_name = secure_filename(file.filename)
        ext = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else ''
        if ext not in Config.ALLOWED_DOC_EXTENSIONS:
            return False, "Only PDF documents are accepted for resume upload", "", 0

        unique_name = f"resume_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}.pdf"
        target_dir = Config.UPLOAD_FOLDER / 'resume'
        target_dir.mkdir(parents=True, exist_ok=True)
        
        destination = target_dir / unique_name
        file.save(str(destination))
        file_size = os.path.getsize(str(destination))

        relative_url = f"/uploads/resume/{unique_name}"
        return True, relative_url, original_name, file_size
