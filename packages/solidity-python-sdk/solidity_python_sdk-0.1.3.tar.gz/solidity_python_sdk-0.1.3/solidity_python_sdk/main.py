import logging
import json
from web3 import Web3
from dotenv import load_dotenv
import os
from eth_account import Account
from solidity_python_sdk.contracts.product_passport import ProductPassport
from solidity_python_sdk.contracts.geolocation import Geolocation
from solidity_python_sdk.contracts.batch import Batch
from solidity_python_sdk.resources import ABI

class DigitalProductPassportSDK:
    """
    SDK for interacting with Digital Product Passport smart contracts.
    """

    def __init__(self, provider_url=None, private_key=None, gas=100000, gwei_bid=30):
        """
        Initializes the SDK with a provider URL and private key.
        """
        logging.basicConfig(level=logging.DEBUG)
        load_dotenv()
        provider_url = provider_url or os.getenv("PROVIDER_URL")
        private_key = private_key or os.getenv("PRIVATE_KEY")

        if not provider_url or not private_key:
            raise ValueError("Provider URL and Private key must be provided.")

        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.account = self.web3.eth.account.from_key(private_key)
        self.gas = gas
        self.gwei_bid = gwei_bid
        self.contracts = self.load_all_contracts()

        # Pass the SDK instance to the contract classes
        self.product_passport = ProductPassport(self)
        self.batch = Batch(self)
        self.geolocation = Geolocation(self)

        logging.info("DigitalProductPassportSDK initialized successfully.")

    def load_all_contracts(self):
        contracts = {}
        abi_folder_path = os.path.dirname(ABI.__file__)
        logging.debug(f"Loading contracts from {abi_folder_path}")
        for filename in os.listdir(abi_folder_path):
            if filename.endswith('.json'):
                logging.debug(f"Found contract file: {filename}")
                contract_name = os.path.splitext(filename)[0]
                file_path = os.path.join(abi_folder_path, filename)
                contracts[contract_name] = self.load_contract(file_path)
                logging.debug(f"Loaded contract {contract_name} from {file_path}")
        return contracts
        
    def load_contract(self, contract_path):
        with open(contract_path) as file:
            contract_interface = json.load(file)
        return contract_interface
