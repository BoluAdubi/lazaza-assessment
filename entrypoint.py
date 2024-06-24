from src.clients import queue_client
import os
import requests
import base64
from dotenv import load_dotenv
from src.clients import image_service_client
from dotenv import load_dotenv

#
# handles only logic involved with upscaling a single image
#
def process_image(message) -> None:
    load_dotenv()
    img_service = image_service_client.ImageServiceClient()

    # upscale image using web service
    request_obj = {
        "access_token": os.getenv("api_access_token"),
        "new_height": message["height"],
        "new_width": message["width"],
        "base64_image": message["image_data"]
    }
    
    service_response = requests.post(os.getenv("image_upscaler_url"), json = request_obj).json()

    try:
        # post upscaled image to image service
        service_response_bytes = base64.b64decode(service_response["base64_image"])        
        img_service.post_image(service_response_bytes)
        print("Log: image successfully upscaled and submitted to image service")
    except:
        print("Error: " + service_response["message"])      

#
# process all messages in queue
#
def _process_upscale_requests() -> None:
    q_client = queue_client.QueueClient()

    # process images while queue is not empty
    while True:
        message = q_client.pop()
        if not message:
            break

        process_image(message)


_process_upscale_requests()