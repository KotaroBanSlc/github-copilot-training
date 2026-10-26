SAMPLE_SALES_RECORDS = [
    {"region": "east", "product_name": "notebook", "quantity": 3, "unit_price": 1200},
    {"region": "west", "product_name": "pen", "quantity": 10, "unit_price": 150},
    {"region": "east", "product_name": "pen", "quantity": 4, "unit_price": 150},
    {"region": "north", "product_name": "folder", "quantity": 5, "unit_price": 300},
]


def calculate_line_amount(sales_record):
    return sales_record["quantity"] * sales_record["unit_price"]


def calculate_total_amount(sales_records):
    total_amount = 0
    for sales_record in sales_records:
        line_amount = calculate_line_amount(sales_record)
        total_amount += line_amount
    return total_amount
