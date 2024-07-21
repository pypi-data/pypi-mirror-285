import weakref
from datetime import datetime

from tons.tonclient.utils import BaseKeyStore, Record, KeyStoreTypeEnum
from tons.tonsdk.utils import Address
from tons.ui._utils import SharedObject, dns_expires_soon
from tons.ui.gui.exceptions import CtxReferenceError
from tons.ui.gui.widgets import DnsListItemData


class DnsInformationModel:
    def __init__(self, ctx: SharedObject,
                 dns_item: DnsListItemData,
                 keystore: BaseKeyStore,
                 record: Record):

        if Address(dns_item.wallet_address) != Address(record.address) or dns_item.wallet_name != record.name:
            raise ValueError('DNS information window model initialisation error: wallet information mismatch.')

        self.__ctx = weakref.ref(ctx)
        self._keystore = keystore
        self._dns_item = dns_item
        self._record = record

    @property
    def _ctx(self) -> SharedObject:
        if self.__ctx() is None:
            raise CtxReferenceError
        return self.__ctx()

    @property
    def dns_expires_soon(self) -> bool:
        return dns_expires_soon(self._dns_item.nft_info, self._ctx.config.dns.max_expiring_in)

    @property
    def domain(self) -> str:
        return self._dns_item.domain

    @property
    def owner_wallet_name(self) -> str:
        return self._record.name

    @property
    def owner_wallet_address(self) -> str:
        return self._record.address_to_show

    @property
    def expires(self) -> datetime:
        try:
            return datetime.utcfromtimestamp(int(self._dns_item.dns_expires))
        except AttributeError:
            raise ValueError('DNS expiration timestamp is invalid')

    @property
    def expires_in(self) -> str:
        return '(' + ' '.join(self._dns_item.dns_expiring_verbal_and_digits[::-1]) + ')'

    @property
    def ownership_status(self) -> str:
        if self._dns_item.is_owned:
            return 'Owned'
        else:
            return 'Taken'

    @property
    def contract_address(self) -> str:
        return self._dns_item.dns_account_address

    @property
    def record(self) -> Record:
        return self._record

    @property
    def keystore(self) -> BaseKeyStore:
        return self._keystore

    @property
    def ctx(self) -> SharedObject:
        return self._ctx
