from ImplicitTLS import ImplicitFTP_TLS
import tempfile

from secrets import FTP_PASSWORD


server = ImplicitFTP_TLS()
server.set_pasv(True)
server.connect(host='infusionsoft.sharefileftp.com', port=990, timeout=90)
server.login(
        user='infusionsoft/josh.fullmer@infusionsoft.com',
        passwd=str(FTP_PASSWORD))
server.prot_p()
server.cwd('josh.fullmer@infusionsoft.com')
try:
    server.cwd('file_upload_test')
except Exception:
    server.mkd('file_upload_test')
    server.cwd('file_upload_test')
server.retrlines('LIST')
print(server.pwd())
with tempfile.NamedTemporaryFile(mode='w+b') as temp:
    temp.write(b'stuff and things')
    temp.seek(0)
    server.storbinary('STOR more.txt', temp)
    temp.flush()
