import os
# import sys
# from pathlib import Path
import tempfile
import unittest
from mtlibs.aws import s3_helper
# from . import configtest
from mtlibs.aws.s3_imageresize import S3ImageVariant

bucket_name = 'djwagcms-media-10010'


class Test测试1(unittest.TestCase):

    def setUp(self) -> None:
        # configtest.configMainAwsKey()
        self.bucketname = "zappa-zapdemo-001"
        return super().setUp()

    def test_upload(self):
        key = "test/test1.txt"
        s3_helper.uploadFile_bytes(bucket_name, key, b'1111')
        saveFileTo = os.path.join(tempfile.gettempdir(), key)
        s3_helper.downloadToLocal(bucket_name, key, saveFileTo)
        s3_helper.delete(bucket_name, key)

    # def test_2(self): 
    #     key = "original_images/5b8debc19c8a3.jpg"
    #     a = S3ImageVariant(src_bucket=self.bucketname,
    #                        dest_bucket=self.bucketname,
    #                        src_prifix="original_images/",
    #                        dest_prifix="image/"
    #                        )
    #     a.onCreateObject(key=key)
        
    def test_许正确设置前缀(self):
        with self.assertRaises(Exception) as context:             
            S3ImageVariant(src_bucket="zappa-zapdemo-001",
                            dest_bucket="zappa-zapdemo-001",
                            src_prifix="",
                            dest_prifix="images/"
                            )
            
    def test_前缀不能相同(self):
        with self.assertRaises(Exception) as context:             
            S3ImageVariant(src_bucket="zappa-zapdemo-001",
                            dest_bucket="zappa-zapdemo-001",
                            src_prifix="images/",
                            dest_prifix="images/"
                            )
    # def test_检测不存在的bucket(self):
    #     is_exists = s3_helper.bucket_exists("bucket_name_notexist_oiuia9sd8f8_jdjfkl232kdf")
    #     self.assertFalse(is_exists)



if __name__ == '__main__':
    unittest.main()
