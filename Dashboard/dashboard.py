import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

def create_yearly_orders_df(df):
    yearly_orders_df = df.resample(rule='Y', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    yearly_orders_df = yearly_orders_df.reset_index()
    yearly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return yearly_orders_df

def create_cities_df(df):
    bycity_df = df.groupby(by="customer_city").customer_id.nunique().reset_index()
    # Mengganti nama kolom
    bycity_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    bycity_df = bycity_df.sort_values(by="customer_count", ascending=False).head(5)
    return bycity_df


def create_category_summary(df):
    category_summary = seller_product_df.groupby('product_category_name').agg({
    'product_id': 'nunique',  
    'price': 'sum'            
}).reset_index()

# Mengganti nama kolom untuk kemudahan
    category_summary.columns = ['Product Category', 'Unique Product Count', 'Total Price']
    category_summary = category_summary.sort_values(by='Total Price', ascending=False)
    
    return category_summary

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "nunique",
        "payment_value": "sum"
    })
    
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    rfm_df['max_order_timestamp'] = pd.to_datetime(rfm_df['max_order_timestamp'])
    
    recent_date = df['order_purchase_timestamp'].max().date()
    rfm_df['recency'] = (recent_date - rfm_df['max_order_timestamp'].dt.date).apply(lambda x: x.days)
    

    return rfm_df


customers_df = pd.read_csv("Dashboard/customer_order.csv")
seller_product_df = pd.read_csv("Dashboard/seller_product.csv")

datetime_columns = ["order_purchase_timestamp", "order_estimated_delivery_date"]
customers_df.sort_values(by="order_purchase_timestamp", inplace=True)
customers_df.reset_index(drop=True, inplace=True)

for column in datetime_columns:
    customers_df[column] = pd.to_datetime(customers_df[column])

    min_date = customers_df["order_purchase_timestamp"].min()
max_date = customers_df["order_purchase_timestamp"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# st.dataframe(main_df)
main_df = customers_df[(customers_df["order_purchase_timestamp"] >= str(start_date)) & 
                (customers_df["order_purchase_timestamp"] <= str(end_date))]

# # Menyiapkan berbagai dataframe
yearly_orders_df = create_yearly_orders_df(main_df)
bycity_df = create_cities_df(main_df)
category_summary_df = create_category_summary(main_df)
rfm_df = create_rfm_df(main_df)


st.header('E-Commerce Publik Dashboard :sparkles:')
st.subheader("Number of Orders per Year")

col1, col2 = st.columns(2)

with col1:
    total_orders = yearly_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(yearly_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))

# Membuat visualisasi
plt.figure(figsize=(10, 5))
plt.plot(
    yearly_orders_df["order_purchase_timestamp"],
    yearly_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#72BCD4"
)
plt.title("Number of Orders per Year", loc="center", fontsize=20)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
plt.xlabel("Date", fontsize=12)
plt.ylabel("Number of Orders", fontsize=12)
plt.grid()

# Menampilkan plot di Streamlit
st.pyplot(plt)

col1, col2 = st.columns(2)

st.subheader("Top 5 Customers by City")

# Membuat visualisasi
plt.figure(figsize=(10, 5))

sns.barplot(
    y="customer_count", 
    x="customer_city",
    data=bycity_df.sort_values(by="customer_count", ascending=False).head(5),
    color='skyblue'
)

# Mengatur batas sumbu y
plt.ylim(0, bycity_df['customer_count'].max() * 1.1)

# Menambahkan judul dan label
plt.title("Number of Customers by City", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)

# Menampilkan grafik
plt.show()

# Tampilkan plot di Streamlit
st.pyplot(plt)


st.subheader("Top Product Categories: Total Price and Unique Product Coun")

categories = category_summary_df.head(5)

fig, ax1 = plt.subplots(figsize=(10, 6))

ax1.bar(categories['Product Category'], categories['Total Price'], color='skyblue', alpha=0.7, label='Total Price')
ax1.set_ylabel('Total Price', color='skyblue')
ax1.tick_params(axis='y', labelcolor='skyblue')

ax2 = ax1.twinx()
ax2.plot(categories['Product Category'], categories['Unique Product Count'], color='orange', marker='o', linewidth=2, label='Unique Product Count')
ax2.set_ylabel('Unique Product Count', color='orange')
ax2.tick_params(axis='y', labelcolor='orange')

plt.title('Top 5 Product Categories: Total Price and Unique Product Count', fontsize=16)
fig.tight_layout() 
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

plt.xticks(rotation=45)
plt.show()

# Tampilkan plot di Streamlit
st.pyplot(fig)

st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    avg_frequency = format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)


st.pyplot(fig)

st.caption('Copyright © Arif Wicaksono 2025')

customers_df.to_csv("customer_order.csv", index=False)
seller_product_df.to_csv("seller_product.csv", index=False)
