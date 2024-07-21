import click

from tons.tonclient import ton_exceptions_handler
from ._base_cmd import cli
from .._utils import click_ton_exception_handler, with_address
from ..._utils import SharedObject


@cli.group()
def contract():
    """
    Operate with contracts
    """


@contract.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_address
@click.pass_obj
def info(shared_object: SharedObject, address: str):
    """
    Show TON blockchain information
    """
    addr_info = shared_object.ton_client.get_address_information(address)
    for k, v in addr_info.dict().items():
        click.echo(str(k) + ': ' + str(v))


@contract.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_address
@click.pass_obj
def balance(shared_object: SharedObject, address: str):
    """
    Show the balance of a contract
    """
    addr_info = shared_object.ton_client.get_address_information(address)
    click.echo(addr_info.balance)


@contract.command()
@ton_exceptions_handler(click_ton_exception_handler)
@with_address
@click.pass_obj
def seqno(shared_object: SharedObject, address: str):
    """
    Show seqno
    """
    _seqno = shared_object.ton_client.seqno(address)
    click.echo(_seqno)
