import requests

from api import download_file, upload_file

# Example usage
if __name__ == "__main__":
    dataset_id_tmp = "64e6c644c60d2823b0a2e266"
    # dataset_id_tmp = "666c22cf6f7335a39a14caa2"  # replace with your dataset ID
    # token_tmp = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvcmdPaWQiOiI1ZmZlYTM1NmU1ZWIzOTAwMTU3NTFhY2MiLCJ1c2VyT2lkIjoiNTlhZDBmMmUyMTEwMDEwNjYyMmExZjBjIiwibmFtZSI6InRlc3QiLCJpc09wZW5BUEkiOnRydWUsImlhdCI6MTcyMDc3OTk2OX0.49qcma_fWkUp1Wt6zLfrD3AHek0tBPb72hr7yWXQ5iY"  # replace with your token

    try:
        # dataset_details = get_dataset(dataset_id_tmp)
        # pprint.pp(dataset_details)
        # upload_file("/home/ubuntu/flask.zip", "flask.zip", dataset_id_tmp)
        print(
            download_file(
                dataset_id_tmp,
                "flask.zip",
            )
        )
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")
