import json

import boto3
import botocore

from komo import printing
from komo.api_client import APIClient
from komo.types import ClientException


def connect(api_key: str):
    api_client = APIClient()
    api_client.connect_lambda(api_key)
