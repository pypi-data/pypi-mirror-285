"""
pip install tweepy-self
python follow_each_other.py
"""

from itertools import cycle
import asyncio
from pathlib import Path
import random

import curl_cffi
from qg_toolkit.qtweepy import twitter
from qg_toolkit.tools.qproxy import Proxy

TWITTERS_TXT = Path("twitters.txt")
PROXIES_TXT = Path("proxies.txt")

for filepath in (
    TWITTERS_TXT,
    PROXIES_TXT,
):
    filepath.touch(exist_ok=True)


TWITTER_ACCOUNTS = qg_toolkit.qtweepy.twitter.account.load_accounts_from_file(TWITTERS_TXT)
PROXIES = Proxy.from_file(PROXIES_TXT)

if not PROXIES:
    PROXIES = [None]

CAPSOLVER_API_KEY = None  # 用于自动解锁
MAX_FOLLOWERS = 10


async def follow(proxy: Proxy, account: twitter.Account, user_id_to_follow: int):
    async with twitter.Client(
        account,
        proxy=proxy,
        capsolver_api_key=CAPSOLVER_API_KEY,
    ) as client:
        await client.follow(user_id_to_follow)
        print(f"{account} 已关注用户ID为 {user_id_to_follow}")


async def main():
    proxy_to_account_list = list(zip(cycle(PROXIES), TWITTER_ACCOUNTS))
    all_proxy_to_account_list = proxy_to_account_list.copy()
    random.shuffle(proxy_to_account_list)

    while proxy_to_account_list:
        proxy, account = proxy_to_account_list.pop(0)  # 类型: Proxy, twitter.Account

        async with twitter.Client(
            account,
            proxy=proxy,
            capsolver_api_key=CAPSOLVER_API_KEY,
        ) as client:
            try:
                me = await client.request_user()
                print(f"{me} 的关注者数量: {me.followers_count}")
                if me.followers_count >= MAX_FOLLOWERS:
                    continue

                proxy_to_account_list.append((proxy, account))
                await follow(*random.choice(all_proxy_to_account_list), me.id)
                await asyncio.sleep(5)

            except curl_cffi.requests.errors.RequestsError as exc:
                print(f"请求错误。可能是坏代理: {exc}")
                continue
            except Exception as exc:
                print(f"发生严重错误: {exc}")
                continue


if __name__ == "__main__":
    asyncio.run(main())
