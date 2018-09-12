import tempfile
import zipfile

from ..ftp.implicit_ftp_tls import ImplicitFTP_TLS
from ..constants import FTP_PASS


def upload_file(filename, file, instance_name):
    server = FTP_Server()
    server.connect()
    server.cwd(instance_name)
    server.upload(filename, file)


def compress_dir(instance_name):
    server = FTP_Server()
    server.connect()
    server.cwd(instance_name)
    filenames = server.dir_list()
    with tempfile.SpooledTemporaryFile() as temp:
        with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as archive:
            for filename in filenames:
                file = server.get_temp_file(filename)
                print(file.name, filename)
                archive.writestr(filename, file.read())
                file.close()
        server.cwd('..')
        server.rmd(instance_name)
        server.upload(f'{instance_name}.zip', temp)


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
        self.server.cwd('josh.fullmer@infusionsoft.com/web_files')

    def cwd(self, directory):
        try:
            self.server.cwd(directory)
        except Exception:
            self.server.mkd(directory)
            self.server.cwd(directory)

    def rmd(self, directory):
        # TODO: Make recursive: https://gist.github.com/artlogic/2632647
        if self.dir_list():
            self.server.cwd(directory)
            for filename in self.dir_list():
                self.server.delete(filename)
            self.server.cwd('..')
        self.server.rmd(directory)

    def upload(self, filename, file):
        """Must be a NamedTemporaryFile"""
        file.seek(0)
        self.server.storbinary(f'STOR {filename}', file)
        file.flush()

    def dir_list(self):
        return self.server.nlst()

    def get_temp_file(self, filename):
        file = tempfile.NamedTemporaryFile()
        self.server.retrbinary(f'RETR {filename}', file.write)
        file.seek(0)
        return file
