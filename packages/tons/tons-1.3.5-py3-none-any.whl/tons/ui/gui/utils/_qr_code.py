from typing import Optional
import urllib.parse
import qrcode


def construct_transfer_uri(address: str,
                           amount: Optional[int] = None,  # nanoton
                           text: Optional[str] = None):
    prefix = 'ton://transfer/'
    uri = f'{prefix}{str(address)}'

    params = []
    if amount is not None:
        params.append(f'amount={amount}')
    if text is not None:
        text = urllib.parse.quote(text)
        params.append(f'text={text}')

    if len(params) == 0:
        return uri

    params = '&'.join(params)
    uri = '?'.join([uri, params])

    return uri


def qr_image(data: str):
    img = qrcode.make(data)
    return img


def _generate_sample():
    uri = ''
    qr_img = qr_image(uri)
    qr_img.save('tons/ui/gui/uis/_qt_assets/images/qr_sample.png')


if __name__ == "__main__":
    _generate_sample()
