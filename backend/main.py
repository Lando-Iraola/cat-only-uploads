import boto3
from boto3.s3.transfer import TransferConfig
from botocore.client import Config
from botocore.exceptions import ClientError
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

    try:
        # List up to 25 objects
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=25)

        if "Contents" not in response:
            return {"message": "No objects found in bucket."}

        results = []

        for obj in response["Contents"]:
            key = obj["Key"]

            results.append(
                {
                    "img_name": key,
                    "img_src": generate_presigned_url(
                        s3_client,
                        "get_object",
                        {"Bucket": bucket_name, "Key": key},
                        300,
                    ),
                }
            )

        return results
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            print("lmao no bucket")
            return []
        print(e)


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


def generate_presigned_url(s3_client, client_method, method_parameters, expires_in):
    """
    Generate a presigned Amazon S3 URL that can be used to perform an action.

    :param s3_client: A Boto3 Amazon S3 client.
    :param client_method: The name of the client method that the URL performs.
    :param method_parameters: The parameters of the specified client method.
    :param expires_in: The number of seconds the presigned URL is valid for.
    :return: The presigned URL.
    """
    try:
        url = s3_client.generate_presigned_url(
            ClientMethod=client_method, Params=method_parameters, ExpiresIn=expires_in
        )
    except ClientError:
        print(f"Couldn't get a presigned URL for client method '{client_method}'.")
        raise

    return url
