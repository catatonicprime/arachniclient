import requests
from requests.auth import HTTPBasicAuth
from io import StringIO


class Scan:
    def __init__(self, _id=None, scanOptions=None, client=None, scan=None):
        self.id = _id
        self.scanOptions = scanOptions
        self.client = client
        self.scan = scan
        self.startTime = None

    def display(self):
        print ("{0} : {1}".format(self.id, self.status))

    @property
    def status(self):
        if self.scan is None:
            return None
        return self.scan['status']

    @property
    def url(self):
        return self.scanOptions['url']
    
    @property
    def runtime(self):
        try:
            return self.scan['statistics']['runtime']
        except:
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
        print('fmt: {0}'.format(fmt))
        if fmt in extensions:
            extension = extensions[fmt]
        report_data = self.client.getReport(self.id, fmt)
        with open("{0}{1}".format(self.id, extension), "wb") as handle:
            handle.write(report_data)


class Client:
    def __init__(self, hostname='127.0.0.1', port='7331', username=None, password=None):
        if hostname is None:
            raise Exception('hostname cannot be None')
        if port is None:
            raise Exception('port cannot be None')
        self.hostname = hostname
        self.port = port
        # Build the clients requests session with auth etc.
        session = requests.Session()
        if not (username is None or password is None):
            session.auth = HTTPBasicAuth(username, password)
        self._session = session

    def getAuth(self):
        if not (self.username is None or self.password is None):
            return HTTPBasicAuth(self.username, self.password)
        return None

    def getUrl(self, endpoint=''):
        return 'http://{0}:{1}/{2}'.format(self.hostname, self.port, endpoint)

    def getScans(self):
        r = self._session.get(self.getUrl('scans'))
        scanIds = r.json()
        scans = []
        for _id in scanIds:
            scans.append(Scan(_id=_id, scan=self.getScan(_id), client=self))
        return scans

    def addScan(self, scanOptions):
        r = self._session.post(self.getUrl('scans'), json=scanOptions)
        if not r.status_code == 200:
            raise Exception('An error occurred: \r\n{0}'.format(r.content))
        try:
            scan_id = r.json()['id']
        except:
            raise Exception('An error occurred retreiving scan id from json: {0}'.format(r.content))
        return scan_id

    def getScan(self, _id):
        r = self._session.get(self.getUrl('scans/{0}'.format(_id)))
        if not r.status_code == 200:
            raise Exception('An error occurred: \r\n{0}'.format(r.content))
        return r.json()

    def pauseScan(self, _id):
        r = self._session.put(self.getUrl('scans/{0}/pause'.format(_id)))
        if not r.status_code == 200:
            raise Exception('Failed to pause scan with id {0}'.format(_id))

    def resumeScan(self, _id):
        r = self._session.put(self.getUrl('scans/{0}/resume'.format(_id)))
        if not r.status_code == 200:
            raise Exception('Failed to resume scan with id {0}'.format(_id))

    def deleteScan(self, _id):
        r = self._session.delete(self.getUrl('scans/{0}'.format(_id)))
        if not r.status_code == 200:
            raise Exception('Failed to delete scan with id {0}'.format(_id))

    def getReport(self, _id, fmt=None):
        url = self.getUrl('scans/{0}/report'.format(_id))
        if fmt in ['json', 'xml', 'yaml', 'html.zip']:
            url = "{0}.{1}".format(url, 'html.zip')
        r = self._session.get(url)
        if not r.status_code == 200:
            raise Exception('Failed to download report for scan id {0}'.format(_id))
        return r.content
