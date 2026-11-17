import base64
from pathlib import Path
from uuid import uuid4
from flask import current_app, url_for

def save_as_image(image_data: str, used_for:str="Personas" ) -> str:
    """
    Convert a Base64 JPEG image into a file.

    Returns the relative path to the saved image.
    """

    # Separate the metadata from the actual image data
    if not "," in image_data:
        raise ValueError("Expected a Base64-encoded JPEG image")

    header, encoded_image = image_data.split(",", 1)

    if header != "data:image/jpeg;base64":
        raise ValueError("Expected a Base64-encoded JPEG image")

    # Decode Base64 into binary image data
    image_bytes = base64.b64decode(
        encoded_image,
        validate=True
    )
    if used_for == "Adventures":
        location = "adventures"
    else:
        location = "personas"
    # Determine the destination folder
    # static_folder = (
    #     Path(__file__).resolve().parent
    #     / ".."
    #     / ".."
    #     / "static"
    #     / "images"
    #     / location
    # )
    static_root = current_app.static_folder
    if static_root is None:
        raise RuntimeError("This Flask app has no static folder configured")
    static_folder = Path(static_root).resolve() / "images" / location
    static_folder.mkdir(parents=True, exist_ok=True)

    # Generate a unique filename
    filename = f"{uuid4().hex}.jpg"

    # Write the binary image to disk
    image_path = static_folder / filename
    image_path.write_bytes(image_bytes)
    file_path = str(image_path)
    # Return the path relative to Flask's static folder
    file_path=url_for(
        "static",
        filename=f"images/{location}/{filename}")
    return file_path