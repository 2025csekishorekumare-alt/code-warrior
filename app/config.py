import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ap_audit.db")
OCR_ENABLED = os.getenv("OCR_ENABLED", "true").lower() == "true"
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "15"))
