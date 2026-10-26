def summarize_orders(orders):
    return {
        "order_count": len(orders),
        "total_quantity": sum(order["quantity"] for order in orders),
        "total_amount": sum(
            order["quantity"] * order["unit_price"] for order in orders
        ),
    }


def format_summary(orders):
    summary = summarize_orders(orders)
    return (
        f"Orders: {summary['order_count']}, "
        f"Quantity: {summary['total_quantity']}, "
        f"Total: {summary['total_amount']}"
    )
