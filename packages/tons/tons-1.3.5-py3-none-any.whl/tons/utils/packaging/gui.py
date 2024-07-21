from pathlib import Path
from typing import List
from PyQt6.uic import pyuic

""" A script to convert all of the *.ui files to auto generated *.py files """
UIS: List[str] = ['create_keystore',
                  'wallet_information',
                  'contact_information',
                  'create_batch_wallet',
                  'create_wallet',
                  'dialog_keystore_password',
                  'main_window',
                  'import_wallet_from_mnemonics',
                  'import_wallet_from_pk',
                  'create_contact',
                  'preferences',
                  'transfer',
                  'select_wallet',
                  'create_batch_wallet_progress',
                  'dialog_qr',
                  'transactions_history',
                  'dns_information']


def __convert_qt_ui(uis_dir: Path, uis_list: List[str], verbose: bool = False):
    pys_dir: Path = uis_dir
    for ui in uis_list:
        ui_path = uis_dir / Path(ui).with_suffix('.ui')
        py_path = pys_dir / Path(ui).with_suffix('.py')

        pyuic.generate(ui_path, py_path, indent=4, execute=False, max_workers=0)
        if verbose:
            print(f'{ui_path} -> {py_path}')


def convert_qt_ui(verbose: bool = False):
    __convert_qt_ui(Path('./tons/ui/gui/uis/_qt_assets'), UIS, verbose)


if __name__ == "__main__":
    convert_qt_ui(verbose=True)
