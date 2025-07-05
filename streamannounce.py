import obspython as obs
import requests
import datetime

WEBHOOK_URL = None
ANNOUNCE_MESSAGE = None
RECONNECT_ANNOUNCE_TIMEOUT = None

last_start_time = None

def send_discord_message(content):
    data = {"content": content}
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code != 204:
            print(f"Failed to send message: {response.status_code}")
    except Exception as e:
        print(f"Error sending webhook: {e}")

def on_event(event):
    global last_start_time
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED:
        if last_start_time is None or datetime.datetime.now() >= last_start_time + datetime.timedelta(minutes = RECONNECT_ANNOUNCE_TIMEOUT):
            if ANNOUNCE_MESSAGE is None:
                send_discord_message("Please configure the announcement message")
            else:
                send_discord_message(ANNOUNCE_MESSAGE)
            last_start_time = datetime.datetime.now()

def script_load(settings):
    obs.obs_frontend_add_event_callback(on_event)

def script_update(settings):
    global WEBHOOK_URL, ANNOUNCE_MESSAGE, RECONNECT_ANNOUNCE_TIMEOUT
    WEBHOOK_URL = obs.obs_data_get_string(settings, "webhook_url")
    ANNOUNCE_MESSAGE = obs.obs_data_get_string(settings, "start_message")
    RECONNECT_ANNOUNCE_TIMEOUT = obs.obs_data_get_int(settings, "reconnect_timeout")

# Define script properties (UI fields)
def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "webhook_url", "Discord Webhook URL", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "start_message", "Start Streaming Message", obs.OBS_TEXT_MULTILINE)
    obs.obs_properties_add_int(props, "reconnect_timeout", "Re-announcement Delay (min)", 0, 60, 1)
    return props
