from dataclasses import dataclass

import boto3


@dataclass
class GetStatusHelpers:
    @staticmethod
    def get_s3_count(bucket_name, prefix, region_name="us-west-2", aws_profile=None):
        """
        Get S3 counts from S3
        :param bucket_name:
        :type bucket_name:
        :param prefix:
        :type prefix:
        :param region_name:
        :type region_name:
        :param aws_profile:
        :type aws_profile:
        :return:
        :rtype:
        """
        boto3.setup_default_session(profile_name=aws_profile,  region_name=region_name)
        s3_resource = boto3.resource('s3')
        bucket = s3_resource.Bucket(name=bucket_name)
        prefix = f"{prefix.rstrip('/')}/"
        return sum(1 for _ in bucket.objects.filter(Prefix=prefix).all())

