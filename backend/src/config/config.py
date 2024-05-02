import configparser


class Config:
    """
    This class helps to interact with a config file
    """
    __CONFIG_FILE_NAME = 'config/config.ini'

    @staticmethod
    def get_config_item(section_name: str, item_name: str) -> any:
        """
        Get a config parameter with the name 'item_name' from the section 'section_name'
        :param section_name: The name of a section
        :param item_name: The name of parameter
        :return: Config parameter
        """
        cfg = configparser.ConfigParser()
        cfg.read(Config.__CONFIG_FILE_NAME)

        return cfg[section_name][item_name]
