import base64
import hashlib
import os
import random
import urllib.parse
from datetime import datetime, timedelta
from itertools import chain, groupby
from threading import Lock
from typing import Optional
from urllib.parse import parse_qs, urlparse

import requests
from Crypto.Cipher import AES
from bs4 import BeautifulSoup
from web3 import Web3
from web3.auto import w3

from qg_toolkit.qgalxe.GeetestFullPageV4_1 import GeetestFullPageV4SyncWrapper
from qg_toolkit.tools.cui_qiu_client import CuiQiuClient
from qg_toolkit.tools.discord import QDiscord
from qg_toolkit.tools.qg_eth import QGEth
from qg_toolkit.tools.qg_file import QGFile
from qg_toolkit.tools.random_tool import RandomGenerator
from qg_toolkit.tools.twitter import QTwitter


class Galxe(QGEth):
    bsc_balance: Optional[float]
    bsc_w3: Optional[Web3]
    lock = Lock()

    def __init__(self, space, twitter_info=None, dis_info=None, ref_code="", *args, **kwargs):
        # 取破解参数
        # "\u0077"    encrypt_query
        # window.initGeetest4({captchaId: "244bcb8b9846215df5af4c624a750db4", product: "bind"})
        # JSON.stringify(e)
        super().__init__(**kwargs)
        if dis_info is None:
            dis_info = {}
        if twitter_info is None:
            twitter_info = {}
        self.twitter_info = twitter_info
        self.dis_info = dis_info
        self.gt = None
        self.ans = {}
        self.space = space
        self.campaigns = []
        self.ref_code = ref_code
        self.userinfo = {}
        self.headers = {
            'authority': 'graphigo.prd.galaxy.eco',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://galxe.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        self.galxe_session = requests.Session()
        self.galxe_session.headers.update(self.headers)
        self.dis_session = requests.Session()
        self.cq_client = CuiQiuClient()
        self.q_twitter: Optional[QTwitter] = None
        self.q_discord: Optional[QDiscord] = None
        self.social_init()

    def social_init(self):
        if self.twitter_info:
            self.q_twitter = QTwitter(index=self.index, username=self.twitter_info.get("username"),token_info=self.twitter_info)
        if self.dis_info:
            self.q_discord = QDiscord(index=self.index, token=self.dis_info.get("token"))
        self.gt = GeetestFullPageV4SyncWrapper()
        # self.gt = QGeetestV4("244bcb8b9846215df5af4c624a750db4")

    def do_galaxy_task(self):
        # 获取整个空间下所有任务，分组自动展开并全统计
        tasks = self.get_space_campaigns()
        # 做整个任务
        self.do_task_item(tasks)
        # 验证所有分组任务(按分组进行验证)
        self.verify_group_task(tasks)
        # 获取某个项目的总得分
        self.get_space_total_score()

    def galaxy_login(self):
        nonce = self.random_str(17)
        # 获取当前时间
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        # 增加一天时间
        tom = (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        msg = f'galxe.com wants you to sign in with your Ethereum account:\n{self.address}\n\nSign in with Ethereum to the app.\n\nURI: https://galxe.com\nVersion: 1\nChain ID: 1\nNonce: {nonce}\nIssued At: {now}\nExpiration Time: {tom}\nNot Before: {tom}'
        signature = self.sign_msg(w3, msg)
        json_data = {
            'operationName': 'SignIn',
            'variables': {
                'input': {
                    'address': self.address,
                    'message': msg,
                    'signature': signature,
                },
            },
            'query': 'mutation SignIn($input: Auth) {\n  signin(input: $input)\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        # print(response.text)
        self.galxe_session.headers.update({"authorization": response.json()['data']['signin']})
        print(f"【{self.index}】【{self.address}】登录成功！")
        # self.get_userinfo()
        return True

    def get_userinfo(self):
        json_data = {
            'operationName': 'AddressInfo',
            'variables': {
                'address': f'{self.address}',
                'listSpaceInput': {
                    'first': 30,
                },
            },
            'query': 'query AddressInfo($address: String!, $listSpaceInput: ListSpaceInput!) {\n  addressInfo(address: $address) {\n    id\n    address\n    solanaAddress\n    aptosAddress\n    seiAddress\n    hasEvmAddress\n    hasSolanaAddress\n    hasAptosAddress\n    hasEmail\n    avatar\n    username\n    hasTwitter\n    hasGithub\n    hasDiscord\n    hasTelegram\n    displayEmail\n    displayTwitter\n    displayGithub\n    displayDiscord\n    displayTelegram\n    isWhitelisted\n    isInvited\n    email\n    twitterUserID\n    twitterUserName\n    githubUserID\n    isVerifiedTwitterOauth2\n    isVerifiedDiscordOauth2\n    enableEmailSubs\n    displayNamePref\n    githubUserName\n    discordUserID\n    discordUserName\n    telegramUserID\n    telegramUserName\n    subscriptions\n    passport {\n      status\n      pendingRedactAt\n      id\n      __typename\n    }\n    passportPendingRedactAt\n    isAdmin\n    spaces(input: $listSpaceInput) {\n      list {\n        ...SpaceBasicFrag\n        __typename\n      }\n      __typename\n    }\n    private {\n      email\n      twitterUserName\n      twitterUserID\n      discordUserID\n      discordUserName\n      githubUserID\n      githubUserName\n      telegramUserID\n      telegramUserName\n      accessToken\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SpaceBasicFrag on Space {\n  id\n  name\n  info\n  thumbnail\n  alias\n  links\n  isVerified\n  status\n  followersCount\n  __typename\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        # print(response.text)
        if response.status_code == 200:
            self.userinfo = response.json()['data']['addressInfo']
        if not self.userinfo["id"]:
            json_data = {
                'operationName': 'CreateNewAccount',
                'variables': {
                    'input': {
                        'schema': f'EVM:{self.address.lower()}',
                        'socialUsername': '',
                        'username': f'{RandomGenerator.generate_random_str(6)}',
                    },
                },
                'query': 'mutation CreateNewAccount($input: CreateNewAccount!) {\n  createNewAccount(input: $input)\n}\n',
            }
            response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
            print(f'【{self.address}】【{self.index}】创建galxe用户：{response.text}')
            self.get_userinfo()

    def init_twitter(self):
        twitter_username = self.userinfo["twitterUserName"]
        if twitter_username == self.twitter_info.get("username"):
            self.q_twitter = QTwitter(index=self.index, username=self.twitter_info.get("username"),
                                      token_info=self.twitter_info)
            # self.q_twitter.init_by_token()

    def get_captcha_by_qg(self):
        solution = self.gt.generate_captcha()
        # print('Geetest V4打码成功:', solution)
        return solution

    # @staticmethod
    # def get_captcha_by_2captcha():
    #     from unicaps import CaptchaSolver, CaptchaSolvingService
    #     page_url = 'https://galxe.com'
    #     captcha_id = '244bcb8b9846215df5af4c624a750db4'
    #     # init captcha solver
    #     with CaptchaSolver(CaptchaSolvingService.TWOCAPTCHA, "e98238e67a43771a1fb1ef1c897a8f6c") as solver:
    #         # solve CAPTCHA
    #         solved = solver.solve_geetest_v4(
    #             page_url=page_url,
    #             captcha_id=captcha_id
    #         )
    #         # get solution data
    #         # lot_number = solved.solution.lot_number
    #         # pass_token = solved.solution.pass_token
    #         # gen_time = solved.solution.gen_time
    #         # captcha_output = solved.solution.captcha_output
    #         return solved.solution

    def get_space_campaigns(self):
        json_data = {
            'operationName': 'BrowseSpaceCampaignsQuery',
            'variables': {
                'alias': f'{self.space}',
                'address': f'{self.address}',
                'campaignInput': {
                    'forAdmin': False,
                    'first': 20,
                    'after': '-1',
                    'excludeChildren': True,
                    'listType': 'Newest',
                    'gasTypes': None,
                    'credSources': None,
                    'types': [
                        'Drop',
                        'MysteryBox',
                        'Forge',
                        'MysteryBoxWR',
                        'Airdrop',
                        'ExternalLink',
                        'OptIn',
                        'OptInEmail',
                        'PowahDrop',
                        'Parent',
                        'Oat',
                        'Bounty',
                        'Token',
                        'DiscordRole',
                        'Mintlist',
                        'Points',
                        'PointsMysteryBox',
                    ],
                    'rewardTypes': None,
                    'chains': None,
                    'statuses': None,
                    'searchString': None,
                },
            },
            'query': 'query BrowseSpaceCampaignsQuery($id: Int, $alias: String, $address: String!, $campaignInput: ListCampaignInput!) {\n  space(id: $id, alias: $alias) {\n    id\n    name\n    alias\n    campaigns(input: $campaignInput) {\n      pageInfo {\n        endCursor\n        hasNextPage\n        __typename\n      }\n      list {\n        ...FragSpaceCampaignBrowse\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment ChildrenForCampaignBtn on Campaign {\n  childrenCampaigns {\n    gamification {\n      nfts {\n        nft {\n          nftCore {\n            contractAddress\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignCredBasic on Cred {\n  id\n  eligible(address: $address)\n  name\n  credSource\n  credType\n  __typename\n}\n\nfragment RewardBasic on ExprReward {\n  arithmeticFormula\n  rewardType\n  __typename\n}\n\nfragment CredentialRewardBasic on CredentialGroupReward {\n  expression\n  rewardType\n  __typename\n}\n\nfragment BrowseCard on Campaign {\n  id\n  numberID\n  name\n  requirementInfo\n  formula\n  gamification {\n    id\n    type\n    __typename\n  }\n  creds {\n    ...CampaignCredBasic\n    __typename\n  }\n  taskConfig(address: $address) {\n    rewardConfigs {\n      rewards {\n        ...RewardBasic\n        __typename\n      }\n      conditionalFormula\n      conditions {\n        attrs {\n          attrName\n          operatorSymbol\n          targetValue\n          __typename\n        }\n        eligible\n        cred {\n          ...CampaignCredBasic\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    participateCondition {\n      conditionalFormula\n      conditions {\n        attrs {\n          attrName\n          operatorSymbol\n          targetValue\n          __typename\n        }\n        eligible\n        cred {\n          ...CampaignCredBasic\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  recurringType\n  endTime\n  latestRecurringTime\n  useCred\n  credentialGroups(address: $address) {\n    id\n    description\n    rewards {\n      ...CredentialRewardBasic\n      __typename\n    }\n    credentials {\n      ...CampaignCredBasic\n      __typename\n    }\n    conditionRelation\n    conditions {\n      expression\n      eligible\n      __typename\n    }\n    __typename\n  }\n  participants {\n    participantsCount\n    __typename\n  }\n  ...CardMedia\n  ...CampaignTag\n  __typename\n}\n\nfragment CardMedia on Campaign {\n  thumbnail\n  type\n  name\n  rewardType\n  status\n  cap\n  gamification {\n    type\n    __typename\n  }\n  tokenReward {\n    tokenAddress\n    userTokenAmount\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  tokenRewardContract {\n    chain\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildName\n      roleName\n      __typename\n    }\n    __typename\n  }\n  participants {\n    bountyWinnersCount\n    participantsCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignTag on Campaign {\n  loyaltyPoints\n  rewardName\n  type\n  gamification {\n    type\n    __typename\n  }\n  cap\n  tokenReward {\n    tokenAddress\n    userTokenAmount\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  tokenRewardContract {\n    chain\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      roleName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ChildrenForCardMedia on Campaign {\n  childrenCampaigns {\n    type\n    name\n    rewardName\n    rewardInfo {\n      discordRole {\n        roleName\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment FragSpaceCampaignBrowse on Campaign {\n  ...CampaignForClaimInfo\n  ...CampaignForClaimButton\n  ...BrowseCard\n  ...ChildrenForCampaignBtn\n  ...ChildrenForCardMedia\n  ...CampaignForCredBox\n  childrenCampaigns {\n    ...BrowseCard\n    ...CampaignForClaimInfo\n    ...CampaignForClaimButton\n    ...CampaignForCredBox\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCustomRaffleButton on Campaign {\n  userParticipants(address: $address, first: 1) {\n    list {\n      status\n      premintTo\n      __typename\n    }\n    __typename\n  }\n  startTime\n  endTime\n  __typename\n}\n\nfragment CampaignForTokenRaffleButton on Campaign {\n  ...CampaignForCustomRaffleButton\n  claimEndTime\n  __typename\n}\n\nfragment CampaignForClaimButton on Campaign {\n  ...CampaignForCustomRaffleButton\n  ...CampaignForTokenRaffleButton\n  ...CampaignForIsGaslessOutOfBalance\n  ...CampaignForClaim\n  ...CampaignForIsLock\n  startTime\n  endTime\n  type\n  distributionType\n  claimEndTime\n  gasType\n  chain\n  tokenReward {\n    tokenAddress\n    userTokenAmount\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  tokenRewardContract {\n    chain\n    __typename\n  }\n  rewardName\n  gamification {\n    nfts {\n      nft {\n        nftCore {\n          chain\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  whitelistInfo(address: $address) {\n    maxCount\n    usedCount\n    __typename\n  }\n  userParticipants(address: $address, first: 1) {\n    list {\n      status\n      premintTo\n      __typename\n    }\n    __typename\n  }\n  dao {\n    alias\n    __typename\n  }\n  parentCampaign {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForIsGaslessOutOfBalance on Campaign {\n  ...CampaignForCheckSufficientForGaslessChain\n  chain\n  __typename\n}\n\nfragment CampaignForCheckSufficientForGaslessChain on Campaign {\n  chain\n  space {\n    id\n    __typename\n  }\n  dao {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForPrepareParticipateMutate on Campaign {\n  id\n  chain\n  __typename\n}\n\nfragment CampaignForClaimCustomReward on Campaign {\n  ...CampaignForPrepareParticipateMutate\n  rewardType\n  chain\n  __typename\n}\n\nfragment CampaignForClaimDiscordRole on Campaign {\n  ...CampaignForPrepareParticipateMutate\n  space {\n    discordGuildID\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForClaimPoints on Campaign {\n  ...CampaignForPrepareParticipateMutate\n  chain\n  __typename\n}\n\nfragment CampaignForClaimToken on Campaign {\n  ...CampaignForPrepareParticipateMutate\n  id\n  numberID\n  endTime\n  distributionType\n  tokenRewardContract {\n    address\n    __typename\n  }\n  chain\n  __typename\n}\n\nfragment CampaignForClaimNftGasless on Campaign {\n  ...CampaignForPrepareParticipateMutate\n  id\n  name\n  chain\n  gamification {\n    nfts {\n      nft {\n        nftCore {\n          chain\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForClaimNftGas on Campaign {\n  ...CampaignForPrepareParticipateMutate\n  id\n  numberID\n  spaceStation {\n    address\n    chain\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForClaim on Campaign {\n  ...CampaignForClaimCustomReward\n  ...CampaignForClaimDiscordRole\n  ...CampaignForClaimToken\n  ...CampaignForClaimNftGasless\n  ...CampaignForClaimNftGas\n  ...CampaignForClaimSeiNFT\n  ...CampaignForClaimPoints\n  ...CampaignForIsGaslessOutOfBalance\n  type\n  gasType\n  __typename\n}\n\nfragment CampaignForClaimSeiNFT on Campaign {\n  id\n  numberID\n  __typename\n}\n\nfragment CampaignForIsLock on Campaign {\n  id\n  parentCampaign {\n    id\n    isSequencial\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCalcCampaigClaimNFT on Campaign {\n  ...CampaignForCalcCampaignCanClaim\n  type\n  whitelistInfo(address: $address) {\n    usedCount\n    __typename\n  }\n  credentialGroups(address: $address) {\n    rewards {\n      rewardType\n      rewardCount\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCalcCampaignCanClaim on Campaign {\n  distributionType\n  cap\n  __typename\n}\n\nfragment CampaignForCalcCampaigClaimCommon on Campaign {\n  type\n  whitelistInfo(address: $address) {\n    usedCount\n    maxCount\n    __typename\n  }\n  credentialGroups(address: $address) {\n    rewards {\n      rewardType\n      rewardCount\n      __typename\n    }\n    __typename\n  }\n  ...CampaignForCalcCampaignCanClaim\n  ...CampaignForIsRaffleParticipateEnded\n  __typename\n}\n\nfragment CampaignForCalcCampaigClaimToken on Campaign {\n  ...CampaignForCalcCampaigClaimCommon\n  __typename\n}\n\nfragment CampaignForCalcCampaigClaimPoints on Campaign {\n  type\n  loyaltyPoints\n  credentialGroups(address: $address) {\n    rewards {\n      rewardType\n      rewardCount\n      __typename\n    }\n    __typename\n  }\n  whitelistInfo(address: $address) {\n    claimedLoyaltyPoints\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForIsRaffleParticipateEnded on Campaign {\n  endTime\n  __typename\n}\n\nfragment CampaignForClaimInfo on Campaign {\n  ...CampaignForCalcCampaigClaimNFT\n  ...CampaignForCalcCampaigClaimCommon\n  ...CampaignForCalcCampaigClaimToken\n  ...CampaignForCalcCampaigClaimPoints\n  ...CampaignAsCampaignParticipants\n  gasType\n  __typename\n}\n\nfragment CampaignAsCampaignParticipants on Campaign {\n  numNFTMinted\n  participants {\n    participantsCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCredBox on Campaign {\n  id\n  type\n  latestRecurringTime\n  recurringType\n  gamification {\n    type\n    __typename\n  }\n  taskConfig(address: $address) {\n    participateCondition {\n      ...ParticipateConditionForCredBox\n      eligible\n      __typename\n    }\n    rewardConfigs {\n      ...RewardConfigForCredBox\n      eligible\n      __typename\n    }\n    __typename\n  }\n  endTime\n  ...CampaignForCredItem\n  credentialGroups(address: $address) {\n    ...CredentialGroupForCredBox\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCredItem on Campaign {\n  ...CampaignForVerifyButton\n  ...CampaignForCredGoTaskButton\n  ...CampaignForCredConnectSocialButton\n  creds {\n    ...CredForCredItem\n    __typename\n  }\n  recurringType\n  numberID\n  endTime\n  __typename\n}\n\nfragment CampaignForVerifyButton on Campaign {\n  id\n  numberID\n  credentialGroups(address: $address) {\n    id\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCredGoTaskButton on Campaign {\n  id\n  name\n  numberID\n  __typename\n}\n\nfragment CampaignForCredConnectSocialButton on Campaign {\n  id\n  numberID\n  name\n  __typename\n}\n\nfragment CredForCredItem on Cred {\n  id\n  eligible(address: $address)\n  credSource\n  credType\n  name\n  ...CredForVerifyButton\n  ...CredForCredGoTaskButton\n  ...CredForCredConnectSocialButton\n  type\n  description\n  __typename\n}\n\nfragment CredForVerifyButton on Cred {\n  id\n  type\n  eligible(address: $address)\n  credSource\n  lastUpdate\n  credContractNFTHolder {\n    timestamp\n    __typename\n  }\n  __typename\n}\n\nfragment CredForCredGoTaskButton on Cred {\n  id\n  credSource\n  referenceLink\n  type\n  metadata {\n    visitLink {\n      link\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CredForCredConnectSocialButton on Cred {\n  type\n  credType\n  credSource\n  id\n  __typename\n}\n\nfragment CredentialGroupForCredBox on CredentialGroup {\n  id\n  description\n  credentials {\n    ...CredForCredItem\n    __typename\n  }\n  rewardAttrVals {\n    ...RewardAttrValForCredItem\n    __typename\n  }\n  conditions {\n    expression\n    ...CredentialGroupConditionForCredItem\n    __typename\n  }\n  conditionRelation\n  rewards {\n    expression\n    rewardType\n    __typename\n  }\n  __typename\n}\n\nfragment RewardAttrValForCredItem on RewardAttrVal {\n  attrName\n  attrTitle\n  __typename\n}\n\nfragment CredentialGroupConditionForCredItem on CredentialGroupCondition {\n  ...CredentialGroupConditionForVerifyButton\n  expression\n  __typename\n}\n\nfragment CredentialGroupConditionForVerifyButton on CredentialGroupCondition {\n  expression\n  __typename\n}\n\nfragment ParticipateConditionForCredBox on ParticipateCondition {\n  conditions {\n    ...ExprEntityForCredItem\n    __typename\n  }\n  __typename\n}\n\nfragment ExprEntityForCredItem on ExprEntity {\n  cred {\n    ...CredForCredItem\n    __typename\n  }\n  attrs {\n    attrName\n    operatorSymbol\n    targetValue\n    __typename\n  }\n  __typename\n}\n\nfragment RewardConfigForCredBox on RewardConfig {\n  rewardAttrVals {\n    attrName\n    __typename\n  }\n  conditions {\n    ...ExprEntityForCredItem\n    __typename\n  }\n  __typename\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        self.campaigns = response.json()["data"]["space"]["campaigns"]["list"]
        self.space_info = self.campaigns[0]["space"]
        # 所有分组任务
        credential_groups = []
        for campaign in self.campaigns:
            credential_groups.append(self.campaign_wrap(campaign))
        # 所有子任务
        credentials = list(chain.from_iterable(credential_groups))
        print(credentials)
        # 筛选有效任务
        credentials = [x for x in credentials if x['status'] == 'Active']
        return credentials

    def get_space_campaigns_v2(self):
        json_data = {
            'operationName': 'SpaceCampaignsMetricQuery',
            'variables': {
                'alias': f'{self.space}',
                'address': f'{self.address}',
                'campaignInput': {
                    'first': 25,
                    'forAdmin': False,
                    'after': '-1',
                },
            },
            'query': 'query SpaceCampaignsMetricQuery($id: Int, $alias: String, $address: String!, $campaignInput: ListCampaignInput!) {\n  space(id: $id, alias: $alias) {\n    id\n    campaigns(input: $campaignInput) {\n      list {\n        nftCore {\n          id\n          __typename\n        }\n        ...SpaceCampaignBasic\n        info\n        referralCode(address: $address)\n        metrics\n        childrenCampaigns {\n          nftCore {\n            id\n            __typename\n          }\n          ...SpaceCampaignBasic\n          info\n          metrics\n          gamification {\n            id\n            type\n            __typename\n          }\n          __typename\n        }\n        gamification {\n          id\n          type\n          __typename\n        }\n        __typename\n      }\n      pageInfo {\n        hasNextPage\n        endCursor\n        __typename\n      }\n      totalCount\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SpaceBasic on Space {\n  id\n  name\n  thumbnail\n  alias\n  isVerified\n  info\n  links\n  status\n  followersCount\n  followersRank\n  backers\n  categories\n  token\n  discordGuildID\n  discordGuildInfo\n  banner\n  seoImage\n  __typename\n}\n\nfragment SpaceCampaignBasic on Campaign {\n  id\n  name\n  description\n  thumbnail\n  startTime\n  endTime\n  status\n  formula\n  cap\n  gasType\n  isPrivate\n  type\n  loyaltyPoints\n  tokenRewardContract {\n    id\n    address\n    chain\n    __typename\n  }\n  tokenReward {\n    userTokenAmount\n    tokenAddress\n    depositedTokenAmount\n    tokenRewardId\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  numberID\n  chain\n  rewardName\n  ...SpaceCampaignMedia\n  space {\n    ...SpaceBasic\n    __typename\n  }\n  credentialGroups(address: $address) {\n    ...CredentialGroupForAddress\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildId\n      guildName\n      roleId\n      roleName\n      inviteLink\n      __typename\n    }\n    premint {\n      startTime\n      endTime\n      chain\n      price\n      totalSupply\n      contractAddress\n      banner\n      __typename\n    }\n    __typename\n  }\n  participants {\n    participantsCount\n    bountyWinnersCount\n    __typename\n  }\n  recurringType\n  latestRecurringTime\n  ...WhitelistInfoFrag\n  creds {\n    ...CredForAddress\n    __typename\n  }\n  taskConfig(address: $address) {\n    participateCondition {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      eligible\n      __typename\n    }\n    rewardConfigs {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      eligible\n      rewards {\n        arithmeticFormula\n        rewardType\n        rewardCount\n        rewardVal\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SpaceCampaignMedia on Campaign {\n  thumbnail\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupForAddress on CredentialGroup {\n  id\n  description\n  credentials {\n    ...CredForAddressWithoutMetadata\n    __typename\n  }\n  conditionRelation\n  conditions {\n    expression\n    eligible\n    ...CredentialGroupConditionForVerifyButton\n    __typename\n  }\n  rewards {\n    expression\n    eligible\n    rewardCount\n    rewardType\n    __typename\n  }\n  rewardAttrVals {\n    attrName\n    attrTitle\n    attrVal\n    __typename\n  }\n  claimedLoyaltyPoints\n  __typename\n}\n\nfragment CredForAddressWithoutMetadata on Cred {\n  id\n  name\n  type\n  credType\n  credSource\n  referenceLink\n  description\n  lastUpdate\n  lastSync\n  syncStatus\n  credContractNFTHolder {\n    timestamp\n    __typename\n  }\n  chain\n  eligible(address: $address)\n  subgraph {\n    endpoint\n    query\n    expression\n    __typename\n  }\n  dimensionConfig\n  value {\n    gitcoinPassport {\n      score\n      lastScoreTimestamp\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupConditionForVerifyButton on CredentialGroupCondition {\n  expression\n  eligibleAddress\n  __typename\n}\n\nfragment WhitelistInfoFrag on Campaign {\n  id\n  whitelistInfo(address: $address) {\n    address\n    maxCount\n    usedCount\n    claimedLoyaltyPoints\n    currentPeriodClaimedLoyaltyPoints\n    currentPeriodMaxLoyaltyPoints\n    __typename\n  }\n  __typename\n}\n\nfragment ExpressionEntity on ExprEntity {\n  cred {\n    id\n    name\n    type\n    credType\n    credSource\n    dimensionConfig\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    chain\n    eligible(address: $address)\n    metadata {\n      visitLink {\n        link\n        __typename\n      }\n      twitter {\n        isAuthentic\n        __typename\n      }\n      worldcoin {\n        dimensions {\n          values {\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  attrs {\n    attrName\n    operatorSymbol\n    targetValue\n    __typename\n  }\n  attrFormula\n  eligible\n  eligibleAddress\n  __typename\n}\n\nfragment CredForAddress on Cred {\n  ...CredForAddressWithoutMetadata\n  metadata {\n    ...CredMetaData\n    __typename\n  }\n  dimensionConfig\n  value {\n    gitcoinPassport {\n      score\n      lastScoreTimestamp\n      __typename\n    }\n    __typename\n  }\n  commonInfo {\n    participateEndTime\n    modificationInfo\n    __typename\n  }\n  __typename\n}\n\nfragment CredMetaData on CredMetadata {\n  visitLink {\n    link\n    __typename\n  }\n  social {\n    socialAccountType\n    socialValueType\n    dimensions {\n      id\n      type\n      title\n      description\n      config\n      values {\n        name\n        type\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  gitcoinPassport {\n    score {\n      title\n      type\n      description\n      config\n      __typename\n    }\n    lastScoreTimestamp {\n      title\n      type\n      description\n      config\n      __typename\n    }\n    __typename\n  }\n  campaignReferral {\n    count {\n      title\n      type\n      description\n      config\n      __typename\n    }\n    __typename\n  }\n  galxeScore {\n    dimensions {\n      id\n      type\n      title\n      description\n      config\n      values {\n        name\n        type\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  twitter {\n    twitterID\n    campaignID\n    isAuthentic\n    __typename\n  }\n  restApi {\n    url\n    method\n    headers {\n      key\n      value\n      __typename\n    }\n    postBody\n    expression\n    __typename\n  }\n  walletBalance {\n    contractAddress\n    snapshotTimestamp\n    chain\n    balance {\n      type\n      title\n      description\n      config\n      __typename\n    }\n    LastSyncBlock\n    LastSyncTimestamp\n    __typename\n  }\n  lensProfileFollow {\n    handle\n    __typename\n  }\n  graphql {\n    url\n    query\n    expression\n    __typename\n  }\n  lensPostUpvote {\n    postId\n    __typename\n  }\n  lensPostMirror {\n    postId\n    __typename\n  }\n  multiDimensionRest {\n    url\n    method\n    headers {\n      key\n      value\n      __typename\n    }\n    postBody\n    expression\n    dimensions {\n      id\n      type\n      title\n      description\n      config\n      __typename\n    }\n    __typename\n  }\n  nftHolder {\n    contractNftHolder {\n      chain\n      contract\n      timestamp\n      __typename\n    }\n    campaignNftHolder {\n      campaignId\n      timestamp\n      __typename\n    }\n    dynamicCampaignNftHolder {\n      campaign {\n        id\n        __typename\n      }\n      __typename\n    }\n    dynamicContractNftHolder {\n      chain\n      contract\n      __typename\n    }\n    __typename\n  }\n  discord {\n    discordAma {\n      guildId\n      channelId\n      startTime\n      endTime\n      eligibleDuration\n      __typename\n    }\n    discordMember {\n      guildId\n      roles {\n        RoleId\n        RoleName\n        __typename\n      }\n      __typename\n    }\n    discordMessage {\n      guildName\n      channelId\n      guildId\n      channelName\n      daysCount\n      __typename\n    }\n    __typename\n  }\n  multiDimensionGraphql {\n    url\n    query\n    expression\n    dimensions {\n      id\n      type\n      title\n      description\n      config\n      __typename\n    }\n    __typename\n  }\n  contractQuery {\n    url\n    chainName\n    abi\n    method\n    headers {\n      key\n      value\n      __typename\n    }\n    contractMethod\n    contractAddress\n    block\n    inputData\n    inputs {\n      name\n      type\n      value\n      __typename\n    }\n    dimensions {\n      id\n      type\n      config\n      description\n      title\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        self.campaigns = response.json()["data"]["space"]["campaigns"]["list"]
        self.space_info = self.campaigns[0]["space"]
        # 所有分组任务
        credential_groups = []
        for campaign in self.campaigns:
            credential_groups.append(self.campaign_wrap(campaign))
        # 所有子任务
        credentials = list(chain.from_iterable(credential_groups))
        print(credentials)
        # 筛选有效任务
        credentials = [x for x in credentials if x['status'] == 'Active']
        return credentials

    def get_task_detail(self, campaign_id):
        json_data = {
            'operationName': 'CampaignDetailAll',
            'variables': {
                'address': f'{self.address}',
                'id': f'{campaign_id}',
                'withAddress': True,
            },
            'query': 'query CampaignDetailAll($id: ID!, $address: String!, $withAddress: Boolean!) {\n  campaign(id: $id) {\n    ...CampaignForSiblingSlide\n    coHostSpaces {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    bannerUrl\n    ...CampaignDetailFrag\n    userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n      list {\n        status\n        premintTo\n        __typename\n      }\n      __typename\n    }\n    space {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    isBookmarked(address: $address) @include(if: $withAddress)\n    inWatchList\n    claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n    parentCampaign {\n      id\n      isSequencial\n      thumbnail\n      __typename\n    }\n    isSequencial\n    numNFTMinted\n    childrenCampaigns {\n      ...ChildrenCampaignsForCampaignDetailAll\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CampaignDetailFrag on Campaign {\n  id\n  ...CampaignMedia\n  ...CampaignForgePage\n  ...CampaignForCampaignParticipantsBox\n  name\n  numberID\n  type\n  inWatchList\n  cap\n  info\n  useCred\n  smartbalancePreCheck(mintCount: 1)\n  smartbalanceDeposited\n  formula\n  status\n  seoImage\n  creator\n  tags\n  thumbnail\n  gasType\n  isPrivate\n  createdAt\n  requirementInfo\n  description\n  enableWhitelist\n  chain\n  startTime\n  endTime\n  requireEmail\n  requireUsername\n  blacklistCountryCodes\n  whitelistRegions\n  rewardType\n  distributionType\n  rewardName\n  claimEndTime\n  loyaltyPoints\n  tokenRewardContract {\n    id\n    address\n    chain\n    __typename\n  }\n  tokenReward {\n    userTokenAmount\n    tokenAddress\n    depositedTokenAmount\n    tokenRewardId\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  spaceStation {\n    id\n    address\n    chain\n    __typename\n  }\n  ...WhitelistInfoFrag\n  ...WhitelistSubgraphFrag\n  gamification {\n    ...GamificationDetailFrag\n    __typename\n  }\n  creds {\n    id\n    name\n    type\n    credType\n    credSource\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    syncStatus\n    credContractNFTHolder {\n      timestamp\n      __typename\n    }\n    chain\n    eligible(address: $address, campaignId: $id)\n    subgraph {\n      endpoint\n      query\n      expression\n      __typename\n    }\n    dimensionConfig\n    value {\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  credentialGroups(address: $address) {\n    ...CredentialGroupForAddress\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildId\n      guildName\n      roleId\n      roleName\n      inviteLink\n      __typename\n    }\n    premint {\n      startTime\n      endTime\n      chain\n      price\n      totalSupply\n      contractAddress\n      banner\n      __typename\n    }\n    loyaltyPoints {\n      points\n      __typename\n    }\n    loyaltyPointsMysteryBox {\n      points\n      weight\n      __typename\n    }\n    __typename\n  }\n  participants {\n    participantsCount\n    bountyWinnersCount\n    __typename\n  }\n  taskConfig(address: $address) {\n    participateCondition {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      eligible\n      __typename\n    }\n    rewardConfigs {\n      id\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    referralConfig {\n      id\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  referralCode(address: $address)\n  recurringType\n  latestRecurringTime\n  nftTemplates {\n    id\n    image\n    treasureBack\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignMedia on Campaign {\n  thumbnail\n  rewardName\n  type\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupForAddress on CredentialGroup {\n  id\n  description\n  credentials {\n    ...CredForAddressWithoutMetadata\n    __typename\n  }\n  conditionRelation\n  conditions {\n    expression\n    eligible\n    ...CredentialGroupConditionForVerifyButton\n    __typename\n  }\n  rewards {\n    expression\n    eligible\n    rewardCount\n    rewardType\n    __typename\n  }\n  rewardAttrVals {\n    attrName\n    attrTitle\n    attrVal\n    __typename\n  }\n  claimedLoyaltyPoints\n  __typename\n}\n\nfragment CredForAddressWithoutMetadata on Cred {\n  id\n  name\n  type\n  credType\n  credSource\n  referenceLink\n  description\n  lastUpdate\n  lastSync\n  syncStatus\n  credContractNFTHolder {\n    timestamp\n    __typename\n  }\n  chain\n  eligible(address: $address)\n  subgraph {\n    endpoint\n    query\n    expression\n    __typename\n  }\n  dimensionConfig\n  value {\n    gitcoinPassport {\n      score\n      lastScoreTimestamp\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupConditionForVerifyButton on CredentialGroupCondition {\n  expression\n  eligibleAddress\n  __typename\n}\n\nfragment WhitelistInfoFrag on Campaign {\n  id\n  whitelistInfo(address: $address) {\n    address\n    maxCount\n    usedCount\n    claimedLoyaltyPoints\n    currentPeriodClaimedLoyaltyPoints\n    currentPeriodMaxLoyaltyPoints\n    __typename\n  }\n  __typename\n}\n\nfragment WhitelistSubgraphFrag on Campaign {\n  id\n  whitelistSubgraph {\n    query\n    endpoint\n    expression\n    variable\n    __typename\n  }\n  __typename\n}\n\nfragment GamificationDetailFrag on Gamification {\n  id\n  type\n  nfts {\n    nft {\n      id\n      animationURL\n      category\n      powah\n      image\n      name\n      treasureBack\n      nftCore {\n        ...NftCoreInfoFrag\n        __typename\n      }\n      traits {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  airdrop {\n    name\n    contractAddress\n    token {\n      address\n      icon\n      symbol\n      __typename\n    }\n    merkleTreeUrl\n    addressInfo(address: $address) {\n      index\n      amount {\n        amount\n        ether\n        __typename\n      }\n      proofs\n      __typename\n    }\n    __typename\n  }\n  forgeConfig {\n    minNFTCount\n    maxNFTCount\n    requiredNFTs {\n      nft {\n        category\n        powah\n        image\n        name\n        nftCore {\n          capable\n          contractAddress\n          __typename\n        }\n        __typename\n      }\n      count\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NftCoreInfoFrag on NFTCore {\n  id\n  capable\n  chain\n  contractAddress\n  name\n  symbol\n  dao {\n    id\n    name\n    logo\n    alias\n    __typename\n  }\n  __typename\n}\n\nfragment ExpressionEntity on ExprEntity {\n  cred {\n    id\n    name\n    type\n    credType\n    credSource\n    dimensionConfig\n    referenceLink\n    description\n    lastUpdate\n    lastSync\n    chain\n    eligible(address: $address)\n    metadata {\n      visitLink {\n        link\n        __typename\n      }\n      twitter {\n        isAuthentic\n        __typename\n      }\n      worldcoin {\n        dimensions {\n          values {\n            value\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    commonInfo {\n      participateEndTime\n      modificationInfo\n      __typename\n    }\n    __typename\n  }\n  attrs {\n    attrName\n    operatorSymbol\n    targetValue\n    __typename\n  }\n  attrFormula\n  eligible\n  eligibleAddress\n  __typename\n}\n\nfragment ExpressionReward on ExprReward {\n  arithmetics {\n    ...ExpressionEntity\n    __typename\n  }\n  arithmeticFormula\n  rewardType\n  rewardCount\n  rewardVal\n  __typename\n}\n\nfragment CampaignForgePage on Campaign {\n  id\n  numberID\n  chain\n  spaceStation {\n    address\n    __typename\n  }\n  gamification {\n    forgeConfig {\n      maxNFTCount\n      minNFTCount\n      requiredNFTs {\n        nft {\n          category\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCampaignParticipantsBox on Campaign {\n  ...CampaignForParticipantsDialog\n  id\n  chain\n  space {\n    id\n    isAdmin(address: $address)\n    __typename\n  }\n  participants {\n    participants(first: 10, after: "-1", download: false) {\n      list {\n        address {\n          id\n          avatar\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    participantsCount\n    bountyWinners(first: 10, after: "-1", download: false) {\n      list {\n        createdTime\n        address {\n          id\n          avatar\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    bountyWinnersCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForParticipantsDialog on Campaign {\n  id\n  name\n  type\n  rewardType\n  chain\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  space {\n    isAdmin(address: $address)\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildName\n      roleName\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SpaceDetail on Space {\n  id\n  name\n  info\n  thumbnail\n  alias\n  status\n  links\n  isVerified\n  discordGuildID\n  followersCount\n  nftCores(input: {first: 1}) {\n    list {\n      id\n      marketLink\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ChildrenCampaignsForCampaignDetailAll on Campaign {\n  space {\n    ...SpaceDetail\n    isAdmin(address: $address) @include(if: $withAddress)\n    isFollowing @include(if: $withAddress)\n    followersCount\n    categories\n    __typename\n  }\n  ...CampaignDetailFrag\n  claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n  userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n    list {\n      status\n      __typename\n    }\n    __typename\n  }\n  parentCampaign {\n    id\n    isSequencial\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForSiblingSlide on Campaign {\n  id\n  space {\n    id\n    alias\n    __typename\n  }\n  parentCampaign {\n    id\n    thumbnail\n    isSequencial\n    childrenCampaigns {\n      id\n      ...CampaignForGetImage\n      ...CampaignForCheckFinish\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForCheckFinish on Campaign {\n  claimedLoyaltyPoints(address: $address)\n  whitelistInfo(address: $address) {\n    usedCount\n    __typename\n  }\n  __typename\n}\n\nfragment CampaignForGetImage on Campaign {\n  ...GetImageCommon\n  nftTemplates {\n    image\n    __typename\n  }\n  __typename\n}\n\nfragment GetImageCommon on Campaign {\n  ...CampaignForTokenObject\n  id\n  type\n  thumbnail\n  __typename\n}\n\nfragment CampaignForTokenObject on Campaign {\n  tokenReward {\n    tokenAddress\n    tokenSymbol\n    tokenDecimal\n    tokenLogo\n    __typename\n  }\n  tokenRewardContract {\n    id\n    chain\n    __typename\n  }\n  __typename\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        resp_json = response.json()['data']['campaign']
        return resp_json

    def campaign_wrap(self, campaign):
        credential_groups = []
        if campaign["childrenCampaigns"]:
            # if campaign["status"] != 'Active':
            #     return credential_groups
            print(f"【{self.index}】【{self.address}】分组任务：{campaign['childrenCampaigns']}")
            if campaign['childrenCampaigns']:
                for i, child in enumerate(campaign['childrenCampaigns'], start=1):
                    if child["status"] != 'Active':
                        continue
                    if not child['credentialGroups']:
                        continue
                    for k, group in enumerate(child['credentialGroups'], start=1):
                        for j, credential in enumerate(group["credentials"], start=1):
                            credential_groups.append({
                                "campaign_id": f"{child['id']}",
                                "group_id": f'{group["id"]}',
                                "id": credential['id'],
                                "remark": f"分组任务{k}-{j}",
                                "credSource": credential['credSource'],
                                "name": f"{credential['name']}",
                                "referenceLink": f"{credential['referenceLink']}",
                                "eligible": f"{credential['eligible']}",
                                "conditionRelation": f"{group['conditionRelation']}",
                                "status": f"{child['status']}"
                            })
                            print(
                                f"【{self.index}】【{self.address}】分组任务{k}-{j}：{credential['name']},任务类型：{credential['credSource']},任务链接：{credential['referenceLink']},任务状态：{child['status']},完成情况：{'是' if credential['eligible'] else '否'}")
        elif campaign['credentialGroups']:
            if campaign["status"] != 'Active':
                return credential_groups
            print(f"【{self.index}】【{self.address}】普通任务：{campaign['credentialGroups']}")
            for i, credential in enumerate(campaign['credentialGroups'][0]['credentials'], start=1):
                credential_groups.append({
                    "campaign_id": f"{campaign['id']}",
                    "group_id": f'{campaign["credentialGroups"][0]["id"]}',
                    "id": credential['id'],
                    "remark": f"普通任务{i}",
                    "credSource": credential['credSource'],
                    "name": f"{credential['name']}",
                    "referenceLink": f"{credential['referenceLink']}",
                    "eligible": f"{credential['eligible']}",
                    "conditionRelation": f"{campaign['credentialGroups'][0]['conditionRelation']}",
                    "status": f"{campaign['status']}"
                })
                print(
                    f"【{self.index}】【{self.address}】普通任务{i}：{credential['name']},任务类型：{credential['credSource']},任务链接：{credential['referenceLink']},任务状态：{campaign['status']},完成情况：{'是' if credential['eligible'] else '否'}")
        return credential_groups

    def do_task_item(self, credential_groups):
        s = 0
        print(f'【{self.index}】【{self.address}】 开始做任务！')
        for x in credential_groups:
            try:
                if x['eligible'] == '1' or x['status'] in ['Expired', 'CapReached']:
                    continue
                if x["credSource"] in ["VISIT_LINK", "WATCH_YOUTUBE"]:
                    # 访问地址、观看任务
                    self.add_typed_credential_items(x)
                elif "TWITTER_FOLLOW" in x["credSource"] and self.q_twitter.tw_ok:
                    # 关注 推特
                    parsed_url = urlparse(x["referenceLink"])
                    query_params = parse_qs(parsed_url.query)
                    follow_user = query_params.get('screen_name', [None])[0]
                    if not follow_user:
                        # 用第二种格式查找
                        follow_user = parsed_url.path.split('/')[-1]
                    self.q_twitter.follow_by_name(follow_user)
                    self.add_typed_credential_items(x)
                elif "TWITTER_RT" in x["credSource"] and self.q_twitter.tw_ok:
                    # 转推
                    query_params = parse_qs(urlparse(x["referenceLink"]).query)
                    tweet_id = query_params.get('tweet_id', [None])[0]
                    if str(tweet_id) == '1689357831059943425' and s == 0:
                        s = s+1
                        self.q_twitter.retweet(tweet_id)
                        self.add_typed_credential_items(x)
                    else:
                        self.q_twitter.retweet(tweet_id)
                        self.add_typed_credential_items(x)
                elif "TWITTER_LIKE" in x["credSource"] and self.q_twitter.tw_ok:
                    # 喜欢 推特
                    query_params = parse_qs(urlparse(x["referenceLink"]).query)
                    tweet_id = query_params.get('tweet_id', [None])[0]
                    self.q_twitter.like(tweet_id)
                    self.add_typed_credential_items(x)
                elif "TWITTER_QUOTE" in x["credSource"] and self.q_twitter.tw_ok:
                    # 发 推特
                    query_params = parse_qs(urlparse(x["referenceLink"]).query)
                    tweet_context = query_params.get('text', [None])[0]
                    self.q_twitter.tweet(tweet_context)
                    self.add_typed_credential_items(x)
                elif "QUIZ" in x["credSource"]:
                    # 回答问题的任务类型（需要答案）
                    if str(x["id"]) in self.ans:
                        print(str(x["id"]), self.ans.get(str(x["id"])))
                        self.verify_credential(x["id"], self.ans.get(str(x["id"])))
                    else:
                        continue
                elif "DISCORD_MEMBER" in x["credSource"]:
                    # dis角色，需要入群并有某个角色
                    pass
                elif "GITCOIN_PASSPORT" in x["credSource"]:
                    pass
                elif "JOIN_TELEGRAM" in x["credSource"]:
                    # 需要加入电报（假进入就行）
                    # self.add_typed_credential_items(x)
                    pass
                elif "SUBGRAPH" in x["credSource"]:
                    # Galaxy pass
                    pass
                elif "SPACE_USERS" in x["credSource"]:
                    # 关注空间
                    self.galxe_follow()
                elif "SURVEY" in x["credSource"]:
                    # 回答问题的任务类型（需要答案）
                    if str(x["id"]) in self.ans:
                        print(str(x["id"]), self.ans.get(str(x["id"])))
                        self.verify_credentialv1(x["id"], self.ans.get(str(x["id"])))
                    else:
                        continue
            except Exception as e:
                print(f'【{self.index}】【{self.address}】 发生异常：{e}')

    def verify_group_task(self, tasks1):
        groups = groupby(tasks1, key=lambda x: (x['campaign_id'], x['group_id']))
        for key, group in groups:
            campaign_id = key[0]
            credential_group_id = key[1]
            print(f'【{self.index}】【{self.address}】开始验证分组：【{campaign_id}】-【{credential_group_id}】')
            group_tasks = list(group)
            all_eligible = any(task['eligible'] == '1' for task in group_tasks) if group_tasks[0]["conditionRelation"] == 'ANY' else all(
                task['eligible'] == '1' for task in group_tasks)
            # 验证任务(按照整组)
            if all_eligible:
                # if str(credential_group_id) != '1300690000':
                #     print(f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】【第{i + 1}个任务】不是目标，跳过')
                #     continue
                result = self.claim(campaign_id, credential_group_id)
                if result == "pre":
                    print(f'【{self.index}】【{self.address}】停止验证，请先完成之前的分组任务')
                    # return
            else:
                can_claim = True
                for i, task in enumerate(group_tasks, start=0):
                    # if task["eligible"] == '1' and task["conditionRelation"] == 'ANY':
                    #     print(f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】【第{i + 1}个任务】满足任何任意一个完成，算整组完成，跳过！')
                    #     break
                    # if str(credential_group_id) != '1300690000':
                    #     print(f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】【第{i + 1}个任务】不是目标，跳过')
                    #     continue
                    if task["eligible"] == '1' and i != len(group_tasks) - 1:
                        print(
                            f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】【第{i + 1}个任务】已验证，跳过')
                        continue
                    # if task["eligible"] == '1' and i == len(group_tasks) - 1:
                    #     result = self.claim(campaign_id, credential_group_id)
                    #     if result == "pre":
                    #         print(f'【{self.index}】【{self.address}】停止验证，请先完成之前的分组任务')
                    #         continue
                    json_data = {
                        'operationName': 'VerifyCredentialCondition',
                        'variables': {
                            'input': {
                                'campaignId': f'{campaign_id}',
                                'credentialGroupId': f'{credential_group_id}',
                                'address': f'{self.address.lower()}',
                                'conditionIndex': i,
                            },
                        },
                        'query': 'mutation VerifyCredentialCondition($input: VerifyCredentialGroupConditionInput!) {\n  verifyCondition(input: $input)\n}\n',
                    }
                    response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
                    print(
                        f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】【第{i + 1}个任务】验证任务结果：{response.text}')
                    json_data2 = {
                        'operationName': 'CampaignDetailAll',
                        'variables': {
                            'address': f'{self.address.lower()}',
                            'withAddress': True,
                            'id': f'{campaign_id}',
                        },
                        'query': 'query CampaignDetailAll($id: ID!, $address: String!, $withAddress: Boolean!) {\n  campaign(id: $id) {\n    coHostSpaces {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    bannerUrl\n    ...CampaignDetailFrag\n    userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n      list {\n        status\n        premintTo\n        __typename\n      }\n      __typename\n    }\n    space {\n      ...SpaceDetail\n      isAdmin(address: $address) @include(if: $withAddress)\n      isFollowing @include(if: $withAddress)\n      followersCount\n      categories\n      __typename\n    }\n    isBookmarked(address: $address) @include(if: $withAddress)\n    claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n    parentCampaign {\n      id\n      isSequencial\n      thumbnail\n      __typename\n    }\n    isSequencial\n    numNFTMinted\n    childrenCampaigns {\n      space {\n        ...SpaceDetail\n        isAdmin(address: $address) @include(if: $withAddress)\n        isFollowing @include(if: $withAddress)\n        followersCount\n        categories\n        __typename\n      }\n      ...CampaignDetailFrag\n      claimedLoyaltyPoints(address: $address) @include(if: $withAddress)\n      userParticipants(address: $address, first: 1) @include(if: $withAddress) {\n        list {\n          status\n          __typename\n        }\n        __typename\n      }\n      parentCampaign {\n        id\n        isSequencial\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment CampaignDetailFrag on Campaign {\n  id\n  ...CampaignMedia\n  name\n  numberID\n  type\n  cap\n  info\n  useCred\n  formula\n  status\n  creator\n  thumbnail\n  gasType\n  isPrivate\n  createdAt\n  requirementInfo\n  description\n  enableWhitelist\n  chain\n  startTime\n  endTime\n  requireEmail\n  requireUsername\n  blacklistCountryCodes\n  whitelistRegions\n  rewardType\n  distributionType\n  rewardName\n  claimEndTime\n  loyaltyPoints\n  tokenRewardContract {\n    id\n    address\n    chain\n    __typename\n  }\n  tokenReward {\n    userTokenAmount\n    tokenAddress\n    depositedTokenAmount\n    tokenRewardId\n    tokenDecimal\n    tokenLogo\n    tokenSymbol\n    __typename\n  }\n  nftHolderSnapshot {\n    holderSnapshotBlock\n    __typename\n  }\n  spaceStation {\n    id\n    address\n    chain\n    __typename\n  }\n  ...WhitelistInfoFrag\n  ...WhitelistSubgraphFrag\n  gamification {\n    ...GamificationDetailFrag\n    __typename\n  }\n  creds {\n    ...CredForAddress\n    __typename\n  }\n  credentialGroups(address: $address) {\n    ...CredentialGroupForAddress\n    __typename\n  }\n  dao {\n    ...DaoSnap\n    nftCores {\n      list {\n        capable\n        marketLink\n        contractAddress\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  rewardInfo {\n    discordRole {\n      guildId\n      guildName\n      roleId\n      roleName\n      inviteLink\n      __typename\n    }\n    premint {\n      startTime\n      endTime\n      chain\n      price\n      totalSupply\n      contractAddress\n      banner\n      __typename\n    }\n    loyaltyPoints {\n      points\n      __typename\n    }\n    loyaltyPointsMysteryBox {\n      points\n      weight\n      __typename\n    }\n    __typename\n  }\n  participants {\n    participantsCount\n    bountyWinnersCount\n    __typename\n  }\n  taskConfig(address: $address) {\n    participateCondition {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      eligible\n      __typename\n    }\n    rewardConfigs {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    referralConfig {\n      conditions {\n        ...ExpressionEntity\n        __typename\n      }\n      conditionalFormula\n      description\n      rewards {\n        ...ExpressionReward\n        __typename\n      }\n      eligible\n      rewardAttrVals {\n        attrName\n        attrTitle\n        attrVal\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  referralCode(address: $address)\n  recurringType\n  latestRecurringTime\n  __typename\n}\n\nfragment DaoSnap on DAO {\n  id\n  name\n  logo\n  alias\n  isVerified\n  __typename\n}\n\nfragment CampaignMedia on Campaign {\n  thumbnail\n  rewardName\n  type\n  gamification {\n    id\n    type\n    __typename\n  }\n  __typename\n}\n\nfragment CredForAddress on Cred {\n  id\n  name\n  type\n  credType\n  credSource\n  referenceLink\n  description\n  lastUpdate\n  syncStatus\n  credContractNFTHolder {\n    timestamp\n    __typename\n  }\n  chain\n  eligible(address: $address)\n  subgraph {\n    endpoint\n    query\n    expression\n    __typename\n  }\n  metadata {\n    ...CredMetaData\n    __typename\n  }\n  value {\n    gitcoinPassport {\n      score\n      lastScoreTimestamp\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CredMetaData on CredMetadata {\n  visitLink {\n    link\n    __typename\n  }\n  gitcoinPassport {\n    score {\n      title\n      type\n      description\n      config\n      __typename\n    }\n    lastScoreTimestamp {\n      title\n      type\n      description\n      config\n      __typename\n    }\n    __typename\n  }\n  campaignReferral {\n    count {\n      title\n      type\n      description\n      config\n      __typename\n    }\n    __typename\n  }\n  restApi {\n    url\n    method\n    headers {\n      key\n      value\n      __typename\n    }\n    postBody\n    expression\n    __typename\n  }\n  walletBalance {\n    contractAddress\n    snapshotTimestamp\n    chain\n    balance {\n      type\n      title\n      description\n      config\n      __typename\n    }\n    LastSyncBlock\n    LastSyncTimestamp\n    __typename\n  }\n  lensProfileFollow {\n    handle\n    __typename\n  }\n  graphql {\n    url\n    query\n    expression\n    __typename\n  }\n  lensPostUpvote {\n    postId\n    __typename\n  }\n  lensPostMirror {\n    postId\n    __typename\n  }\n  __typename\n}\n\nfragment CredentialGroupForAddress on CredentialGroup {\n  id\n  description\n  credentials {\n    ...CredForAddress\n    __typename\n  }\n  conditionRelation\n  conditions {\n    expression\n    eligible\n    __typename\n  }\n  rewards {\n    expression\n    eligible\n    rewardCount\n    rewardType\n    __typename\n  }\n  rewardAttrVals {\n    attrName\n    attrTitle\n    attrVal\n    __typename\n  }\n  claimedLoyaltyPoints\n  __typename\n}\n\nfragment WhitelistInfoFrag on Campaign {\n  id\n  whitelistInfo(address: $address) {\n    address\n    maxCount\n    usedCount\n    claimedLoyaltyPoints\n    currentPeriodClaimedLoyaltyPoints\n    currentPeriodMaxLoyaltyPoints\n    __typename\n  }\n  __typename\n}\n\nfragment WhitelistSubgraphFrag on Campaign {\n  id\n  whitelistSubgraph {\n    query\n    endpoint\n    expression\n    variable\n    __typename\n  }\n  __typename\n}\n\nfragment GamificationDetailFrag on Gamification {\n  id\n  type\n  nfts {\n    nft {\n      id\n      animationURL\n      category\n      powah\n      image\n      name\n      treasureBack\n      nftCore {\n        ...NftCoreInfoFrag\n        __typename\n      }\n      traits {\n        name\n        value\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  airdrop {\n    name\n    contractAddress\n    token {\n      address\n      icon\n      symbol\n      __typename\n    }\n    merkleTreeUrl\n    addressInfo(address: $address) {\n      index\n      amount {\n        amount\n        ether\n        __typename\n      }\n      proofs\n      __typename\n    }\n    __typename\n  }\n  forgeConfig {\n    minNFTCount\n    maxNFTCount\n    requiredNFTs {\n      nft {\n        category\n        powah\n        image\n        name\n        nftCore {\n          capable\n          contractAddress\n          __typename\n        }\n        __typename\n      }\n      count\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment NftCoreInfoFrag on NFTCore {\n  id\n  capable\n  chain\n  contractAddress\n  name\n  symbol\n  dao {\n    id\n    name\n    logo\n    alias\n    __typename\n  }\n  __typename\n}\n\nfragment ExpressionEntity on ExprEntity {\n  cred {\n    id\n    name\n    type\n    credType\n    credSource\n    referenceLink\n    description\n    lastUpdate\n    chain\n    eligible(address: $address)\n    metadata {\n      visitLink {\n        link\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  attrs {\n    attrName\n    operatorSymbol\n    targetValue\n    __typename\n  }\n  attrFormula\n  eligible\n  __typename\n}\n\nfragment ExpressionReward on ExprReward {\n  arithmetics {\n    ...ExpressionEntity\n    __typename\n  }\n  arithmeticFormula\n  rewardType\n  rewardCount\n  rewardVal\n  __typename\n}\n\nfragment SpaceDetail on Space {\n  id\n  name\n  info\n  thumbnail\n  alias\n  links\n  isVerified\n  discordGuildID\n  followersCount\n  __typename\n}\n',
                    }
                    response2 = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data2)
                    if "errors" in response.text and task["conditionRelation"] == 'ALL':
                        can_claim = False
                    if response.json()['data']['verifyCondition'] and i == len(group_tasks) - 1 and can_claim:
                        result = self.claim(campaign_id, credential_group_id)
                        if result == "pre":
                            print(f'【{self.index}】【{self.address}】停止验证，请先完成之前的分组任务')
                            # return

    def verify_credential(self, cred_id, input_values):
        # 验证任务(按照单任务)
        # solution = self.get_captcha_by_2captcha()
        # solution = self.get_captcha_by_qg()
        json_data = {
            'operationName': 'SyncCredentialValue',
            'variables': {
                'input': {
                    'syncOptions': {
                        'credId': f'{cred_id}',
                        'address': f'{self.address}',
                        'quiz': {
                            'answers': input_values,
                        },
                    },
                },
            },
            'query': 'mutation SyncCredentialValue($input: SyncCredentialValueInput!) {\n  syncCredentialValue(input: $input) {\n    value {\n      address\n      spaceUsers {\n        follow\n        points\n        participations\n        __typename\n      }\n      campaignReferral {\n        count\n        __typename\n      }\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      walletBalance {\n        balance\n        __typename\n      }\n      multiDimension {\n        value\n        __typename\n      }\n      allow\n      survey {\n        answers\n        __typename\n      }\n      quiz {\n        allow\n        correct\n        __typename\n      }\n      __typename\n    }\n    message\n    __typename\n  }\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】回答题目结果！:{response.text}')

    def verify_credentialv1(self, cred_id, input_values):
        json_data = {
            'operationName': 'SyncCredentialValue',
            'variables': {
                'input': {
                    'syncOptions': {
                        'credId': f'{cred_id}',
                        'address': f'{self.address}',
                        'survey': {
                            'answers': input_values,
                        },
                    },
                },
            },
            'query': 'mutation SyncCredentialValue($input: SyncCredentialValueInput!) {\n  syncCredentialValue(input: $input) {\n    value {\n      address\n      spaceUsers {\n        follow\n        points\n        participations\n        __typename\n      }\n      campaignReferral {\n        count\n        __typename\n      }\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      walletBalance {\n        balance\n        __typename\n      }\n      multiDimension {\n        value\n        __typename\n      }\n      allow\n      survey {\n        answers\n        __typename\n      }\n      quiz {\n        allow\n        correct\n        __typename\n      }\n      __typename\n    }\n    message\n    __typename\n  }\n}\n',
        }

        response = requests.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】回答题目结果！:{response.text}')

    def verify_credential_v2(self, cred_id, input_values):
        # 验证任务(按照单任务)
        # solution = self.get_captcha_by_2captcha()
        solution = self.get_captcha_by_qg()
        json_data = {
            'operationName': 'manuallyVerifyCredential',
            'variables': {
                'input': {
                    'credId': f'{cred_id}',
                    'address': f'{self.address}',
                    'captcha': {
                        'lotNumber': f'{solution["lot_number"]}',
                        'captchaOutput': f'{solution["captcha_output"]}',
                        'passToken': f'{solution["pass_token"]}',
                        'genTime': f'{solution["gen_time"]}',
                    },
                    'credQuiz': {
                        'input': input_values,
                    },
                },
            },
            'query': 'mutation manuallyVerifyCredential($input: ManuallyVerifyCredentialInput!) {\n  manuallyVerifyCredential(input: $input) {\n    eligible\n    credQuiz {\n      output {\n        correct\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        json_data = {
            'operationName': 'SyncCredentialValue',
            'variables': {
                'input': {
                    'syncOptions': {
                        'credId': f'{cred_id}',
                        'address': f'{self.address}',
                        'quiz': {
                            'answers': input_values,
                        },
                    },
                },
            },
            'query': 'mutation SyncCredentialValue($input: SyncCredentialValueInput!) {\n  syncCredentialValue(input: $input) {\n    value {\n      address\n      spaceUsers {\n        follow\n        points\n        participations\n        __typename\n      }\n      campaignReferral {\n        count\n        __typename\n      }\n      gitcoinPassport {\n        score\n        lastScoreTimestamp\n        __typename\n      }\n      walletBalance {\n        balance\n        __typename\n      }\n      multiDimension {\n        value\n        __typename\n      }\n      allow\n      survey {\n        answers\n        __typename\n      }\n      quiz {\n        allow\n        correct\n        __typename\n      }\n      __typename\n    }\n    message\n    __typename\n  }\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】回答题目结果！:{response.text}')
    def add_typed_credential_items(self, cred):
        # solution = self.get_captcha_by_2captcha()
        solution = self.get_captcha_by_qg()
        json_data = {
            'operationName': 'AddTypedCredentialItems',
            'variables': {
                'input': {
                    'credId': f'{cred["id"]}',
                    'operation': 'APPEND',
                    'items': [
                        f'{self.address}',
                    ],
                    'captcha': {
                        'lotNumber': f'{solution["lot_number"]}',
                        'captchaOutput': f'{solution["captcha_output"]}',
                        'passToken': f'{solution["pass_token"]}',
                        'genTime': f'{solution["gen_time"]}',
                    },
                },
            },
            'query': 'mutation AddTypedCredentialItems($input: MutateTypedCredItemInput!) {\n  typedCredentialItems(input: $input) {\n    id\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】任务:{cred["name"]}，报文{response.text}')

    def get_space_total_score(self):
        json_data = {
            'operationName': 'SpaceAccessQuery',
            'variables': {
                'alias': f'{self.space}',
                'address': f'{self.address}',
            },
            'query': 'query SpaceAccessQuery($id: Int, $alias: String, $address: String!) {\n  space(id: $id, alias: $alias) {\n    id\n    isFollowing\n    discordGuildID\n    discordGuildInfo\n    status\n    isAdmin(address: $address)\n    unclaimedBackfillLoyaltyPoints(address: $address)\n    addressLoyaltyPoints(address: $address) {\n      id\n      points\n      rank\n      __typename\n    }\n    __typename\n  }\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        total_score = response.json()['data']['space']['addressLoyaltyPoints']["points"]
        print(f"【{self.index}】【{self.address}】:项目【{self.space}】总得分: {total_score}")
        # QGFile.save_to_file('./taiko得分情况.txt',f"{self.index}----{self.address}----{self.private_key}----总得分: {total_score}")

    def galxe_follow(self):
        json_data = {
            'operationName': 'followSpace',
            'variables': {
                'spaceIds': [
                    int(self.space_info['id'])
                ],
            },
            'query': 'mutation followSpace($spaceIds: [Int!]) {\n  followSpace(spaceIds: $spaceIds)\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】关注空间结果:{response.text}')

    def remove_twitter(self):
        json_data = {
            'operationName': 'DeleteSocialAccount',
            'variables': {
                'input': {
                    'address': f'{self.address}',
                    'type': 'TWITTER',
                },
            },
            'query': 'mutation DeleteSocialAccount($input: DeleteSocialAccountInput!) {\n  deleteSocialAccount(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        if response.status_code == 200:
            print(f"【{self.index}】【{self.address}】移除绑定推特成功！")

    def remove_dis(self):
        json_data = {
            'operationName': 'DeleteSocialAccount',
            'variables': {
                'input': {
                    'address': f'{self.address}',
                    'type': 'DISCORD',
                },
            },
            'query': 'mutation DeleteSocialAccount($input: DeleteSocialAccountInput!) {\n  deleteSocialAccount(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        if response.status_code == 200:
            print(f"【{self.index}】【{self.address}】移除绑定discord成功！")

    def bind_twitter(self):
        if self.userinfo.get("hasTwitter") or not self.q_twitter.tw_ok:
            return
        # 生成发推链接，然后去发推
        # url = f"https://twitter.com/intent/tweet?text=Verifying+my+Twitter+account+for+my+%23GalxeID+gid%3A{self.userinfo['id']}+@Galxe%20%0A%0A&url=galxe.com/galxeid"
        cookies = {
            'auth_token': f'{self.twitter_info.get("auth_token")}',
            'ct0': f'{self.twitter_info.get("ct0")}',
            'lang': 'zh-cn',
        }
        # print(url)
        # 1.发推
        headers = {
            'authority': 'twitter.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://twitter.com',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'x-client-transaction-id': 'tDvfovzMiQJwznR0tE7eFX0IO2WRzGi2chaiKerfDAYNJLza6Dgwgtdcx8ITsu+yyz4r3bSbt5HIoRv4+wFVrkzXlPDatQ',
            'x-client-uuid': '13d21bd0-399b-4499-b073-18a4c048e15e',
            'x-csrf-token': f'{self.twitter_info.get("ct0")}',
        }
        json_data = {
            'variables': {
                'tweet_text': f'{random.randint(0, 99999)}Verifying my Twitter account for my #GalxeID gid:{self.userinfo["id"]} @Galxe \n\n galxe.com/id ',
                'dark_request': False,
                'media': {
                    'media_entities': [],
                    'possibly_sensitive': False,
                },
                'semantic_annotation_ids': [],
            },
            'features': {
                'tweetypie_unmention_optimization_enabled': True,
                'responsive_web_edit_tweet_api_enabled': True,
                'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
                'view_counts_everywhere_api_enabled': True,
                'longform_notetweets_consumption_enabled': True,
                'responsive_web_twitter_article_tweet_consumption_enabled': False,
                'tweet_awards_web_tipping_enabled': False,
                'longform_notetweets_rich_text_read_enabled': True,
                'longform_notetweets_inline_media_enabled': True,
                'responsive_web_graphql_exclude_directive_enabled': True,
                'verified_phone_label_enabled': False,
                'freedom_of_speech_not_reach_fetch_enabled': True,
                'standardized_nudges_misinfo': True,
                'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': True,
                'responsive_web_media_download_video_enabled': False,
                'responsive_web_graphql_skip_user_profile_image_extensions_enabled': False,
                'responsive_web_graphql_timeline_navigation_enabled': True,
                'responsive_web_enhance_cards_enabled': False,
            },
            'fieldToggles': {
                'withArticleRichContentState': False,
                'withAuxiliaryUserLabels': False,
            },
            'queryId': 'tTsjMKyhajZvK4q76mpIBg',
        }

        response = requests.post(
            'https://twitter.com/i/api/graphql/tTsjMKyhajZvK4q76mpIBg/CreateTweet',
            cookies=cookies,
            headers=headers,
            json=json_data,
        )
        print(response.text)
        rest_id = response.json()["data"]["create_tweet"]["tweet_results"]["result"]["rest_id"]
        # 发推成功后，再验证
        tweet_url = f"https://twitter.com/{self.q_twitter.username}/status/{rest_id}"
        json_data = {
            'operationName': 'VerifyTwitterAccount',
            'variables': {
                'input': {
                    'address': f'{self.address.lower()}',
                    'tweetURL': f'{tweet_url}',
                },
            },
            'query': 'mutation VerifyTwitterAccount($input: VerifyTwitterAccountInput!) {\n  verifyTwitterAccount(input: $input) {\n    address\n    twitterUserID\n    twitterUserName\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(response.text)
        if response.status_code == 200 and "twitterUserID" in response.text:
            print(f"【{self.index}】【{self.address}】绑定twitter成功！")

    def bind_email(self, email):
        if self.userinfo.get("hasEmail"):
            return
        if not email:
            email = RandomGenerator.generate_random_email(8)
        # solution = self.get_captcha_by_2captcha()
        solution = self.get_captcha_by_qg()
        json_data = {
            'operationName': 'SendVerifyCode',
            'variables': {
                'input': {
                    'address': f'{self.address}',
                    'email': f'{email}',
                    'captcha': {
                        'lotNumber': f'{solution["lot_number"]}',
                        'captchaOutput': f'{solution["captcha_output"]}',
                        'passToken': f'{solution["pass_token"]}',
                        'genTime': f'{solution["gen_time"]}',
                    },
                },
            },
            'query': 'mutation SendVerifyCode($input: SendVerificationEmailInput!) {\n  sendVerificationCode(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)

        if response.status_code == 200:
            print(f"【{self.index}】【{self.address}】-【{email}】发送短信成功！")
            # 获取邮箱验证码并验证
            html = self.cq_client.search_cq_email(email, "Please confirm your email on Galxe")
            soup = BeautifulSoup(html, features="html.parser")
            code = soup.find('h1').text
            print(f"【{email}】验证验证码：{code}")
            json_data = {
                'operationName': 'UpdateEmail',
                'variables': {
                    'input': {
                        'address': f'{self.address}',
                        'email': f'{email}',
                        'verificationCode': f'{code}',
                    },
                },
                'query': 'mutation UpdateEmail($input: UpdateEmailInput!) {\n  updateEmail(input: $input) {\n    code\n    message\n    __typename\n  }\n}\n',
            }
            response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
            if "errors" not in response.text:
                print(f"【{self.index}】【{self.address}】绑定邮箱成功！")
            else:
                print(f"【{self.index}】【{self.address}】绑定邮箱失败！{response.text}")

    def bind_dis(self, dis_token):
        if not dis_token or self.userinfo.get("hasDiscord"):
            return
        # 1.构造discord url并授权
        # url = f"https://discord.com/oauth2/authorize?client_id=947863296789323776&redirect_uri=https://galxe.com&response_type=code&scope=identify%20guilds%20guilds.members.read&prompt=consent&state=Discord_Auth;0x45fba672eecf7ba2e20931a684aa4d22a85a9551"
        cookies = {
            '__dcfduid': '78516ee0e2c911ed88ecf571fdf02241',
            '__sdcfduid': '78516ee1e2c911ed88ecf571fdf0224113d706e3e9fb111087940be8ff0c16b098dfbc293adb1ee82029bdf6617dcaf9',
            '__cfruid': '2bf5834374fa9e9ff70aef2cdfeffe733b7e2d17-1691949088',
            'cf_clearance': 'WVfETz.gsWArALAR082A747pyTYCRegQgxV9Wq8jk5o-1691953556-0-1-85a9f762.6885cbe4.d2a8a882-0.2.1691953556',
        }
        headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'authorization': dis_token,
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'pragma': 'no-cache',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'zh-CN',
            'x-discord-timezone': 'Asia/Shanghai',
        }
        params = {
            'client_id': '947863296789323776',
            'response_type': 'code',
            'redirect_uri': 'https://galxe.com',
            'scope': 'identify guilds guilds.members.read',
            'state': f'Discord_Auth;{self.address}',
        }

        json_data = {
            'permissions': '0',
            'authorize': True,
        }
        response = self.dis_session.post('https://discord.com/api/v9/oauth2/authorize', params=params, cookies=cookies,
                                         headers=headers, json=json_data)
        print(f"【{self.index}】【{self.address}】绑定dis-step1，报文：{response.text}")
        # 解析 URL
        parsed_url = urllib.parse.urlparse(response.json()["location"])
        # location = response.json()["location"]
        # 获取查询字符串参数
        query_params = urllib.parse.parse_qs(parsed_url.query)
        # 获取 auth_type 和 state 参数的值
        code = query_params['code'][0]
        state = query_params['state'][0]
        # 2.galaxy验证绑定
        json_data = {
            'operationName': 'VerifyDiscord',
            'variables': {
                'input': {
                    'address': f'{self.address}',
                    'parameter': '',
                    'token': f'{code}',
                },
            },
            'query': 'mutation VerifyDiscord($input: VerifyDiscordAccountInput!) {\n  verifyDiscordAccount(input: $input) {\n    address\n    discordUserID\n    discordUserName\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', headers=headers, json=json_data)
        print(f"【{self.index}】【{self.address}】绑定dis-step2，报文：{response.text}")

    def claim(self, campaign_id, credential_group_id):
        # 获取任务详情
        detail = self.get_task_detail(campaign_id)

        # 计算总的奖励点数
        total_point = sum(z["rewardCount"] for x in detail["credentialGroups"] for z in x["rewards"] if z["rewardType"] == "LOYALTYPOINTS")
        total_point2 = sum(z["rewardCount"] for x in detail["credentialGroups"] for z in x["rewards"] if z["rewardType"] == "LOYALTYPOINTSMYSTERYBOX")
        # 检查是否已经领取奖励，如果是，则跳过
        if detail['claimedLoyaltyPoints'] >= total_point and total_point and detail.get("recurringType") != "DAILY":
            print(f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】此组任务已领取奖励')
            return "skip"

        if not total_point2 and not total_point and detail.get("recurringType") != "DAILY":
            print(f'【{self.index}】【{self.address}】【{campaign_id}】【{credential_group_id}】此组任务已领取奖励')
            return "skip"
        # solution = self.get_captcha_by_2captcha()
        solution = self.get_captcha_by_qg()
        json_data = {
            'operationName': 'PrepareParticipate',
            'variables': {
                'input': {
                    'signature': '',
                    'campaignID': f'{campaign_id}',
                    'address': f'{self.address}',
                    'mintCount': 1,
                    'chain': f'{detail["chain"]}',
                    'captcha': {
                        'lotNumber': f'{solution["lot_number"]}',
                        'captchaOutput': f'{solution["captcha_output"]}',
                        'passToken': f'{solution["pass_token"]}',
                        'genTime': f'{solution["gen_time"]}',
                    },
                    'referralCode': f'{self.ref_code}',
                },
            },
            'query': 'mutation PrepareParticipate($input: PrepareParticipateInput!) {\n  prepareParticipate(input: $input) {\n    allow\n    disallowReason\n    signature\n    nonce\n    mintFuncInfo {\n      funcName\n      nftCoreAddress\n      verifyIDs\n      powahs\n      cap\n      __typename\n    }\n    extLinkResp {\n      success\n      data\n      error\n      __typename\n    }\n    metaTxResp {\n      metaSig2\n      autoTaskUrl\n      metaSpaceAddr\n      forwarderAddr\n      metaTxHash\n      reqQueueing\n      __typename\n    }\n    solanaTxResp {\n      mint\n      updateAuthority\n      explorerUrl\n      signedTx\n      verifyID\n      __typename\n    }\n    aptosTxResp {\n      signatureExpiredAt\n      tokenName\n      __typename\n    }\n    tokenRewardCampaignTxResp {\n      signatureExpiredAt\n      verifyID\n      __typename\n    }\n    loyaltyPointsTxResp {\n      TotalClaimedPoints\n      __typename\n    }\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】【{campaign_id}】整组任务奖励领取结果：{response.text}')
        if "you need completed pre-sequence" in response.text:
            return "pre"
        else:
            return "pass"

    def get_passport_url(self):
        # if not self.userinfo["passport"]["status"] == 'NOT_ISSUED' or not self.userinfo["passport"]["status"] == 'DECLINED':
        #     print(f'【{self.index}】【{self.address}】实名了，跳过！！！！')
        #     return
        message = f"get_or_create_address_inquiry:{self.address.lower()}"
        signature = self.sign_msg(w3, message)
        json_data = {
            'operationName': 'GetOrCreateInquiryByAddress',
            'variables': {
                'input': {
                    'address': f'{self.address.lower()}',
                    'signature': f'{signature}',
                },
            },
            'query': 'mutation GetOrCreateInquiryByAddress($input: GetOrCreateInquiryByAddressInput!) {\n  getOrCreateInquiryByAddress(input: $input) {\n    status\n    vendor\n    personaInquiry {\n      inquiryID\n      sessionToken\n      declinedReason\n      __typename\n    }\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        persona_inquiry = response.json()['data']['getOrCreateInquiryByAddress']['personaInquiry']
        random_string = ''.join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(16)])
        if persona_inquiry["sessionToken"]:
            url = f'https://withpersona.com/widget?client-version=4.7.1&container-id=persona-widget-{random_string}&flow-type=embedded&environment=production&iframe-origin=https%3A%2F%2Fgalxe.com&inquiry-id={persona_inquiry["inquiryID"]}&session-token={persona_inquiry["sessionToken"]}'
            print(f'【{self.index}】【{self.address}】KYC地址: {url}')
            with open('KYC.txt', 'a', encoding='utf-8') as f:
                f.write(f'{self.address}----{self.index}----{url}\n')
        else:
            print("未认证")

    def encrypt_data(self, data, password):
        key = hashlib.sha3_256(password.encode('utf-8')).digest()
        iv = os.urandom(12)
        text = data.encode('utf-8')
        cipher = AES.new(key, AES.MODE_GCM, iv)
        cipher_text, tag = cipher.encrypt_and_digest(text)
        encrypted_data = iv + cipher_text + tag
        enc_result = base64.b64encode(encrypted_data)
        encrypted_hex = "0x" + enc_result.hex()
        return encrypted_hex

    def mint_pass_step_1(self):
        if self.userinfo["passport"]["status"] not in 'PENDING_PREPARE':
            # log = f'{self.index}----{self.address}'
            # QGFile.save_to_file("无实名.txt",log)
            print(f'【{self.index}】【{self.address}】不处于PENDING_PREPARE，跳过！！！！')
            return
        message1 = f"prepare_address_passport:{self.address.lower()}"
        signature1 = self.sign_msg(w3, message1)
        json_data = {
            'operationName': 'PreparePassport',
            'variables': {
                'input': {
                    'signature': f'{signature1}',
                    'address': f'{self.address.lower()}',
                },
            },
            'query': 'mutation PreparePassport($input: PreparePassportInput!) {\n  preparePassport(input: $input) {\n    data\n    __typename\n  }\n}\n',
        }

        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】 mint-PreparePassport报文：{response.text}')
        if "galaxy passport cannot be created" in response.text:
            print(f'【{self.index}】【{self.address}】 未实名，跳过！')
            return
        elif "AlreadyExists: passport has already been created" in response.text:
            print(f'【{self.index}】【{self.address}】 已经mint，跳过！')
            return
        password = "Aa246135123@"
        encrypted_hex = self.encrypt_data(response.json()["data"]["preparePassport"]["data"], password)
        message2 = f"save_address_passport:{self.address.lower()}"
        signature2 = self.sign_msg(w3, message2)
        json_data = {
            'operationName': 'SavePassport',
            'variables': {
                'input': {
                    'signature': f'{signature2}',
                    'address': f'{self.address.lower()}',
                    'cipher': f'{encrypted_hex}',
                },
            },
            'query': 'mutation SavePassport($input: SavePassportInput!) {\n  savePassport(input: $input) {\n    id\n    encrytionAlgorithm\n    cipher\n    __typename\n  }\n}\n',
        }
        response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
        print(f'【{self.index}】【{self.address}】 mint-SavePassport报文：{response.text}')

    def mint_pass_step_2(self):
        if self.userinfo["passport"]["status"] == 'NOT_ISSUED':
            log = f'{self.index}----{self.address}'
            QGFile.save_to_file("无实名2.txt", log)
            print(f'【{self.index}】【{self.address}】无实名，跳过！！！！')
            return
        if 0.02 < self.bsc_balance < 0.0251:
            log = f'{self.index}----{self.address}'
            QGFile.save_to_file("余额不足2.txt", log)
            print(f'【{self.index}】【{self.address}】，余额不足:{self.bsc_balance}')
            return
        elif self.userinfo["passport"]["status"] == 'ISSUED_NOT_MINTED':
            solution = self.get_captcha_params()
            json_data = {
                'operationName': 'PrepareParticipate',
                'variables': {
                    'input': {
                        'signature': '',
                        'campaignID': 'GCfBiUt5ye',
                        'address': f'{self.address.lower()}',
                        'mintCount': 1,
                        'chain': 'BSC',
                        'captcha': {
                            'lotNumber': f'{solution.lot_number}',
                            'captchaOutput': f'{solution.captcha_output}',
                            'passToken': f'{solution.pass_token}',
                            'genTime': f'{solution.gen_time}',
                        },
                    },
                },
                'query': 'mutation PrepareParticipate($input: PrepareParticipateInput!) {\n  prepareParticipate(input: $input) {\n    allow\n    disallowReason\n    signature\n    nonce\n    mintFuncInfo {\n      funcName\n      nftCoreAddress\n      verifyIDs\n      powahs\n      cap\n      __typename\n    }\n    extLinkResp {\n      success\n      data\n      error\n      __typename\n    }\n    metaTxResp {\n      metaSig2\n      autoTaskUrl\n      metaSpaceAddr\n      forwarderAddr\n      metaTxHash\n      reqQueueing\n      __typename\n    }\n    solanaTxResp {\n      mint\n      updateAuthority\n      explorerUrl\n      signedTx\n      verifyID\n      __typename\n    }\n    aptosTxResp {\n      signatureExpiredAt\n      tokenName\n      __typename\n    }\n    tokenRewardCampaignTxResp {\n      signatureExpiredAt\n      verifyID\n      __typename\n    }\n    loyaltyPointsTxResp {\n      TotalClaimedPoints\n      __typename\n    }\n    __typename\n  }\n}\n',
            }
            response = self.galxe_session.post('https://graphigo.prd.galaxy.eco/query', json=json_data)
            print(f'【{self.index}】【{self.address}】 mint-参数报文：{response.text}')
            action_name = "mint_pass"
            to_address = "0x2D18f2d27D50C9b4013DEBA3D54f60996bD8847E"
            prepare = response.json()["data"]["prepareParticipate"]
            powah = hex(prepare["mintFuncInfo"]["powahs"][0])[2:].rjust(64, '0')
            verifyID = hex(prepare["mintFuncInfo"]["verifyIDs"][0])[2:].rjust(64, '0')
            signature = prepare["signature"][2:].ljust(192, '0')
            input_data = f'0x2e4dbe8f' \
                         f'{powah}' \
                         f'000000000000000000000000{prepare["mintFuncInfo"]["nftCoreAddress"][2:]}' \
                         f'{verifyID}' \
                         f'{powah}' \
                         f'00000000000000000000000000000000000000000000000000000000000000a0' \
                         f'0000000000000000000000000000000000000000000000000000000000000041' \
                         f'{signature}'
            # print(input_data)
            value = "0.025"
            self.sent_tx_with_assembled_by_type0(self.bsc_w3, to_address, value, input_data, action_name, 150000, 1.1)
            log = f'{self.index}----{self.address}'
            QGFile.save_to_file("已mint2.txt", log)
        else:
            print(f'【{self.index}】【{self.address}】 已经mint过pass啦！！！！')
            log = f'{self.index}----{self.address}'
            QGFile.save_to_file("已mint2.txt", log)

    def save_userinfo(self):
        self.get_userinfo()
        self.get_space_total_score()
        log = f'{self.index}----{self.address}----{self.userinfo.get("hasEmail")}----{self.userinfo.get("email")}----{self.userinfo.get("hasDiscord")}----{self.userinfo.get("discordUserName")}----{self.userinfo.get("hasTwitter")}----{self.userinfo.get("twitterUserName")}----{self.userinfo["passport"]["status"]}----{self.total_score}'
        QGFile.save_to_file(f"{self.space}-1-100-3.txt", log)
