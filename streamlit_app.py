import pandas as pd
#import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

import plotly.express as px


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_date').agg({
        "order_id": "nunique",
        "total_price": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "total_price": "revenue"
    }, inplace=True)
    
    return daily_orders_df



def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby("product_name").quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order_items_df


def create_bygender_df(df):
    bygender_df = df.groupby(by="gender").customer_id.nunique().reset_index()
    bygender_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bygender_df


def create_byage_df(df):
    byage_df = df.groupby(by="age_group").customer_id.nunique().reset_index()
    byage_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    byage_df['age_group'] = pd.Categorical(byage_df['age_group'], ["Youth", "Adults", "Seniors"])
    
    return byage_df


def create_bystate_df(df):
    bystate_df = df.groupby(by="state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bystate_df


def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_date": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "total_price": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_date"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

all_df = pd.read_csv("all_data.csv")

datetime_columns = ["order_date", "delivery_date"]
all_df.sort_values(by="order_date", inplace=True)
all_df.reset_index(inplace=True)
 
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])


min_date = all_df["order_date"].min()
max_date = all_df["order_date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image(r"C:\Users\HP\streamlit_veven\img\tshirt.png", width=150)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )


main_df = all_df[(all_df["order_date"] >= str(start_date)) & 
                (all_df["order_date"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
sum_order_items_df = create_sum_order_items_df(main_df)
bygender_df = create_bygender_df(main_df)
byage_df = create_byage_df(main_df)
bystate_df = create_bystate_df(main_df)
rfm_df = create_rfm_df(main_df)

st.header('My Collection Dashboard :sparkles:')


st.subheader('Daily Orders')

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "AUD", locale='es_CO'
    )
    st.metric("Total Revenue", value=total_revenue)

fig_daily = px.line(
    daily_orders_df,
    x="order_date",
    y="order_count",
    markers=True,
    title="Daily Order Count"
)

st.plotly_chart(fig_daily, use_container_width=True)


st.subheader("Best & Worst Performing Product")

col1, col2 = st.columns(2)

with col1:
    fig_best = px.bar(
        sum_order_items_df.head(5),
        x="quantity_x",
        y="product_name",
        orientation="h",
        title="Best Performing Product",
        color="product_name"
    )
    st.plotly_chart(fig_best, use_container_width=True)

with col2:
    fig_worst = px.bar(
        sum_order_items_df.sort_values("quantity_x").head(5),
        x="quantity_x",
        y="product_name",
        orientation="h",
        title="Worst Performing Product",
        color="product_name"
    )
    st.plotly_chart(fig_worst, use_container_width=True)




fig_gender = px.bar(
    bygender_df.sort_values("customer_count", ascending=False),
    x="gender",
    y="customer_count",
    title="Number of Customer by Gender",
    color="gender"
)
st.plotly_chart(fig_gender, use_container_width=True)


fig_age = px.bar(
    byage_df,
    x="age_group",
    y="customer_count",
    title="Number of Customer by Age Group",
    color="age_group"
)
st.plotly_chart(fig_age, use_container_width=True)



fig_state = px.bar(
    bystate_df.sort_values("customer_count", ascending=False),
    x="customer_count",
    y="state",
    orientation="h",
    title="Number of Customer by State",
    color="state"
)
st.plotly_chart(fig_state, use_container_width=True)


st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Average Recency (days)", round(rfm_df.recency.mean(), 1))

with col2:
    st.metric("Average Frequency", round(rfm_df.frequency.mean(), 2))

with col3:
    st.metric(
        "Average Monetary",
        format_currency(rfm_df.monetary.mean(), "AUD", locale='es_CO')
    )




col1, col2, col3 = st.columns(3)

with col1:
    fig_recency = px.bar(
        rfm_df.sort_values("recency").head(5),
        x="customer_id",
        y="recency",
        title="Top Customers by Recency"
    )
    st.plotly_chart(fig_recency, use_container_width=True)

with col2:
    fig_frequency = px.bar(
        rfm_df.sort_values("frequency", ascending=False).head(5),
        x="customer_id",
        y="frequency",
        title="Top Customers by Frequency"
    )
    st.plotly_chart(fig_frequency, use_container_width=True)

with col3:
    fig_monetary = px.bar(
        rfm_df.sort_values("monetary", ascending=False).head(5),
        x="customer_id",
        y="monetary",
        title="Top Customers by Monetary"
    )
    st.plotly_chart(fig_monetary, use_container_width=True)

st.caption("Copyright © MyCollection 2025")
