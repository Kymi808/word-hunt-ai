"""
Screen capture and OCR for reading the Word Hunt board.
Uses macOS screenshot + Tesseract OCR or Vision framework.
"""

import subprocess
import tempfile
import os

try:
    import cv2
    import numpy as np

    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pytesseract

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def capture_screen_region(x: int, y: int, w: int, h: int, output_path: str | None = None) -> str:
    """
    Capture a region of the screen using macOS screencapture.
    Returns the path to the saved screenshot.
    """
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)

    subprocess.run(
        ["screencapture", "-R", f"{x},{y},{w},{h}", "-x", output_path],
        check=True,
    )
    return output_path


def capture_full_screen(output_path: str | None = None) -> str:
    """Capture the full screen."""
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)

    subprocess.run(["screencapture", "-x", output_path], check=True)
    return output_path


def ocr_board_from_image(image_path: str, grid_region: tuple[int, int, int, int] | None = None) -> str:
    """
    Extract 16 letters from a screenshot of the Word Hunt board.

    grid_region: (x, y, w, h) of the 4x4 grid within the image.
    If None, attempts to detect the grid automatically.

    Returns a 16-character string of the board letters.
    """
    if not CV2_AVAILABLE:
        raise ImportError("opencv-python is required for OCR. Install with: pip install opencv-python")
    if not TESSERACT_AVAILABLE:
        raise ImportError("pytesseract is required for OCR. Install with: pip install pytesseract")

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Could not load image: {image_path}")

    if grid_region:
        x, y, w, h = grid_region
        img = img[y : y + h, x : x + w]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    cell_h, cell_w = thresh.shape[0] // 4, thresh.shape[1] // 4
    letters = []

    for row in range(4):
        for col in range(4):
            y1, y2 = row * cell_h, (row + 1) * cell_h
            x1, x2 = col * cell_w, (col + 1) * cell_w

            # Add padding to avoid cell borders
            pad = int(min(cell_h, cell_w) * 0.15)
            cell = thresh[y1 + pad : y2 - pad, x1 + pad : x2 - pad]

            # Resize for better OCR accuracy
            cell = cv2.resize(cell, (100, 100), interpolation=cv2.INTER_LINEAR)

            text = pytesseract.image_to_string(
                cell,
                config="--psm 10 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            )
            letter = text.strip().upper()
            if len(letter) == 1 and letter.isalpha():
                letters.append(letter)
            else:
                letters.append("?")

    result = "".join(letters)
    if "?" in result:
        print(f"Warning: OCR detected uncertain letters: {result}")
        print("You may need to manually correct letters marked with '?'")
    return result


def ocr_with_apple_vision(image_path: str) -> str:
    """
    Use macOS Vision framework via a Swift script for better OCR accuracy.
    Falls back gracefully if not available.
    """
    swift_code = """
    import Foundation
    import Vision
    import AppKit

    let imagePath = CommandLine.arguments[1]
    guard let image = NSImage(contentsOfFile: imagePath),
          let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        print("ERROR: Could not load image")
        exit(1)
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = false

    let handler = VNImageRequestHandler(cgImage: cgImage)
    try handler.perform([request])

    guard let observations = request.results else {
        print("ERROR: No results")
        exit(1)
    }

    for observation in observations {
        if let candidate = observation.topCandidates(1).first {
            print(candidate.string)
        }
    }
    """
    fd, script_path = tempfile.mkstemp(suffix=".swift")
    os.close(fd)
    try:
        with open(script_path, "w") as f:
            f.write(swift_code)
        result = subprocess.run(
            ["swift", script_path, image_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""
    finally:
        os.unlink(script_path)
