import argparse
import logging
from pprint import pformat

from utils.parse_documents import FileEmbeder
from utils.delete_documents import FileDeleter
from utils.list_blob_files import ListGCSFiles


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def app(args):
    """Helps user to test some srv-embed-service funtions as command-line arguments."""

    bucket = args.bucket
    bucket_prefix = args.bucket_prefix if args.bucket_prefix else None 
    app_url = args.app_url
    operation = args.operation

    logging.info(f"bucket: {bucket} - bucket_prefix {bucket_prefix}")  
    logging.info(f"app_url: {app_url} - operation {operation}")  

    blob_files = ListGCSFiles(bucket_name=bucket, prefix=bucket_prefix).list_gcs_files()

    if operation == "delete":
        for blob in blob_files: 
            logging.info(f"Removing file {blob} from index...")  
            delete_documents = FileDeleter(endpoint_url=app_url, file_path=blob)
            delete_documents.delete_file()
    elif operation == "embed":
        for blob in blob_files: 
            logging.info(f"Embedding file {blob} to index...")  
            embed_documents = FileEmbeder(endpoint_url=app_url, file_path=blob)
            embed_documents.embed_file()
    elif operation == "summarize":
        for blob in blob_files: 
            logging.info(f"Summarizing file {blob} to index...")  
            summarize_documents = FileEmbeder(endpoint_url=app_url, file_path=blob)
            summarize_documents.summarise_file()
    else:
        raise NotImplementedError(
            f"""Operation {operation} not implemented.
            Operations available are: delete, embed and summarize
            """)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Helps user to test some srv-embed-service functions")
    parser.add_argument("-b", "--bucket", help="The bucket name to list files from")
    parser.add_argument("-p", "--bucket_prefix", help="(Optional) The bucket prefix name to list files from")
    parser.add_argument("-a", "--app_url", help="The app url (e.g: https://app.com/)")
    parser.add_argument("-o", "--operation", help="delete, embed or summarize")
    args = parser.parse_args()

    app(args)