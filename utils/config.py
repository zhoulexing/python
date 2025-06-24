import os
import json


class Config:
    def __init__(self, config_path = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "../assets/json/config.json")
            
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
        self.config = self.load_config()
        
    def save_config(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    config = Config()
    print(config.get("wxinfo"))