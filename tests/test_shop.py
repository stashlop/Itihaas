"""Merchandise catalogue, cart and checkout."""
import io

import pytest

from itihaas.merchandise_models import CartItem, Merchandise, Order
from itihaas.seed import DEMO_PRODUCTS, seed_merchandise


@pytest.fixture()
def products(db):
    seed_merchandise()
    return Merchandise.query.order_by(Merchandise.id).all()


def test_seed_is_idempotent(db):
    assert seed_merchandise() == len(DEMO_PRODUCTS)
    assert seed_merchandise() == 0


def test_shop_lists_and_filters(client, products):
    page = client.get("/shop").get_data(as_text=True)
    assert "Classic Kurta" in page and "Heritage Postcard Set" in page
    filtered = client.get("/shop?category=souvenirs").get_data(as_text=True)
    assert "Heritage Postcard Set" in filtered and "Classic Kurta" not in filtered


def test_empty_shop_shows_empty_state(client):
    assert "being stocked" in client.get("/shop").get_data(as_text=True)


def test_product_detail_and_404(client, products):
    assert client.get(f"/product/{products[0].id}").status_code == 200
    assert client.get("/product/9999").status_code == 404


def test_add_to_cart_respects_stock(client, user, products, db):
    product = products[0]
    product.stock = 3
    db.session.commit()
    client.post(f"/add-to-cart/{product.id}", data={"quantity": "2"})
    client.post(f"/add-to-cart/{product.id}", data={"quantity": "2"})  # would exceed stock
    assert CartItem.query.one().quantity == 2
    assert client.post(f"/add-to-cart/{product.id}", data={"quantity": "abc"}).status_code == 302
    assert CartItem.query.one().quantity == 2


def test_checkout_creates_order_and_reduces_stock(client, user, products):
    product = products[0]
    start_stock = product.stock
    client.post(f"/add-to-cart/{product.id}", data={"quantity": "2"})
    response = client.post("/checkout", data={"shipping_address": "12 Heritage Lane, Jaipur 302001", "payment_method": "upi"})
    assert response.status_code == 302 and "/order-confirmation/" in response.headers["Location"]
    order = Order.query.one()
    assert order.payment_status == "completed" and order.total_amount == 2 * product.price
    assert Merchandise.query.filter_by(id=product.id).one().stock == start_stock - 2
    assert CartItem.query.count() == 0
    assert client.get(response.headers["Location"]).status_code == 200


def test_checkout_blocks_when_stock_ran_out(client, user, products, db):
    product = products[0]
    client.post(f"/add-to-cart/{product.id}", data={"quantity": "2"})
    product.stock = 1
    db.session.commit()
    client.post("/checkout", data={"shipping_address": "12 Heritage Lane, Jaipur 302001", "payment_method": "cod"})
    assert Order.query.count() == 0


def test_checkout_validates_input(client, user, products):
    client.post(f"/add-to-cart/{products[0].id}", data={"quantity": "1"})
    client.post("/checkout", data={"shipping_address": "short", "payment_method": "upi"})
    client.post("/checkout", data={"shipping_address": "12 Heritage Lane, Jaipur", "payment_method": "crypto"})
    assert Order.query.count() == 0


def test_users_cannot_touch_other_carts_or_orders(client, user, products, make_user, login):
    client.post(f"/add-to-cart/{products[0].id}", data={"quantity": "1"})
    client.post("/checkout", data={"shipping_address": "12 Heritage Lane, Jaipur 302001", "payment_method": "cod"})
    order_id = Order.query.one().id
    client.post(f"/add-to-cart/{products[1].id}", data={"quantity": "1"})
    item_id = CartItem.query.one().id
    client.get("/logout")
    make_user(email="other@example.com")
    login(email="other@example.com")
    assert client.post(f"/remove-from-cart/{item_id}").status_code == 403
    assert client.get(f"/order-confirmation/{order_id}").status_code == 403


def test_guide_product_upload_validates_images(client, make_user, login, app):
    make_user(email="guide@example.com", guide=True)
    login(email="guide@example.com")
    form = {"name": "Tote", "description": "Hand-made", "price": "500", "stock": "5", "category": "accessories"}

    bad = client.post("/add-product", data={**form, "image": (io.BytesIO(b"<?php"), "shell.php")},
                      content_type="multipart/form-data")
    assert bad.status_code == 302 and Merchandise.query.count() == 0

    good = client.post("/add-product", data={**form, "image": (io.BytesIO(b"\x89PNG fake"), "tote.png")},
                       content_type="multipart/form-data")
    assert good.status_code == 302
    product = Merchandise.query.one()
    assert product.image_url.startswith("/static/uploads/product") and product.image_url.endswith("_tote.png")


def test_regular_user_cannot_add_products(client, user):
    client.post("/add-product", data={"name": "x"})
    assert Merchandise.query.count() == 0
