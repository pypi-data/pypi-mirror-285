import os
import tempfile
import unittest
# from aws import s3_helper
# from aws.s3_imageresize import S3ImageVariant

class Test测试1(unittest.TestCase):
    def setUp(self) -> None:
        self.bucketname = "zappa-zapdemo-001"
        return super().setUp()

    def test_upload(self):
        print("hello test")

if __name__ == '__main__':
    unittest.main()
