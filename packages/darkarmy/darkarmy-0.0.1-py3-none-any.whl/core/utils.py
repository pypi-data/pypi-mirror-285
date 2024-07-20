
class attackerAgent():
    '''base class for attacker agent'''
    def __init__(self, name, host, port, username, password):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.client = self.connect()

    def connect(self):
        '''connect to the agent'''
        pass

    def disconnect(self):
        '''disconnect from the agent'''
        pass

    def execute(self, command):
        '''execute a command on the agent'''
        pass

    def upload(self, local, remote):
        '''upload a file to the agent'''
        pass

    def download(self, remote, local):
        '''download a file from the agent'''
        pass

    def __str__(self):
        return f'{self.name} {self.host}:{self.port}'

class defenderAgent():
    '''base class for defender agent'''
    def __init__(self, name, host, port, username, password):
        self.name = name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None
        self.client = self.connect()

    def connect(self):
        '''connect to the agent'''
        pass

    def disconnect(self):
        '''disconnect from the agent'''
        pass

    def execute(self, command):
        '''execute a command on the agent'''
        pass

    def upload(self, local, remote):
        '''upload a file to the agent'''
        pass

    def download(self, remote, local):
        '''download a file from the agent'''
        pass

    def detect_attack(self):
        '''detect an attack'''
        pass
    
    def __str__(self):
        return f'{self.name} {self.host}:{self.port}'