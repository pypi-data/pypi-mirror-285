# About

Python-SDK to work with Investfly API.
[Investfly](https://www.investfly.com)

Investfly offers a platform for developing automated stock trading strategies. Users can create trading strategies through an intuitive drag-and-drop interface or by coding in Python.

The Investfly SDK contains the API and tools needed to build and deploy Python-based trading strategies on the Investfly platform.

Although you can edit Python code in our browser-based editor, writing code in a familiar IDE (Pycharm, VSCode) is recommended due to all the benefits that rich IDE offers. This SDK and CLI that comes with it makes it possible to develop trading strategy locally using your favorite IDE and upload it your Investfly account.

# Quickstart

### SDK Installation and Setup

Investfly-SDK comes with all required Python classes used for strategy development as well as a command line tool (CLI) called `investfly-cli`

Using a terminal app, run the following commands.

**Setup Project and Virtual Environment**

```commandline
mkdir investfly
cd investfly
python3 -m venv venv
source venv/bin/activate
```

**Install investfly-sdk**

```commandline
pip install investfly-sdk
```

**Launch investfly-cli**

Install investfly-sdk also adds investfly-cli in your path inside the virtual environment. It can be launched simply by using `investfly-cli` command in the virtual env.

```commandline
(venv) user@host$ investfly-cli 

investfly-cli$ -h
usage: investfly-cli [-h]
                     {login,logout,strategy.list,strategy.copysamples,strategy.create,strategy.download,strategy.update,strategy.backtest.start,strategy.backtest.stop,strategy.backtest.result,exit}
                     ...

positional arguments:
  {login,logout,strategy.list,strategy.copysamples,strategy.create,strategy.download,strategy.update,strategy.backtest.start,strategy.backtest.stop,strategy.backtest.result,exit}
                        Available Commands
    login               Login to Investfly
    logout              Logout from Investfly
    strategy.list       List Python Strategies
    strategy.copysamples
                        Copy Samples from SDK
    strategy.create     Create a new trading strategy
    strategy.download   Download one of your strategy and save it to a file
    strategy.update     Update strategy Python Code
    strategy.backtest.start
                        Start backtest for strategy
    strategy.backtest.stop
                        Stop backtest for strategy
    strategy.backtest.result
                        Get backtest result, waiting if backtest is still
                        running
    exit                Stop and Exit CLI

options:
  -h, --help            show this help message and exit

investfly-cli$ 
```

**Test Installation**

You can test the installation by using the CLI to login and logout of Investfly.
```commandline
investfly-cli$ login -u <YOUR_USERNAME> -p <YOUR_PASSWORD>
Session(username='xxxxxx', clientId='xxxxx-kaj1p3lv', clientToken='b29c9acc-330a-4821-9187-282d827e3e91')

investfly-cli$ logout
```


### Trading Strategy Development

Investfly-SDK comes with a starter strategy template and many sample strategies to help you get started quickly.


**Copy Samples**

```commandline
investfly-cli$ copysamples
Samples copied to ./samples directory
```

**Create New Strategy**

You can use one of the samples to create a new strategy. Normally, you would make a copy of the sample strategy, edit the copy using your favorite IDE to create a new strategy.
But for now, we'll use the unmodified sample
```commandline
investfly-cli$ login -u <YOUR_USERNAME> -p <YOUR_PASSWORD>
Session(username='xxxxx', clientId='xxxxxx-krfs61aa', clientToken='766fad47-3e1e-4f43-a77a-72a95a395fec')

investfly-cli$ strategy.create -n MySmaCrossOverStrategy -f ./samples/strategies/SmaCrossOverStrategy.py
Created strategy 83

investfly-cli$ strategy.list
{'strategyId': 83, 'strategyName': 'MySmaCrossOverStrategy'}

```

**Edit and Update Code**

Edit and update ./samples/strategies/SmaCrossOverStrategy.py as you like. For testing, change the `StandardSymbolsList.SP_100` to `StandardSymbolsList.SP_500` inside `getSecurityUniverseSelector` function.  

```commandline
investfly-cli$ strategy.update --id 83 -f ./samples/strategies/SmaCrossOverStrategy.py
Code Updated
```

After the code is updated, next step is to backtest the strategy and deploy it live. 
You can do them by logging into Investfly with a web browser, navigating to the strategy page and invoking corresponding actions.


### IDE Editor

The primary reason for publishing this SDK is so that you can use your favorite IDE Editor to write and update Python Code.
We recommend using PyCharm community edition:
https://www.jetbrains.com/pycharm/download

Using IDE editor will assist with auto-completion and type hints. Additionally, use type checking tools like mypy to check your code before deploying.

When using the IDE, open `investfly` directory created above as a project with your IDE. 
Make sure that Python Interpreter is configured to the virtual environment `investfly/venv/bin/python` created above.


# API Docs

API Docs are published at https://www.investfly.com/guides/docs/index.html

# Getting Help
Please email [admin@investfly.com](admin@investfly.com) for any support or bug report



