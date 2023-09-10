import os
import nft_storage
from nft_storage.api import nft_storage_api
from nft_storage.model.error_response import ErrorResponse
from nft_storage.model.upload_response import UploadResponse
from nft_storage.model.unauthorized_error_response import UnauthorizedErrorResponse
from nft_storage.model.forbidden_error_response import ForbiddenErrorResponse


# Configure Bearer authorization (JWT): bearerAuth
# TODO: learn what JWT is
configuration = nft_storage.Configuration(access_token=os.getenv("NFT_STORAGE_API_KEY"))

# Enter a context with an instance of the API client
with nft_storage.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = nft_storage_api.NFTStorageAPI(api_client)

    body = open(f"v1_txt2img_0.png", "rb")
    try:
        api_response = api_instance.store(body, _check_return_type=False)
        print(api_response)
    except nft_storage.ApiException as e:
        print("Exception when calling NFTStorageAPI->store: %s\n" % e)
