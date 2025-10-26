import base64

import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from fastapi import FastAPI, UploadFile

s3_client = boto3.client(
    "s3",
    endpoint_url="http://minio.local:9000",
    aws_access_key_id="admin",
    aws_secret_access_key="12345678",
    config=Config(signature_version="s3v4"),
)

app = FastAPI()


@app.get("/cats")
def cat_img_list():
    bucket_name = "cats"

    # List up to 25 objects
    response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=25)

    if "Contents" not in response:
        return {"message": "No objects found in bucket."}

    results = []

    for obj in response["Contents"]:
        key = obj["Key"]

        # Get the object
        file_obj = s3_client.get_object(Bucket=bucket_name, Key=key)
        file_bytes = file_obj["Body"].read()

        # Encode to base64
        encoded_str = base64.b64encode(file_bytes).decode("utf-8")

        # Append metadata + base64
        results.append(
            {
                "key": key,
                "size": obj["Size"],
                "base64": encoded_str,
            }
        )

    return results


@app.post("/cats")
def cat_upload(cat_img: UploadFile):
    GB = 1024**3
    config = TransferConfig(multipart_threshold=5 * GB)
    s3_client.upload_fileobj(
        cat_img.file,
        "cats",
        cat_img.filename,
        Config=config,
        ExtraArgs={"ContentType": cat_img.content_type},
    )
