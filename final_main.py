import pandas as pd
from datetime import datetime
 
#Read source files
 
customers_df = pd.read_csv("customers.csv")
products_df = pd.read_csv("products.csv")
orders_df = pd.read_csv("orders.csv")
 
print("Files loaded successfully\n")
 
print("Customers:")
print(customers_df.head())
 
print("\nProducts:")
print(products_df.head())
 
print("\nOrders:")
print(orders_df.head())

#Schema validation
 
expected_order_columns = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "order_date"
]
if set(orders_df.columns) != set(expected_order_columns):
    raise Exception(
        f"Schema mismatch detected.\n"
        f"Expected: {expected_order_columns}\n"
        f"Found: {list(orders_df.columns)}"
    )
 
print("\nSchema validation passed")
 
#REMOVE DUPLICATES
 
customers_df = customers_df.drop_duplicates()
 
orders_df = orders_df.drop_duplicates(
    subset=["order_id"]
)
 
print("Duplicate records removed")
 
#IDENTIFY INVALID ORDERS
 
invalid_orders = orders_df[
    ~orders_df["customer_id"].isin(
        customers_df["customer_id"]
    )
]
 
print("\nInvalid Orders:")
print(invalid_orders)
 
invalid_orders.to_csv(
    "invalid_orders.csv",
    index=False
)
 
#KEEP ONLY VALID ORDERS
 
valid_orders = orders_df[
    orders_df["customer_id"].isin(
        customers_df["customer_id"]
    )
].copy()

print(f"\nValid Orders: \n{valid_orders}")
 
#HANDLE LATE ARRIVING RECORDS
 
current_load_date = pd.to_datetime(
    "2026-11-05"
)
 
valid_orders["order_date"] = pd.to_datetime(
    valid_orders["order_date"]
)
 
valid_orders["late_flag"] = (
    valid_orders["order_date"]
    < current_load_date
)
 
print("\nLate Records:")
print(
    valid_orders[
        valid_orders["late_flag"] == True
    ]
)

#JOIN CUSTOMER DATA
 
sales_df = pd.merge(
    valid_orders,
    customers_df,
    on="customer_id",
    how="inner"
)
#JOIN PRODUCT DATA
 
sales_df = pd.merge(
    sales_df,
    products_df,
    on="product_id",
    how="inner"
)
 
print("\nCustomer and Product Join Completed")
 
#CALCULATE SALES AMOUNT
 
sales_df["sales_amount"] = (
    sales_df["quantity"]
    * sales_df["price"]
)
 
#CREATE CURATED DATA
 
required_columns = [
    "order_id",
    "customer_id",
    "customer_name",
    "city",
    "product_id",
    "product_name",
    "price",
    "quantity",
    "sales_amount",
    "order_date"
]
 
final_sales = sales_df[
    required_columns
]
 
#SAVE CURATED DATA
 
final_sales.to_csv(
    "curated_sales.csv",
    index=False
)
 
print("\nCurated file created successfully")
 
#RECONCILIATION REPORT
 
source_count = len(orders_df)
target_count = len(final_sales)
 
reconciliation = pd.DataFrame({
    "source_count": [source_count],
    "target_count": [target_count],
    "status": [
        "SUCCESS"
        if source_count >= target_count
        else "FAILED"
    ]
})
 
reconciliation.to_csv(
    "reconciliation_report.csv",
    index=False
)
 
print("\nReconciliation Report")
print(reconciliation)
 
#PIPELINE RUN LOG
 
pipeline_log = pd.DataFrame({
    "run_time": [datetime.now()],
    "source_count": [source_count],
    "target_count": [target_count],
    "invalid_orders": [len(invalid_orders)],
    "status": ["SUCCESS"]
})
 
pipeline_log.to_csv(
    "pipeline_run_log.csv",
    index=False
)
 
print("\nPipeline Log")
print(pipeline_log)
 
#INCREMENTAL LOAD

 
last_loaded_date = pd.to_datetime(
    "2026-11-04"
)
 
incremental_orders = orders_df[
    pd.to_datetime(
        orders_df["order_date"]
    ) > last_loaded_date
]
 
incremental_orders.to_csv(
    "incremental_orders.csv",
    index=False
)
 
print("\nIncremental Records")
print(incremental_orders)
 
#SCD TYPE 2 SAMPLE
 
customer_history = customers_df.copy()
 
customer_history["start_date"] = (
    datetime.today().date()
)
 
customer_history["end_date"] = (
    "9999-12-31"
)
 
customer_history["is_current"] = "Y"
 
customer_history.to_csv(
    "dim_customer_scd2.csv",
    index=False
)
 
print("\nSCD Type 2 Customer Dimension Created")
 
#DATA QUALITY REPORT
 
dq_report = pd.DataFrame({
    "total_orders": [len(orders_df)],
    "valid_orders": [len(valid_orders)],
    "invalid_orders": [len(invalid_orders)]
})
 
dq_report.to_csv(
    "data_quality_report.csv",
    index=False
)
 
print("\nData Quality Report")
print(dq_report)
 
print("\nPipeline Execution Completed Successfully")