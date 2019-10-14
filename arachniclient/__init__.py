import requests
from requests.auth import HTTPBasicAuth
from io import StringIO


class Scan:
    def __init__(self, scanId=None, scanOptions=None, client=None, scan=None):
        self.id = scanId
        self.scanOptions = scanOptions
        self.client = client
        self.scan = scan

    def display(self):
        print ("{0} : {1}".format(self.id, self.status))

    @property
    def status(self):
        self.updateScan()
        if self.scan is None:
            return None
        return self.scan['status']

    @property
    def url(self):
        return self.scanOptions['url']

    @property
    def runtime(self):
        self.updateScan()
        try:
            return self.scan['statistics']['runtime']
        except ValueError:
            return None

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

    def downloadReport(self, fmt=None, dest=None):
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
        fmt = str(fmt)
        if fmt in extensions:
            extension = extensions[fmt]
        report_data = self.client.getReport(self.id, fmt)
        with open("{0}{1}".format(self.id, extension), "wb") as handle:
            handle.write(report_data)


class Client:
    def __init__(self, hostname='127.0.0.1', port=7331, username=None, password=None):
        if hostname is None:
            raise Exception('hostname cannot be None')
        if port is None:
            raise Exception('port cannot be None')
        self.hostname = hostname
        self.port = port

        # Build the client requests session with auth etc.
        session = requests.Session()
        if (username or password):
            session.auth = HTTPBasicAuth(username, password)
        self._session = session

    def getUrl(self, endpoint=''):
        return 'http://{0}:{1}/{2}'.format(self.hostname, self.port, endpoint)

    def getScans(self):
        r = self._session.get(self.getUrl('scans'))
        scanIds = r.json()
        scans = []
        for scanId in scanIds:
            scans.append(Scan(scanId=scanId, scan=self.getScan(scanId), client=self))
        return scans

    def addScan(self, scanOptions):
        r = self._session.post(self.getUrl('scans'), json=scanOptions)
        if not r.status_code == 200:
            raise Exception('An error occurred: \r\n{0}'.format(r.content))
        try:
            scan_id = r.json()['id']
        except ValueError:
            raise Exception('An error occurred retreiving scan id from json: {0}'.format(r.content))
        return scan_id

    def getScan(self, scanId):
        r = self._session.get(self.getUrl('scans/{0}'.format(scanId)))
        if r.status_code == 200:
            return r.json()
        raise Exception('An error occurred: \r\n{0}'.format(r.content))

    def pauseScan(self, scanId):
        r = self._session.put(self.getUrl('scans/{0}/pause'.format(scanId)))
        if r.status_code == 200:
            return
        raise Exception('Failed to pause scan with id {0}'.format(scanId))

    def resumeScan(self, scanId):
        r = self._session.put(self.getUrl('scans/{0}/resume'.format(scanId)))
        if r.status_code == 200:
            return
        raise Exception('Failed to resume scan with id {0}'.format(scanId))

    def deleteScan(self, scanId):
        r = self._session.delete(self.getUrl('scans/{0}'.format(scanId)))
        if r.status_code == 200:
            return
        raise Exception('Failed to delete scan with id {0}'.format(scanId))

    def getReport(self, scanId, fmt=None):
        url = self.getUrl('scans/{0}/report'.format(scanId))
        if fmt in ['json', 'xml', 'yaml', 'html.zip']:
            url = "{0}.{1}".format(url, fmt)
        r = self._session.get(url)
        if r.status_code == 200:
            return r.content
        raise Exception('Failed to download report for scan id {0}'.format(scanId))
