import requests
import json
import os

# Replace with your NFT.Storage bearer token
bearer_token = os.getenv("NFT_STORAGE_API_KEY")

# Replace this with your Python object
imgURI = (
    "https://ipfs.io/ipfs/bafybeigwmnwmevdkox7kzqzpqqszgggbq2s2up3gjwpntxcgyrz64fkp44"
)

attributes = {"trait_type": "trait1", "value": "value1"}
token_metadata = {
    "name": "flying dog",
    "description": "description",
    "symbol": "symbol",
    "image": imgURI,
    "attributes": attributes,  # User supplied
}

# Convert the Python object to a JSON string
json_data = json.dumps(token_metadata)

# Prepare the HTTP headers with the bearer token and content type
headers = {
    "Authorization": f"Bearer {bearer_token}",
    "Content-Type": "application/json",
}

# Prepare the URL for the /upload endpoint
upload_url = "https://api.nft.storage/upload"

# Send a POST request to the /upload endpoint with the JSON data
response = requests.post(upload_url, headers=headers, data=json_data)

# Check the response
if response.status_code == 200:
    print("JSON data uploaded successfully!")
    print("IPFS CID:", json.loads(response.text)["value"]["cid"])
    # IPFS CID: bafkreidr5cnmualj2eh7g6bpe2iztglbfvottfceamswqevlye7negmkcq
else:
    print("Error uploading JSON data. Status code:", response.status_code)
    print("Response:", response.text)
