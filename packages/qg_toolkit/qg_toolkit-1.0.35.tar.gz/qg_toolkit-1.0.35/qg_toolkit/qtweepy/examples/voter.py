"""
大规模投票的脚本
"""

import asyncio
from itertools import cycle
from pathlib import Path
from typing import Iterable

from qg_toolkit.qtweepy import twitter
from qg_toolkit.tools.qproxy import Proxy

TwitterAccountWithAdditionalData = tuple[str, twitter.Account]
SortedAccounts = dict[twitter.AccountStatus: TwitterAccountWithAdditionalData]

INPUT_OUTPUT_DIR = Path("input-output")
INPUT_OUTPUT_DIR.mkdir(exist_ok=True)

PROXIES_TXT = INPUT_OUTPUT_DIR / "PROXIES.txt"
ACCOUNTS_TXT = INPUT_OUTPUT_DIR / f"{twitter.AccountStatus.GOOD}.txt"
[filepath.touch() for filepath in (PROXIES_TXT, ACCOUNTS_TXT)]

MAX_TASKS = 100
SEPARATOR = ":"
FIELDS = ("auth_token", "password", "email", "username", "ct0")

# 要进行大规模投票，需要提取 tweet_id 和 card_id 参数。
# 您可以在投票推文页面的请求参数中找到它们。
TWEET_ID = 1701624723933905280
CARD_ID = 1701624722256236544
CHOICE_NUMBER = 1


async def vote(
        proxies: Iterable[Proxy],
        accounts: Iterable[twitter.Account],
        tweet_id: int,
        card_id: int,
        choice_number: int,
):

    if not proxies:
        proxies = [None]

    proxy_to_account_list = list(zip(cycle(proxies), accounts))

    for proxy, account in proxy_to_account_list:
        async with twitter.Client(account, proxy=proxy) as twitter_client:
            vote_data = await twitter_client.vote(tweet_id, card_id, choice_number)
            votes_count = vote_data["card"]["binding_values"]["choice1_count"]["string_value"]
            print(f"投票数：{votes_count}")


if __name__ == '__main__':
    proxies = Proxy.from_file(PROXIES_TXT)
    print(f"代理数量：{len(proxies)}")
    if not proxies:
        print(f"(可选) 在任何格式中添加代理 "
              f"\n\t到文件 {PROXIES_TXT}")

    accounts = qg_toolkit.qtweepy.twitter.account.load_accounts_from_file(ACCOUNTS_TXT)
    if not accounts:
        print(f"以 {SEPARATOR.join(FIELDS)} 格式添加帐户"
              f" (auth_token 为必填项，其他为可选项)"
              f"\n\t到文件 {ACCOUNTS_TXT}")
        quit()

    asyncio.run(vote(proxies, accounts, TWEET_ID, CARD_ID, CHOICE_NUMBER))
