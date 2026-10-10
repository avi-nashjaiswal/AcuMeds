"""
Paytm payment helper utilities.
"""
import json
from typing import Dict, Optional

import requests
import paytmchecksum
from flask import current_app, url_for


class PaytmError(Exception):
    """Paytm integration error."""


def _paytm_base_url() -> str:
    env = current_app.config.get('PAYTM_ENV', 'prod')
    return 'https://securegw.paytm.in' if env == 'prod' else 'https://securegw-stage.paytm.in'


def _checkout_js_url(mid: str) -> str:
    base = _paytm_base_url()
    return f"{base}/merchantpgpui/checkoutjs/merchants/{mid}.js"


def build_order_id(order_id: int) -> str:
    return f"MED-{order_id}"


def parse_order_id(paytm_order_id: str) -> Optional[int]:
    if not paytm_order_id:
        return None
    if paytm_order_id.startswith('MED-'):
        suffix = paytm_order_id.split('-', 1)[1]
        if suffix.isdigit():
            return int(suffix)
    return None


def initiate_transaction(order, amount: float, customer_id: str) -> Dict[str, str]:
    mid = current_app.config.get('PAYTM_MID')
    merchant_key = current_app.config.get('PAYTM_MERCHANT_KEY')
    website = current_app.config.get('PAYTM_WEBSITE', 'DEFAULT')

    if not mid or not merchant_key:
        raise PaytmError('Paytm credentials are missing. Set PAYTM_MID and PAYTM_MERCHANT_KEY.')

    callback_url = current_app.config.get('PAYTM_CALLBACK_URL') or url_for(
        'order.paytm_callback', _external=True
    )

    paytm_order_id = build_order_id(order.id)
    body = {
        'requestType': 'Payment',
        'mid': mid,
        'websiteName': website,
        'orderId': paytm_order_id,
        'callbackUrl': callback_url,
        'txnAmount': {
            'value': f"{amount:.2f}",
            'currency': 'INR'
        },
        'userInfo': {
            'custId': customer_id
        }
    }

    signature = paytmchecksum.generateSignature(json.dumps(body), merchant_key)
    payload = {
        'body': body,
        'head': {
            'signature': signature
        }
    }

    url = f"{_paytm_base_url()}/theia/api/v1/initiateTransaction?mid={mid}&orderId={paytm_order_id}"
    response = requests.post(url, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()

    txn_token = data.get('body', {}).get('txnToken')
    if not txn_token:
        result_info = data.get('body', {}).get('resultInfo', {})
        message = result_info.get('resultMsg') or 'Failed to initiate Paytm transaction.'
        raise PaytmError(message)

    return {
        'order_id': paytm_order_id,
        'txn_token': txn_token,
        'mid': mid,
        'amount': f"{amount:.2f}",
        'callback_url': callback_url,
        'checkout_js_url': _checkout_js_url(mid)
    }


def verify_signature(params: Dict[str, str]) -> bool:
    merchant_key = current_app.config.get('PAYTM_MERCHANT_KEY')
    if not merchant_key:
        return False

    payload = dict(params)
    checksum = payload.pop('CHECKSUMHASH', '')
    if not checksum:
        return False

    return paytmchecksum.verifySignature(payload, merchant_key, checksum)


def is_payment_success(params: Dict[str, str]) -> bool:
    return params.get('STATUS') == 'TXN_SUCCESS'
