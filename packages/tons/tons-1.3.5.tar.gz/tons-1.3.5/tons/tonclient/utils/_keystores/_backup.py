from typing import Optional, Union, List, Dict

from pydantic import BaseModel, ValidationError, validator

from tons import settings
from tons.tonsdk.contract.wallet import WalletVersionEnum, WalletContract
from tons.tonsdk.crypto import mnemonic_is_valid
from tons.tonsdk.utils import Address
from ._keystore import BaseKeyStore
from ._keystore._secret import UnknownSecretKind, WalletSecret
from ._record import Record
from .._exceptions import InvalidBackupError
from .._whitelist import WhitelistContact


class TonCliRecordBackup(BaseModel):
    name: str
    comment: Optional[str] = ""
    config: str
    kind: str
    address: Union[str, Address]
    mnemonics: List[str]

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True

    def to_backup_record(self) -> Optional["RecordBackup"]:
        if not self.__supported_wallet():
            return None

        version = self.__map_kind_to_version()
        workchain = int(self.__map_config_to_workchain())

        default_subwallet_id = WalletContract.default_subwallet_id(workchain, version)
        subwallet_id = self.__map_config_to_subwallet_id()
        subwallet_id = default_subwallet_id if subwallet_id is None else int(subwallet_id)

        return RecordBackup(name=self.name, address=self.address,
                            version=version,
                            workchain=workchain,
                            subwallet_id=subwallet_id,
                            mnemonics=" ".join(self.mnemonics),
                            comment=self.comment)

    def __supported_wallet(self):
        return self.kind in self.kind_version_map

    def __map_kind_to_version(self):
        return self.kind_version_map.get(self.kind, None)

    def __map_config_to_workchain(self):
        # "wc=0,walletId=698983191,pk=qweqweqwe"
        return self.config.split(",")[0].split("=")[1]

    def __map_config_to_subwallet_id(self):
        temp = self.config.split("walletId=")
        if len(temp) == 2:
            return temp[1].split(",")[0]

        return None

    @property
    def kind_version_map(self) -> Dict:
        return {
            "org.ton.wallets.v2": WalletVersionEnum.v2r1,
            "org.ton.wallets.v2.r2": WalletVersionEnum.v2r2,
            "org.ton.wallets.v3": WalletVersionEnum.v3r1,
            "org.ton.wallets.v3.r2": WalletVersionEnum.v3r2,
        }


class RecordBackup(BaseModel):
    name: str
    address: Union[str, Address]
    version: WalletVersionEnum
    workchain: int
    subwallet_id: Optional[int]
    mnemonics: str  # actually contains mnemonics or private key, field name is kept for backwards compatibility
    comment: Optional[str] = ""

    class Config:
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True

    @classmethod
    def from_record(cls, record: "Record", secret: WalletSecret) -> "RecordBackup":
        return cls(
            name=record.name,
            address=record.address,
            version=record.version,
            workchain=record.workchain,
            subwallet_id=record.subwallet_id,
            mnemonics=cls._wallet_secret_to_string(secret),
            comment=record.comment,
        )

    def secret(self) -> WalletSecret:
        if mnemonic_is_valid(self.mnemonics.split()):
            encoded_mnemonics = self.mnemonics.encode('utf-8')
            return WalletSecret(encoded_mnemonics)

        pk = bytes.fromhex(self.mnemonics)
        return WalletSecret(pk)

    @validator("mnemonics", always=True)
    def _validate_mnemonics(cls, v, values):
        if mnemonic_is_valid(v.split()):
            return v

        try:
            pk = bytes.fromhex(v)
            _ = WalletSecret(pk)
        except (ValueError, UnknownSecretKind) as exc:
            raise exc

        return v

    @classmethod
    def _wallet_secret_to_string(cls, secret: WalletSecret) -> str:
        """ If mnemonics are present - return mnemonics
            Otherwise - return private key in hex format"""
        if secret.mnemonics:
            return secret.mnemonics
        else:
            return secret.private_key[:32].hex().upper()


class KeystoreBackup(BaseModel):
    version: int = settings.CURRENT_KEYSTORE_VERSION
    records: List[RecordBackup]
    contacts: List[WhitelistContact] = []

    @classmethod
    def backup_json(cls, keystore: BaseKeyStore) -> Dict:
        records: List[RecordBackup] = []
        for record in keystore.get_records(False):
            secret = keystore.get_secret(record)
            records.append(RecordBackup.from_record(record, secret))

        return cls(records=records, contacts=keystore.contacts, version=keystore.version).dict()

    @classmethod
    def restore_from_tons(cls, json_data: Union[Dict, List]) -> 'KeystoreBackup':
        records: List[RecordBackup] = []
        contacts: List[WhitelistContact] = []

        version = 1 if isinstance(json_data, list) else json_data["version"]

        if version == 1:
            raw_records = json_data
        else:
            try:
                raw_records = json_data['records']
            except KeyError:
                raise InvalidBackupError('Invalid backup: "records" key does not exist')

        raw_contacts = []
        if version >= 4:
            try:
                raw_contacts = json_data['contacts']
            except KeyError:
                raise InvalidBackupError('Invalid backup: "contacts" key does not exist')

        try:
            for raw_record in raw_records:
                records.append(RecordBackup.parse_obj(raw_record))
        except ValidationError:
            raise InvalidBackupError('Invalid backup: validation failed while parsing records')

        try:
            for raw_contact in raw_contacts:
                contacts.append(WhitelistContact.parse_obj(raw_contact))
        except ValidationError:
            raise InvalidBackupError('Invalid backup: validation failed while parsing contacts')

        return cls(records=records, contacts=contacts, version=version)

    @classmethod
    def restore_from_ton_cli(cls, json_data: Dict) -> 'KeystoreBackup':
        records: List[RecordBackup] = []
        for raw_record in json_data:
            backup_record = TonCliRecordBackup.parse_obj(
                raw_record).to_backup_record()
            if backup_record:
                records.append(backup_record)

        return cls(records=records, contacts=[])
