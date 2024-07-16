import json

from maitai_common.processes.websocket_listener_thread import WebsocketListenerThread
from maitai_gen.application import Application


class ConfigListenerThread(WebsocketListenerThread):
    def __init__(self, config, path, type, key=None):
        super(ConfigListenerThread, self).__init__(path, type, key)
        self.config = config

    def on_message(self, ws, message):
        event = json.loads(message)
        if event.get("event_type") == 'APPLICATION_CONFIG_CHANGE':
            application_json = event.get("event_data")
            if application_json:
                try:
                    application = Application().from_dict(application_json)
                    self.config.store_application_metadata([application])
                except:
                    self.config.refresh_applications()
            else:
                self.config.refresh_applications()
