
AccessKey = "AKIAIG5G4NXEKQXUQSUA"
SecretKey = "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"

bucketName = "liut"

@profile
def test_s3_simples3():
	from simples3 import S3Bucket
	s = S3Bucket(bucketName, access_key=AccessKey, secret_key=SecretKey)
	for (key, modify, etag, size) in s.listdir():
		print "%r (%r) is size %r, modified %r" % (key, etag, size, modify)


if __name__ == '__main__':
	
	test_s3_simples3()
