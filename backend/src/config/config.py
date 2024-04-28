import configparser


class Config:
    __CONFIG_FILE_NAME = 'config/config.ini'

    @staticmethod
    def get_config_item(section_name: str, item_name: str) -> any:
        cfg = configparser.ConfigParser()
        cfg.read(Config.__CONFIG_FILE_NAME)

        return cfg[section_name][item_name]
