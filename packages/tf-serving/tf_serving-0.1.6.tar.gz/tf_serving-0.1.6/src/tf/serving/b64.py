import base64

def encode64(img: bytes) -> str:
  """Encode a JPG/PGN/WEBP image as URL-safe base64 encoded UTF-8 string (as TensorFlow Serving expects)"""
  return base64.urlsafe_b64encode(img).decode('utf-8')