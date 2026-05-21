class SMSPollingError(Exception):
    pass


class RequestError(SMSPollingError):
    pass


class ParseError(SMSPollingError):
    pass


class ProviderNotFoundError(Exception):
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        super().__init__(f"Provider '{provider_name}' not found.")


class PlatformNotSupportedError(Exception):
    def __init__(self, provider_name: str, platform: str):
        self.provider_name = provider_name
        self.platform = platform
        super().__init__(f"Provider '{provider_name}' does not support platform '{platform}'.")


class NoProviderAvailableError(Exception):
    def __init__(self, platform: str):
        self.platform = platform
        super().__init__(f"No available provider for platform '{platform}'.")
