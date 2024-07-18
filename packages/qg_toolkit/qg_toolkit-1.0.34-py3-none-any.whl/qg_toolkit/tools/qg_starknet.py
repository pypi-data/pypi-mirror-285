from starknet_py.net.account.account import Account
from starknet_py.net.full_node_client import FullNodeClient


class QGStarkNet:
    def __init__(self, private_key: str, node_url=None):
        if node_url:
            self.client = FullNodeClient(node_url=node_url)
        else:
            self.client = FullNodeClient(node_url="https://starknet-mainnet.infura.io/v3/9eaa3112b4cc486180aa596882dfa6cd")
        self.account = Account(
            private_key=private_key,
            client=self.client,
        )

    def get_account(self):
        return self.account

    def get_private_key(self):
        return self.account.private_key

    def get_public_key(self):
        return self.account.public_key

    def sign_msg(self, type_data):
        # typed_data = {
        #     "types": {
        #         "StarkNetDomain": [
        #             {
        #                 "name": "name",
        #                 "type": "felt"
        #             },
        #             {
        #                 "name": "version",
        #                 "type": "felt"
        #             },
        #             {
        #                 "name": "chainId",
        #                 "type": "felt"
        #             }
        #         ],
        #         "contents": [
        #             {
        #                 "name": "Greetings",
        #                 "type": "string"
        #             },
        #             {
        #                 "name": "Sign",
        #                 "type": "felt"
        #             },
        #             {
        #                 "name": "timestamp",
        #                 "type": "felt"
        #             }
        #         ],
        #         "Message": [
        #             {
        #                 "name": "contents",
        #                 "type": "contents"
        #             }
        #         ]
        #     },
        #     "primaryType": "Message",
        #     "domain": {
        #         "name": "Avail Rewards",
        #         "version": "1",
        #         "chainId": "0x534e5f4d41494e"
        #     },
        #     "message": {
        #         "contents": {
        #             "Greetings": "Greetings from Avail!",
        #             "Sign": "Sign to Check your Eligibility",
        #             "timestamp": 1713519490
        #         }
        #     }
        # }
        # 签名消息
        signature = self.account.sign_message(typed_data=type_data)
        print(signature)
        # 验证签名
        verify_result = self.account.verify_message(typed_data=type_data, signature=signature)
        print(verify_result)


