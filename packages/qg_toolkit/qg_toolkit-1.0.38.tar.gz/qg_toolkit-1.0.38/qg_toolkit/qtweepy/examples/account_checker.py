"""
Скрипт для установки статуса Twitter аккаунтов (проверка на бан).
"""

import asyncio
import sys
from itertools import cycle
from pathlib import Path
from typing import Iterable

from loguru import logger

from curl_cffi import requests

from qg_toolkit import qtweepy
from qg_toolkit.qtweepy.twitter import *
from qg_toolkit.qtweepy.twitter.utils import load_lines, write_lines
from qg_toolkit.tools.qproxy import Proxy

LOGGING_LEVEL = "INFO"
logger.enable("twitter")
logger.remove()
logger.add(sys.stderr, level=LOGGING_LEVEL)


TwitterAccountWithAdditionalData = tuple[str, Account]
SortedAccounts = dict[AccountStatus : TwitterAccountWithAdditionalData]

INPUT_OUTPUT_DIR = Path("input-output")
INPUT_OUTPUT_DIR.mkdir(exist_ok=True)

PROXIES_TXT = INPUT_OUTPUT_DIR / "PROXIES.txt"
ACCOUNTS_TXT = INPUT_OUTPUT_DIR / f"{AccountStatus.UNKNOWN}.txt"
[filepath.touch() for filepath in (PROXIES_TXT, ACCOUNTS_TXT)]

SEPARATOR = ":"
MAX_TASKS = 10

CAPSOLVER_API_KEY = None  # To auto-unlock


async def limited_gather(tasks: list[asyncio.Task], limit: int = 100):
    semaphore = asyncio.Semaphore(limit)

    async def sem_task(task):
        async with semaphore:
            return await task

    await asyncio.gather(*(sem_task(task) for task in tasks))


def sort_accounts(
    accounts: Iterable[TwitterAccountWithAdditionalData],
) -> SortedAccounts:
    status_to_account_with_additional_data = {
        f'{status}': list() for status in qtweepy.twitter.AccountStatus
    }
    for additional_data, account in accounts:
        status_to_account_with_additional_data[account.status].append(
            (additional_data, account)
        )
    return status_to_account_with_additional_data


def save_sorted_accounts_with_additional_data(
    sorted_accounts: dict[AccountStatus : (str, Account)]
):
    for status, accounts_with_additional_data in sorted_accounts.items():
        filepath = INPUT_OUTPUT_DIR / f"{status}.txt"
        lines = [
            additional_data
            for additional_data, account in accounts_with_additional_data
        ]
        write_lines(filepath, lines)


def load_accounts_with_additional_data() -> list[TwitterAccountWithAdditionalData]:
    accounts = list()
    for file in INPUT_OUTPUT_DIR.iterdir():
        if file.is_file() and file.stem in AccountStatus.__members__:
            status = file.stem
            for additional_data in load_lines(file):
                auth_token = additional_data.split(SEPARATOR)[0]
                account = Account(auth_token=auth_token)
                account.status = status
                accounts.append((additional_data, account))
    return accounts


def print_statistic(sorted_accounts: SortedAccounts):
    for status, accounts_with_additional_data in sorted_accounts.items():
        print(f"{status}: {len(accounts_with_additional_data)}")


async def establish_account_status(account: Account, proxy: Proxy = None):
    async with Client(
        account, proxy=proxy, capsolver_api_key=CAPSOLVER_API_KEY
    ) as twitter_client:
        try:
            await twitter_client.establish_status()
        except requests.errors.RequestsError:
            pass

    print(f"{proxy.fixed_length} {account} {account.status}")


async def check_accounts(
    accounts: Iterable[TwitterAccountWithAdditionalData],
    proxies: Iterable[Proxy],
):
    sorted_accounts = sort_accounts(accounts)
    print_statistic(sorted_accounts)

    if not proxies:
        proxies = [None]

    proxy_to_account_list = list(zip(cycle(proxies), accounts))

    tasks = []
    for proxy, account_with_additional_data in proxy_to_account_list:
        account = account_with_additional_data[1]
        if account.status == AccountStatus.UNKNOWN.value:
            tasks.append(establish_account_status(account, proxy=proxy))
    try:
        await limited_gather(tasks, limit=MAX_TASKS)
    finally:
        sorted_accounts = sort_accounts(accounts)
        save_sorted_accounts_with_additional_data(sorted_accounts)
        print_statistic(sorted_accounts)


if __name__ == "__main__":
    proxies = Proxy.from_file(PROXIES_TXT)
    print(f"代理：{len(proxies)}")
    if not proxies:
        print(
            f"(可选) 请在以下文件中输入代理信息"
            f"\n\t路径：{PROXIES_TXT}"
        )

    accounts = load_accounts_with_additional_data()
    if not accounts:
        print(
            f"请在以下文件中输入账户信息"
            f"\n\t路径：{ACCOUNTS_TXT}"
            f"\n\t格式：auth_token:data1:data2:..."
            f"\n\t(auth_token 是必填项，data1、data2 等为账户其他信息)"
        )
        quit()

    asyncio.run(check_accounts(accounts, proxies))

