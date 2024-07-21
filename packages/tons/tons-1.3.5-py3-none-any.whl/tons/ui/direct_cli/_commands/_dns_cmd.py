from typing import List, Dict
from uuid import UUID

import click

from tons.tonclient._client._base import NftItemInfoResult, BroadcastStatusEnum, BroadcastResult
from tons.tonclient._exceptions import TonDappError
from tons.tonsdk.contract.wallet import Wallets
from tons.tonsdk.utils import Address
from ._base_cmd import cli
from .._utils import with_keystore, CustomClickException, with_daemon
from ..._utils import SharedObject, form_dns_table, dns_expires_soon, get_wallet_from_record_ctx


@cli.group()
def dns():
    """
    Operate with DNS
    """


@dns.command(name='list')
@with_keystore(sensitive_data=False)
@click.option('--expire-soon', is_flag=True, default=False,
              help="Display only domains that expire soon")
@click.option('--exclude-not-owned', is_flag=True, default=False,
              help="Display only items with claimed ownership")
@click.pass_obj
def list_(shared_object: SharedObject, expire_soon: bool, exclude_not_owned: bool):
    """
    Display list of DNS belonging to wallets from the keystore
    """
    dns_items_info = __fetch_dns_items(shared_object, expire_soon)
    table = form_dns_table(dns_items_info, not exclude_not_owned)
    click.echo(table)


@dns.command()
@with_keystore(sensitive_data=True)
@with_daemon
@click.option('--expiring-soon', '-e', is_flag=True, default=False,
              help="Refresh all domains that expire soon")
@click.option('--domain', '-d', type=str, required=False,
              help="Refresh a specific domain")
@click.option('--exclude-not-owned', is_flag=True, default=False,
              help="Refresh only items with claimed ownership")
@click.pass_obj
def refresh(shared_object: SharedObject, expiring_soon: bool, domain: str, exclude_not_owned: bool):
    """
    Refresh DNS ownership
    """
    if bool(domain) == expiring_soon:
        raise CustomClickException("Either specify a domain xor run with --expiring-soon flag")
    dns_items = __fetch_dns_items(shared_object, expiring_soon)

    if domain:
        if domain.endswith('.ton'):
            domain = domain[:-4]
        try:
            dns_items = [next(item for item in dns_items if item.dns_domain == domain)]
        except StopIteration:
            raise CustomClickException(f"{domain}.ton is not held by any wallet in your keystore")

    if exclude_not_owned:
        dns_items = [item for item in dns_items if item.owner_address]

    if expiring_soon or exclude_not_owned:
        if len(dns_items) == 0:
            click.echo("No domain requires refreshment.")
            return

    pending_tasks: Dict[UUID, NftItemInfoResult] = {}

    for item in dns_items:
        record = shared_object.keystore.get_record_by_address(Address(item.owner_or_max_bidder))
        wallet = get_wallet_from_record_ctx(shared_object, record)
        task_id = shared_object.ton_daemon.refresh_dns_ownership(wallet, item)
        pending_tasks[task_id] = item

    while len(pending_tasks) > 0:
        r = shared_object.ton_daemon.results_queue.get()
        dns_item = pending_tasks[r.task_id]
        result_description = str(r.broadcast_result)
        if isinstance(r.broadcast_result, BroadcastResult):
            if r.broadcast_result.status in [BroadcastStatusEnum.committed, BroadcastStatusEnum.broadcasted]:
                try:
                    updated_dns_info = shared_object.ton_client.get_dns_domain_information(dns_item.dns_domain)
                except TonDappError as e:
                    result_description = f"The transaction has been {r.broadcast_result.status}, but failed to check " \
                                         f"if the ownership has been refreshed, due to error: " + str(e)
                else:
                    if updated_dns_info.dns_last_fill_up_time > dns_item.dns_last_fill_up_time:
                        result_description = "Ownership refreshed successfully."
                    else:
                        result_description = f"The transaction has been {r.broadcast_result.status}, but failed to " \
                                             f"verify that the ownership has been refreshed. " \
                                             f"Please check the domain ownership status manually after a few minutes. "

        click.echo(f"{dns_item.dns_domain}.ton: {result_description}")

        del pending_tasks[r.task_id]


def __fetch_dns_items(shared_object: SharedObject, only_expire_soon: bool = False) -> List[NftItemInfoResult]:
    addresses = [record.address
                 for record in shared_object.keystore.get_records(shared_object.config.tons.sort_keystore)]
    dns_items_info = shared_object.ton_client.get_dns_items_information(addresses)
    max_expiring_in = shared_object.config.dns.max_expiring_in
    if only_expire_soon:
        dns_items_info = list(filter(lambda dns_item: dns_expires_soon(dns_item, max_expiring_in),
                                     dns_items_info))
    return dns_items_info
