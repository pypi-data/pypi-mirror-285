class AzureBlobDataSource:

    def __init__(self, client_id='', tenant_id='', client_secret='', account_url='', container_name='', blob_name=''):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.account_url = account_url
        self.container_name = container_name
        self.blob_name = blob_name

    def show(self):
        print("client_id =", self.client_id)
        print("tenant_id =", self.tenant_id)
        print("client_secret =", self.client_secret)
        print("account_url =", self.account_url)
        print("container_name =", self.container_name)
        print("blob_name =", self.blob_name)

    def to_dict(self):
        out = {
                "client_id": self.client_id,
                "tenant_id": self.tenant_id,
                "client_secret": self.client_secret,
                "account_url": self.account_url,
                "container_name": self.container_name,
                "blob_name": self.blob_name,
                }
        return out

class AWSS3DataSource:
    def __init__(self, access_key='', secret_token='', bucket='', key=''):
        self.access_key = access_key
        self.secret_token = secret_token
        self.bucket = bucket
        self.key = key

    def show(self):
        print("access_key =", self.access_key)
        print("secret_token =", self.secret_token)

    def to_dict(self):
        out = {
                "access_key": self.access_key,
                "secret_token": self.secret_token,
                "bucket": self.bucket,
                "key": self.key
                }
        return out

class URLDataSource:
    def __init__(self, url=''):
        self.url = url

    def show(self):
        print("URL =", self.url)

class LocalDataSource:
    def __init__(self, filename=''):
        self.filename = filename

    def show(self):
        print("File Name =", self.filename)

class DataSource:

    def __init__(self, location, **kwargs):
        self.location = location

        if location == "azure_blob":
            self.src = AzureBlobDataSource(**kwargs)
        elif location == "aws_s3":
            self.src = AWSS3DataSource(**kwargs)
        elif location == "webpage":
            self.src = URLDataSource(**kwargs)
        elif location == "local":
            self.src = LocalDataSource(**kwargs)

    def show(self):    
         self.src.show()

