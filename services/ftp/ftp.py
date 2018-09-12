from django.core.files.temp import NamedTemporaryFile

from ..ftp.implicit_ftp_tls import ImplicitFTP_TLS
from ..constants import FTP_PASS


def upload_file(filename, file, instance_name):
    server = FTP_Server()
    server.connect()
    server.cwd(instance_name)
    server.upload(filename, file)


class FTP_Server():

    def __init__(self):
        self.server = ImplicitFTP_TLS()

    def connect(self):
        self.server.set_pasv(True)
        self.server.connect(
            host='infusionsoft.sharefileftp.com',
            port=990,
            timeout=90)
        self.server.login(
                user='infusionsoft/josh.fullmer@infusionsoft.com',
                passwd=FTP_PASS)
        self.server.prot_p()
        self.server.cwd('josh.fullmer@infusionsoft.com')

    def cwd(self, directory):
        try:
            self.server.cwd(directory)
        except Exception:
            self.server.mkd(directory)
            self.server.cwd(directory)

    def upload(self, filename, file):
        """Must be a NamedTemporaryFile"""
        if not isinstance(file, NamedTemporaryFile):
            raise Exception('File must be NamedTemporaryFile')
        file.seek(0)
        self.server.storbinary(f'STOR {filename}', file)
        file.flush()
