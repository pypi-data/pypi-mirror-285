from thestage_core.services.config_provider.config_provider import ConfigProviderCore


class ConfigProvider(ConfigProviderCore):

    def __init__(
            self,
            project_path: str,
            auto_create: bool = True,
            only_global: bool = False,
    ):
        super(ConfigProvider, self).__init__(
            project_path=project_path,
            auto_create=auto_create,
            only_global=only_global,
        )
