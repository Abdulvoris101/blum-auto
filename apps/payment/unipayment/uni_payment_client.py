import asyncioimport sslimport certifiimport urllib3from unipayment import UniPaymentClient, Configuration, ApiClientfrom unipayment.rest import RESTClientObjectfrom urllib3.contrib.socks import SOCKSProxyManagerfrom apps.accounts.managers import ProxyManagerclass RESTClient(RESTClientObject):    def __init__(self, configuration, proxyScheme, pools_size=4, maxsize=None):        super().__init__(configuration)        addition_pool_args = {}        if configuration.assert_hostname is not None:            addition_pool_args['assert_hostname'] = configuration.assert_hostname        self.pool_manager = SOCKSProxyManager(            proxy_url=f"socks5h://{proxyScheme.host}:{proxyScheme.port}",            username=proxyScheme.user,            password=proxyScheme.password        )    @classmethod    async def create(cls, configuration, pools_size=4, maxsize=None):        proxyScheme = await ProxyManager.getGhostProxyByPhoneCode(91)        return cls(configuration, proxyScheme, pools_size)class ApiClientCustom(ApiClient):    def __init__(self, configuration=None, header_name=None, header_value=None, cookie=None):        super().__init__(configuration, header_name, header_value, cookie)        self.rest_client = None    async def initialize(self):        self.rest_client = await RESTClient.create(self.configuration)class UniPayment(UniPaymentClient):    def __init__(self, client_id, client_secret, is_sandbox=False, debug=False):        self.configuration = Configuration()        super().__init__(client_id, client_secret, is_sandbox, debug)        self.configuration.verify_ssl = False        self.api_client = None    async def initialize(self):        self.api_client = ApiClientCustom(self.configuration)        await self.api_client.initialize()