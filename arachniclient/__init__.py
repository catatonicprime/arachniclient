import requests
from requests.auth import HTTPBasicAuth
from io import StringIO
import time


class Scan:
    def __init__(self, _id=None, scanOptions=None, client=None, scan=None):
        self.id = _id
        self.scanOptions = scanOptions
        self.client = client
        self.scan = scan

    def display(self):
        print ("Scan {0}:".format(self.id))
        print ("\tStatus: {0}".format(self.scan['status']))
        print ("\tIssues: {0}".format(self.scan['issues']))
        print ("\tCurrent Page: {0}".format(self.scan['statistics']['current_page']))

    def updateScan(self):
        if self.client is None:
            raise Exception("client cannot be None")
        if self.id is None:
            raise Exception("id cannot be None")
        self.scan = self.client.getScan(self.id)

    def pauseScan(self):
        if self.client is None:
            raise Exception("client cannot be None")
        if self.id is None:
            raise Exception("id cannot be None")
        self.client.pauseScan(self.id)

    def resumeScan(self):
        if self.client is None:
            raise Exception("client cannot be None")
        if self.id is None:
            self.startScan()
        else:
            self.client.resumeScan(self.id)

    def startScan(self):
        if self.client is None:
            raise Exception("client cannot be None")
        if self.id is not None:
            self.resumeScan()
            return
        if self.scanOptions is None:
            raise Exception("scanOptions cannot be None")
        if self.scanOptions['url'] is None:
            raise Exception('Scan URL is required')
        self.id = self.client.addScan(self.scanOptions)

    def deleteScan(self):
        if self.client is None:
            raise Exception("client cannot be None")
        if self.id is None:
            raise Exception("id cannot be None")
        self.client.deleteScan(self.id)
        self.id = None

    def downloadReport(self, _format=None, dest=None):
        if self.client is None:
            raise Exception("client cannot be None")
        if self.id is None:
            raise Exception("id cannot be None")
        extensions = {'json': '.json',
                      'xml': '.xml',
                      'yaml': '.yaml',
                      'html.zip': '.html.zip'}
        # Default to '.json' extension.
        extension = extensions['json']
        fmt = str(_format)
        print('fmt: {0}'.format(fmt))
        if fmt in extensions:
            extension = extensions[fmt]
        report_data = self.client.getReport(self.id, _format)
        with open("{0}{1}".format(self.id, extension), "wb") as handle:
            handle.write(report_data)


class Client:
    def __init__(self, hostname='localhost', port='7331', username=None, password=None):
        if hostname is None:
            raise Exception('Hostname cannot be None')
        if port is None:
            raise Exception('Port cannot be None')
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    def getAuth(self):
        if not (self.username is None or self.password is None):
            return HTTPBasicAuth(self.username, self.password)
        return None

    def getUrl(self, endpoint=''):
        return 'http://{0}:{1}/{2}'.format(self.hostname, self.port, endpoint)

    def getScans(self):
        r = requests.get(self.getUrl('scans'), auth=self.getAuth())
        scanIds = r.json()
        scans = []
        for _id in scanIds:
            scans.append(Scan(_id=_id, scan=self.getScan(_id), client=self))
        return scans

    def addScan(self, scanOptions):
        r = requests.post(self.getUrl('scans'), json=scanOptions, auth=self.getAuth())
        if not r.status_code == 200:
            raise Exception('An error occurred: \r\n{0}'.format(r.content))
        try:
            scan_id = r.json()['id']
        except:
            raise Exception('An error occurred retreiving scan id from json: {0}'.format(r.content))
        return scan_id

    def getScan(self, _id):
        r = requests.get(self.getUrl('scans/{0}'.format(_id)), auth=self.getAuth())
        if not r.status_code == 200:
            raise Exception('An error occurred: \r\n{0}'.format(r.content))
        return r.json()

    def pauseScan(self, _id):
        r = requests.put(self.getUrl('scans/{0}/pause'.format(_id)), auth=self.getAuth())
        if not r.status_code == 200:
            raise Exception('Failed to pause scan with id {0}'.format(_id))

    def resumeScan(self, _id):
        r = requests.put(self.getUrl('scans/{0}/resume'.format(_id)), auth=self.getAuth())
        if not r.status_code == 200:
            raise Exception('Failed to resume scan with id {0}'.format(_id))

    def deleteScan(self, _id):
        r = requests.delete(self.getUrl('scans/{0}'.format(_id)), auth=self.getAuth())
        if not r.status_code == 200:
            raise Exception('Failed to delete scan with id {0}'.format(_id))

    def getReport(self, _id, _format=None):
        url = self.getUrl('scans/{0}/report'.format(_id))
        if _format in ['json', 'xml', 'yaml', 'html.zip']:
            url = "{0}.{1}".format(url, 'html.zip')
        r = requests.get(url, auth=self.getAuth())
        if not r.status_code == 200:
            raise Exception('Failed to download report for scan id {0}'.format(_id))
        return r.content
