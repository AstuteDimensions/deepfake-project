import base64
import requests


import os

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

def upload_image(image_path):
    """
    Upload an image to ImgBB and return its public URL.
    """

    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read())

    url = "https://api.imgbb.com/1/upload"

    payload = {
        "key": IMGBB_API_KEY,
        "image": encoded_image
    }

    response = requests.post(url, payload)

    if response.status_code == 200:
        data = response.json()
        return data["data"]["url"]
    else:
        print(response.text)
        return None


if __name__ == "__main__":
    path = input("Image path: ")

    image_url = upload_image(path)

    if image_url:
        print("\nUploaded Successfully!")
        print(image_url)
    else:
        print("Upload Failed.")