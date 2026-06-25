# PixelDNA

PixelDNA is a Flask-based image tamper detection and watermarking application. It provides a simple web interface for user registration, image upload, watermark embedding, and tampering verification using perceptual hashing, ELA, and digital watermark extraction.

## Features

- User registration and login with Flask-Login
- Image upload and watermark embedding using DWT-DCT watermarking
- Tamper verification with:
  - perceptual hash comparison
  - error level analysis (ELA)
  - watermark extraction verification
- Audit logging of user actions
- Stores users and watermark metadata in SQLite (`database.db`)

## Project Structure

- `app.py` - main Flask application and routes
- `auth.py` - user authentication, registration, and watermark metadata storage
- `audit.py` - audit log management
- `modules/embedder.py` - watermark embedding logic
- `modules/extracter.py` - watermark extraction logic
- `modules/detector.py` - tamper detection flow combining hashing, ELA, and watermark verification
- `modules/ela.py` - error level analysis helper
- `modules/hasher.py` - perceptual hash comparison helper
- `templates/` - HTML templates for the app
- `static/` - static assets and generated output folders
- `uploads/` - temporary uploaded image storage

## Requirements

This project is built for Python and uses a virtual environment located in `pixeldna_env`.

Required packages include:

- Flask
- Flask-Login
- Werkzeug
- OpenCV (`cv2`)
- `imwatermark`
- `imagehash`
- `numpy`

If you prefer using the provided virtual environment, activate it first.

## Setup

1. Open a terminal in the project root:

```powershell
cd C:\Users\sketh\OneDrive\Desktop\PixelDNA
.\pixeldna_env\Scripts\Activate.ps1
```

2. Install dependencies if not already available:

```powershell
pip install flask flask-login opencv-python imwatermark imagehash
```

3. Ensure the database and folders are created by running the app once:

```powershell
python app.py
```

The app will automatically initialize `database.db` and create `uploads/`, `static/watermarked/`, and `static/verify_runs/`.

## Running the App

Start the Flask server:

```powershell
python app.py
```

Then open a browser at:

```
http://127.0.0.1:5000/
```

## Usage

1. Register a new account.
2. Log in.
3. Upload an image on the dashboard to embed a watermark.
4. Use the verification page to upload an original and suspect image to check for tampering.

## Notes

- Watermarked images are saved in `static/watermarked/`.
- Verification runs store temporary files in `static/verify_runs/`.
- The stored watermark metadata links users to images and watermark text values.

## License

This project is provided as-is for experimentation and learning.
