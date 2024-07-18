import awscrt.auth
import awscrt.http
import awscrt.io
import awscrt.s3
import os
import threading
import typing
import urllib.parse
import multiprocessing

class File:
    def __init__(self, source: typing.Literal["local", "remote"], path: str):
        if not isinstance(source, str):
            raise TypeError('source must be a string')
        if source != "local" and source != "remote":
            raise ValueError('source must be local or remote')

        self.is_local = source == "local"
        self.path = path
        if not self.is_local:
            self.url_parts = urllib.parse.urlsplit(self.path)

    @property
    def bucket(self):
        if self.is_local:
            raise ValueError('this is a local file')
        return self.url_parts.netloc

    @property
    def key(self):
        if self.is_local:
            raise ValueError('this is a local file')
        return self.url_parts.path[1:]

class Transfer:
    def __init__(self, source: File, dest: File):
        if not isinstance(source, File) or not isinstance(dest, File):
            raise TypeError('source and dest must be a File')
        if source.is_local == dest.is_local:
            raise ValueError(
                'source and dest must be from different sources (local/local or remote/remote is not implemented)'
            )

        self.source = source
        self.dest = dest
        self.is_upload = source.is_local

    @property
    def is_download(self):
        return not self.is_upload

    @property
    def local(self):
        return self.source if self.is_upload else self.dest

    @property
    def remote(self):
        return self.dest if self.is_upload else self.source

class CredentialAdapter:
    def __init__(self, credentials):
        self.credentials = credentials            

    def __call__(self):
        credentials = self.credentials.get_frozen_credentials()            
        return awscrt.auth.AwsCredentials(                
            credentials.access_key, credentials.secret_key, credentials.token            
        )

class TransferManager:
    def __init__(self, refreshable_session=None):
        self._event_loop_group = awscrt.io.EventLoopGroup()
        self._host_resolver = awscrt.io.DefaultHostResolver(self._event_loop_group)
        self._bootstrap = awscrt.io.ClientBootstrap(self._event_loop_group, self._host_resolver)
        self._part_size = 8 * 1024 * 1024
        self._target_gbps = 1
        try:
            threads = multiprocessing.cpu_count()
        except NotImplementedError:
            threads = 24    # in case of error, default to 24 threads
        self._semaphore = threading.Semaphore(threads)
        self._region = "eu-west-1"
        self.session = refreshable_session
        if self.session is not None:
            self.creds_adapter = CredentialAdapter(self.session.get_credentials())
            self.creds_provider = awscrt.auth.AwsCredentialsProvider.new_delegate(self.creds_adapter)
        else:
            self.creds_provider = awscrt.auth.AwsCredentialsProvider.new_default_chain(client_bootstrap=self._bootstrap)
        self._signing_config = awscrt.s3.create_default_s3_signing_config(
            region=self._region,
            credential_provider=self.creds_provider
        )
        self._client = awscrt.s3.S3Client(
            bootstrap=self._bootstrap,
            region=self._region,
            part_size=self._part_size,
            throughput_target_gbps=self._target_gbps,
            signing_config=self._signing_config
        )

    def _bucket_to_host(self, bucket: str):
        return f'{bucket}.s3.{self._region}.amazonaws.com'

    def _transfer_to_req(self, transfer: Transfer):
        headers = awscrt.http.HttpHeaders()
        headers.add('host', self._bucket_to_host(transfer.remote.bucket))
        if transfer.is_upload:
            file_size = os.path.getsize(transfer.local.path)
            headers.add('content-length', str(file_size))
            headers.add('x-amz-storage-class', 'INTELLIGENT_TIERING')
        request = awscrt.http.HttpRequest(
            method='PUT' if transfer.is_upload else 'GET',
            headers=headers,
            path=urllib.parse.quote(f'/{transfer.remote.key}')
        )
        return request

    def _on_done_callback(self, error, error_headers, error_body, **kwargs):
        self._semaphore.release()

    def _do_transfer(self, transfers: list[Transfer]):
        if not isinstance(transfers, list):
            raise TypeError('transfers must be a list')
        if len(transfers) == 0:
            raise ValueError('transfers cannot be empty')
        if not all(isinstance(x, Transfer) for x in transfers):
            raise TypeError('transfers must be of type Transfer')

        # Requests should be kept (i.e. they should not go out of scope) otherwise it won't work
        requests = []

        for t in transfers:
            self._semaphore.acquire()
            req = self._client.make_request(
                request=self._transfer_to_req(t),
                type=awscrt.s3.S3RequestType.PUT_OBJECT if t.is_upload else awscrt.s3.S3RequestType.GET_OBJECT,
                recv_filepath=t.local.path if t.is_download else None,
                send_filepath=t.local.path if t.is_upload else None,
                on_done=self._on_done_callback
            )
            requests.append(req)

        # Waits until all requests have finished, raises exception if a request failed.
        # However, if a request failed, the exception is not raised until all requests have started.
        for request in requests:
            request.finished_future.result()