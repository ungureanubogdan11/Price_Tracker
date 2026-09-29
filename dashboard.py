import os
import json
import streamlit as st
import pandas as pd

def load_history(filename = "prices.json") -> dict:
    if not os.path.exists(filename):
        return {}
    
    if os.path.exists(filename) and os.path.getsize(filename) == 0:
        return {}
    
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def get_raw_data(filename = "prices.json") -> list:
    history = load_history(filename)

    raw_data = []

    for url, data in history.items():
        data_line = {}
        data_line["url"] = url
        data_line.update(data)
        raw_data.append(data_line)
    
    return raw_data

raw_data = get_raw_data()
df = pd.DataFrame(raw_data)


# search bar
search_query = st.sidebar.text_input("Search sets or set number:", "")
if search_query:
    df = df[df["title"].str.contains(search_query, case=False)]

# filter by vouchers
only_vouchers = st.sidebar.checkbox("Only show active vouchers")
if only_vouchers:
    df = df[df["voucher_discount"] > 0]


st.title("Price Tracker for Lego on [eMag](https://emag.ro)")

total_sets = len(df)
st.subheader(f"Total sets tracked: {total_sets}")


#stats cards
expensive_idx = df["best_price"].idxmax()
expensive_row = df.loc[expensive_idx]

cheapest_idx = df["best_price"].idxmin()
cheapest_row = df.loc[cheapest_idx]

discount_idx = df["voucher_discount"].idxmax()
discouont_row = df.loc[discount_idx]



col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Most expensive set:",
        value=f"{expensive_row['best_price']:.2f} Lei",
        delta=expensive_row['title'][:25] + "..."
    )
    st.link_button("View", expensive_row["url"], use_container_width=True)

with col2:
    st.metric(
        label="Cheapest set:",
        value=f"{cheapest_row['best_price']:.2f} Lei",
        delta=cheapest_row['title'][:25] + "..."
    )
    st.link_button("View", cheapest_row["url"], use_container_width=True)

with col3:
    st.metric(
        label="Biggest discount:",
        value=f"{discouont_row['voucher_discount']}%",
        delta=discouont_row['title'][:25] + "..."
    )
    st.link_button("View", discouont_row["url"], use_container_width=True)

st.subheader("Tracked Sets:")

#display all sets as cards

for col, row in df.iterrows():
    with st.container(border=True):
        st.markdown(f"### {row['title']}")
        info_col, btn_col = st.columns([3, 1])
        with info_col:
            st.markdown(f"**Current Price:** `{row['best_price']:.2f} Lei`")
            if row.get("voucher_discount", 0) > 0:
                st.caption(f"Voucher Applied: -{row['voucher_discount']}%")
            else:
                st.caption("Standard price (No active voucher)")
                
        with btn_col:
            st.link_button("View on eMAG", row["url"])
