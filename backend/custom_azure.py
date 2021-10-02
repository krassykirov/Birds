from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'djangostg'
    account_key = ''
    azure_container = 'media'
    expiration_secs = None

class AzureStaticStorage(AzureStorage):
    account_name = 'djangostg'
    account_key = ''
    azure_container = 'static'
    expiration_secs = None