"""Exercise actual pricing helpers without importing the app or contacting Stripe/DB."""
import ast
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest


def pricing_scope():
    path = Path(__file__).resolve().parents[1] / 'server.py'
    tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    functions = {'_get_live_stripe_plan_prices_sync', '_fetch_stripe_pricing_sync', '_format_kr'}
    nodes = [node for node in tree.body if (
        isinstance(node, ast.FunctionDef) and node.name in functions
    ) or (
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PUBLIC_PRICING_FALLBACK' for t in node.targets)
    )]
    from typing import Optional
    scope = {'Optional': Optional, 'logger': logging.getLogger(__name__)}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), scope)
    return scope


@pytest.mark.parametrize('old_first', [False, True])
@pytest.mark.parametrize('expanded_default', [False, True])
def test_default_price_wins_in_any_list_order(old_first, expanded_default):
    scope = pricing_scope()
    product = SimpleNamespace(name='Thai2Drive 3 Months', default_price=(
        SimpleNamespace(id='price_249') if expanded_default else 'price_249'))
    current = SimpleNamespace(id='price_249', product=product, unit_amount=24900, currency='nok', livemode=True)
    old = SimpleNamespace(id='price_299', product=product, unit_amount=29900, currency='nok', livemode=True)
    prices = [old, current] if old_first else [current, old]
    for key, amount in [('monthly', 9900), ('lifetime', 69900)]:
        p = scope['PUBLIC_PRICING_FALLBACK'][key]
        price_id = 'price_' + key
        prices.append(SimpleNamespace(id=price_id, product=SimpleNamespace(
            name=p['stripe_product_name'], default_price=price_id),
            unit_amount=amount, currency='nok', livemode=True))
    scope['_stripe_module'] = lambda: SimpleNamespace(Price=SimpleNamespace(list=lambda **kw: SimpleNamespace(data=prices)))
    data = scope['_get_live_stripe_plan_prices_sync']()
    assert data is not None and data['source'] == 'stripe_live'
    plan = next(p for p in data['plans'] if p['id'] == 'three_months')
    assert plan['stripe_price'] is current  # checkout uses this same object
    assert plan['stripe_price_id'] == 'price_249'
    assert plan['amount'] == 249 and plan['display'] == '249 kr'
    public = scope['_fetch_stripe_pricing_sync']()
    assert all('stripe_price' not in p for p in public['plans'])


def test_unapproved_default_amount_fails_closed():
    scope = pricing_scope()
    price = SimpleNamespace(id='price_unapproved', product=SimpleNamespace(
        name='Thai2Drive 3 Months', default_price='price_unapproved'),
        unit_amount=19900, currency='nok', livemode=True)
    scope['_stripe_module'] = lambda: SimpleNamespace(Price=SimpleNamespace(list=lambda **kw: SimpleNamespace(data=[price])))
    assert scope['_get_live_stripe_plan_prices_sync']() is None
