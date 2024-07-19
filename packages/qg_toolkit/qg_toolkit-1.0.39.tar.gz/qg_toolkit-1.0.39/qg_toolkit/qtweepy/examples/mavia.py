from itertools import cycle
import asyncio
from pathlib import Path

import curl_cffi
from qg_toolkit.qtweepy import twitter
from qg_toolkit.tools.qproxy import Proxy

TWITTERS_TXT = Path("twitters.txt")
PROXIES_TXT = Path("proxies.txt")
RESULTS_TXT = Path("results.txt")
DYM_MESSAGES_TXT = Path("dym_messages.txt")
MAVIA_MESSAGES_TXT = Path("mavia_messages.txt")

for filepath in (
    TWITTERS_TXT,
    PROXIES_TXT,
    RESULTS_TXT,
    DYM_MESSAGES_TXT,
    MAVIA_MESSAGES_TXT,
):
    filepath.touch(exist_ok=True)

SCREENSHOTS_DIR = Path("screenshots")

for dirpath in (SCREENSHOTS_DIR,):
    dirpath.mkdir(exist_ok=True)

TWITTER_ACCOUNTS = qg_toolkit.qtweepy.twitter.account.load_accounts_from_file(TWITTERS_TXT)
PROXIES = Proxy.from_file(PROXIES_TXT)

if not PROXIES:
    PROXIES = [None]

QUOT_MAVIA_TWEET_URL = "https://twitter.com/Bybit_Official/status/1754416124207181938"
QUOT_DYM_TWEET_URL = "https://twitter.com/Bybit_Official/status/1760246614252286288"
USER_IDS_TO_FOLLOW = [
    999947328621395968,  # https://twitter.com/Bybit_Official
    1451208655752282116,  # https://twitter.com/MaviaGame
    1506297383793176584,  # https://twitter.com/dymension
]


async def main():
    proxy_to_account_list = list(zip(cycle(PROXIES), TWITTER_ACCOUNTS))

    for (
        (proxy, twitter_account),
        dym_quote_message_text,
        mavia_quote_message_text,
        screenshot_path,
    ) in zip(
        proxy_to_account_list,
        open(DYM_MESSAGES_TXT, "r").readlines(),
        open(MAVIA_MESSAGES_TXT, "r").readlines(),
        SCREENSHOTS_DIR.iterdir(),
    ):  # 类型: (Proxy, twitter.Account), str, str, Path,
        async with twitter.Client(twitter_account, proxy=proxy) as twitter_client:
            try:
                # 关注用户
                for user_id in USER_IDS_TO_FOLLOW:
                    await twitter_client.follow(user_id)
                    print(f"{twitter_account} 关注了用户ID为 {user_id}")
                    await asyncio.sleep(3)

                # DYM推特
                dym_tweet = await twitter_client.quote(
                    QUOT_DYM_TWEET_URL, dym_quote_message_text
                )
                print(f"{twitter_account} 发布了引用推特 (DYM): {dym_tweet.url}")
                print(f"\t文本: {dym_tweet.text}")
                await asyncio.sleep(3)

                # Mavia推特
                image = open(screenshot_path, "rb").read()
                media_id = await twitter_client.upload_image(image)
                mavia_tweet = await twitter_client.quote(
                    QUOT_MAVIA_TWEET_URL,
                    mavia_quote_message_text,
                    media_id=media_id,
                )
                print(f"{twitter_account} 发布了引用推特 (MAVIA): {mavia_tweet.url}")
                print(f"\t文本: {mavia_tweet.text}")
                print(f"\t截图: {screenshot_path.stem}")
                await asyncio.sleep(3)

                with open(RESULTS_TXT, "a") as results_file:
                    results_file.write(
                        f"{twitter_account.auth_token},{screenshot_path.stem},{mavia_tweet.url},{dym_tweet.url}\n"
                    )

            except curl_cffi.requests.errors.RequestsError as exc:
                print(f"请求错误。可能是坏代理: {exc}")
                continue
            except Exception as exc:
                print(f"发生严重错误: {exc}")
                continue


if __name__ == "__main__":
    asyncio.run(main())
