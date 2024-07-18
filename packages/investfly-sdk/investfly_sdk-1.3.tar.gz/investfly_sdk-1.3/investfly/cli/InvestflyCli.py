import argparse
import pickle
import os.path
import time
from typing import List, cast

from investfly.api.InvestflyApiClient import InvestflyApiClient
from investfly.models import Session, IndicatorSpec
from investfly.models.StrategyModels import TradingStrategyModel, BacktestResult, BacktestStatus, BacktestResultStatus

from investfly import samples
import inspect
from pathlib import Path
import shutil


class InvestflyCli:

    def __init__(self):
        self.running: bool = True
        self.investflyApi = InvestflyApiClient()


    def __loginAction(self, args: argparse.Namespace) -> Session:
        username = args.username
        password = args.password
        session = self.investflyApi.login(username, password)
        return session

    def __logoutAction(self, args: argparse.Namespace) -> None:
        self.investflyApi.logout()

    def __exitAction(self, args: argparse.Namespace|None) -> None:
        if self.investflyApi.isLoggedIn():
            self.investflyApi.logout()
        self.running = False

    def __copySamples(self, args: argparse.Namespace) -> str:
        samplesPath = inspect.getfile(samples)
        path = Path(samplesPath)
        parentPath = path.parent
        shutil.copytree(parentPath, './samples', dirs_exist_ok=True)
        return "Samples copied to ./samples directory"


    # ==== Strategy Command Handlers

    def __listStrategies(self, args: argparse.Namespace) -> str:
        strategies: List[TradingStrategyModel] = self.investflyApi.strategyApi.listStrategies()
        strategiesDictList = list(map(lambda model: str({'strategyId': model.strategyId,  'strategyName': model.strategyName}), strategies))
        return "\n".join(strategiesDictList)

    def __createStrategy(self, args: argparse.Namespace) -> str:
        name = args.name
        path = args.file
        with open(path, 'r') as source_file:
            code = source_file.read()
        tradingStrategyModel = TradingStrategyModel(strategyName=name, strategyDesc=name, pythonCode=code)
        tradingStrategyModel = self.investflyApi.strategyApi.createStrategy(tradingStrategyModel)
        return f'Created strategy {tradingStrategyModel.strategyId}'

    def __downloadCode(self, args: argparse.Namespace) -> str:
        strategyId = int(args.id)
        path = args.file
        strategyModel: TradingStrategyModel = self.investflyApi.strategyApi.getStrategy(strategyId)
        code: str = cast(str, strategyModel.pythonCode)
        with open(path, 'w') as out_file:
            out_file.write(code)
        return f"Strategy saved to {path}"

    def __updateCode(self, args: argparse.Namespace) -> str:
        strategyId = int(args.id)
        path = args.file
        with open(path, 'r') as source_file:
            code = source_file.read()
        self.investflyApi.strategyApi.updateStrategyCode(strategyId, code)
        return 'Code Updated'

    def __startBacktest(self, args: argparse.Namespace) -> str:
        strategyId = int(args.id)
        message = self.investflyApi.strategyApi.startBacktest(strategyId)
        return str(message.toDict())

    def __stopBacktest(self, args: argparse.Namespace) -> str:
        strategyId = int(args.id)
        message = self.investflyApi.strategyApi.stopBacktest(strategyId)
        return str(message.toDict())

    def __pollResults(self, args: argparse.Namespace) -> str:
        strategyId = int(args.id)
        backtestResult: BacktestResult = self.investflyApi.strategyApi.getBacktestResult(strategyId)
        backtestStatus: BacktestResultStatus = backtestResult.status
        print(str(backtestStatus.toDict()))
        notFinished = backtestStatus.jobStatus == BacktestStatus.QUEUED or backtestStatus.jobStatus == BacktestStatus.INITIALIZING or backtestStatus.jobStatus == BacktestStatus.RUNNING
        try:
            while notFinished:
                time.sleep(3)
                backtestResult = self.investflyApi.strategyApi.getBacktestResult(strategyId)
                backtestStatus = backtestResult.status
                print(str(backtestStatus.toDict()))
                notFinished = backtestStatus.jobStatus == BacktestStatus.QUEUED or backtestStatus.jobStatus == BacktestStatus.INITIALIZING or backtestStatus.jobStatus == BacktestStatus.RUNNING
        except KeyboardInterrupt as e:
            print("Interrupted")
            pass
        return str(backtestResult.performance)

    # ==== INDICATOR COMMAND HANDLERS

    def __listIndicators(self, args: argparse.Namespace) -> str:
        indicators: List[IndicatorSpec] = self.investflyApi.indicatorApi.listIndicators()
        idList = list(map(lambda spec: spec.indicatorId, indicators))
        return str(idList)

    def __createUpdateIndicator(self, args: argparse.Namespace):
        path = args.file
        with open(path, 'r') as source_file:
            code = source_file.read()
        self.investflyApi.indicatorApi.createUpdateIndicator(code)

    def __downloadIndicatorCode(self, args: argparse.Namespace):
        indicatorId = args.id
        path = args.file
        code = self.investflyApi.indicatorApi.getIndicatorCode(indicatorId)
        with open(path, 'w') as out_file:
            out_file.write(code)
        return f"Indicator saved to {path}"

    def runCli(self) -> None:
        parser = argparse.ArgumentParser(prog="investfly-cli")
        subparser = parser.add_subparsers(help='Available Commands', dest="command")

        parser_login = subparser.add_parser('login', help='Login to Investfly')
        parser_login.add_argument('-u', '--username', required=True, help='Input username')
        parser_login.add_argument('-p', '--password', required=True, help='Input user password')
        parser_login.set_defaults(func=self.__loginAction)

        parser_logout = subparser.add_parser('logout', help="Logout from Investfly")
        parser_logout.set_defaults(func=self.__logoutAction)

        parser_copySamples = subparser.add_parser('copysamples', help='Copy Strategy and Indicator Samples from SDK')
        parser_copySamples.set_defaults(func=self.__copySamples)

        parser_exit = subparser.add_parser('exit', help='Stop and Exit CLI')
        parser_exit.set_defaults(func = self.__exitAction)

        # ======= STRATEGY COMMANDS ==========

        parser_listStrategies = subparser.add_parser('strategy.list', help='List Python Strategies')
        parser_listStrategies.set_defaults(func=self.__listStrategies)

        parser_createStrategy = subparser.add_parser('strategy.create', help='Create a new trading strategy')
        parser_createStrategy.add_argument('-n', '--name', required=True, help='Strategy Name')
        parser_createStrategy.add_argument('-f', '--file', required=True, help='Python File Path relative to the project root that contains strategy code')
        parser_createStrategy.set_defaults(func=self.__createStrategy)

        parser_downloadStrategy = subparser.add_parser('strategy.download', help='Download one of your strategy python code and save it to a file')
        parser_downloadStrategy.add_argument('-i', '--id', required=True, help='Strategy ID')
        parser_downloadStrategy.add_argument('-f', '--file', required=True, help='File path (with file name) to save strategy python code')
        parser_downloadStrategy.set_defaults(func=self.__downloadCode)

        parser_updateCode = subparser.add_parser('strategy.update', help='Update strategy Python Code')
        parser_updateCode.add_argument('-i', '--id', required=True, help='Strategy ID')
        parser_updateCode.add_argument('-f', '--file', required=True, help='File path (with file name) that contains strategy code')
        parser_updateCode.set_defaults(func=self.__updateCode)

        parser_startBacktest = subparser.add_parser('strategy.backtest.start', help='Start backtest for strategy')
        parser_startBacktest.add_argument('-i', '--id', required=True, help='Strategy ID')
        parser_startBacktest.set_defaults(func=self.__startBacktest)

        parser_stopBacktest = subparser.add_parser('strategy.backtest.stop', help='Stop backtest for strategy')
        parser_stopBacktest.add_argument('-i', '--id', required=True, help='Strategy ID')
        parser_stopBacktest.set_defaults(func=self.__stopBacktest)

        parser_resultBacktest = subparser.add_parser('strategy.backtest.result', help='Get backtest result, waiting if backtest is still running')
        parser_resultBacktest.add_argument('-i', '--id', required=True, help='Strategy ID')
        parser_resultBacktest.set_defaults(func=self.__pollResults)

        # ====== INDICATOR COMMANDS ====

        parser_listIndicators = subparser.add_parser('indicator.list', help='List Custom Indicators')
        parser_listIndicators.set_defaults(func=self.__listIndicators)

        parser_downloadIndicator = subparser.add_parser('indicator.download', help='Download indicator python code and save it to a file')
        parser_downloadIndicator.add_argument('-i', '--id', required=True, help='IndicatorId ID')
        parser_downloadIndicator.add_argument('-f', '--file', required=True,  help='File path (with file name) to save indicator python code')
        parser_downloadIndicator.set_defaults(func=self.__downloadIndicatorCode)

        parser_createUpdateIndicator = subparser.add_parser('indicator.update', help='Create or update indicator. Indicator ID is retried from ClassName')
        parser_createUpdateIndicator.add_argument('-f', '--file', required=True, help='File path (with file name) that contains indicator code')
        parser_createUpdateIndicator.set_defaults(func=self.__createUpdateIndicator)

        while self.running:
            try:
                data = input("\ninvestfly-cli$ ")
                args = parser.parse_args(data.split())
                if args.command is None:
                    # When user hits Enter without any command
                    parser.print_help()
                else:
                    result = args.func(args)
                    if result is not None:
                        print(result)
            except SystemExit:
                # System exit is caught because when -h is used, argparser displays help and exists the apputils with SystemExit
                pass
            except KeyboardInterrupt:
                self.__exitAction(None)
            except Exception as e:
                print("Received exception " + str(e))



def main():
    investflyCli = InvestflyCli()
    investflyCli.runCli()

if __name__ == '__main__':
    main()
