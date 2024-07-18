""" This package contains REST API Client classes to make REST API calls to Investfly server.
The entry point is `investfly.api.InvestflyApiClient`

InvestflyApiClient has members to access specific endpoints such as strategyApi, portfolioApi etc

For now, only those API methods that are commonly used during in strategy development are added in the clients.

```
from investfly.api.InvestflyApiClient import InvestflyApiClient
api = InvestflyApiClient()
api.login("<YOUR USERNAME>", "<YOUR PASSWORD>")
pythonStrategies = api.strategyApi.getStrategies()
print(pythonStrategies)
api.logout()
```

"""