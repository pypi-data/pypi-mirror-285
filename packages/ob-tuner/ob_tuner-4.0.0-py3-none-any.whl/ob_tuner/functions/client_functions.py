from openbrain.orm.model_client import Client
from ob_tuner.util import logger
import gradio as gr

def save_client_details(email, leadmo_api_key, leadmo_location_id, lls_api_key):
    """Update the client with the latest values from the database"""
    try:
        client = Client(email=email, leadmo_api_key=leadmo_api_key, leadmo_location_id=leadmo_location_id, lls_api_key=lls_api_key)
        client.save()
        gr.Info(f"Successfully updated ")
    except Exception as e:
        gr.Error(f"Failed to update the user: {e}")

def load_client_details(email):
    """Load the client details from the database"""
    try:
        _client = Client.get(email=email)
    except Exception as e:
        gr.Warning(f"User not found, creating user...")
        _client = Client(email=email, leadmo_api_key="", leadmo_location_id=None, lls_api_key=None)
        _client.save()

        # gr.Error(f"Failed to load the user: {e}")

    # email = client.email
    leadmo_api_key = _client.leadmo_api_key
    leadmo_location_id = _client.leadmo_location_id
    lls_api_key = _client.lls_api_key
    return [leadmo_api_key, leadmo_location_id, lls_api_key]
