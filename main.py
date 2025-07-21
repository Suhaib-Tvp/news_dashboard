

import streamlit as st
import requests
import pandas as pd
import json
import pickle
import matplotlib.pyplot as plt
from datetime import date

# Load sentiment function from pickle
with open("news_model.pkl", "rb") as f:
    get_sentiment = pickle.load(f)

st.set_page_config(page_title="📊 News Sentiment Dashboard", layout="centered")

API_KEY = "pub_90c7e03f76c44364828a85c437caa6c9"  # Replace with your key

st.title("📰 News Sentiment Dashboard")

topic = st.text_input("📌 Enter a topic (e.g., politics, sports)", value="technology")
date_input = st.date_input("📅 Select date", value=date.today())

if st.button("Fetch News"):
    st.info("Fetching news...")

    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q={topic}&country=in&language=en&from_date={date_input}&to_date={date_input}"
    response = requests.get(url)
    data = response.json()
    articles = data.get("results", [])

    if not articles:
        st.warning("⚠️ No news articles found for this topic and date.")
    else:
        df = pd.json_normalize(articles)
        if 'title' in df.columns and 'pubDate' in df.columns:
            df = df[df['title'].notnull()][['title', 'description', 'link', 'pubDate']]
            df['timestamp'] = pd.to_datetime(df['pubDate'])
            df["combined_text"] = df["title"].fillna("") + " " + df["description"].fillna("")
            df["sentiment"] = df["combined_text"].apply(get_sentiment)

            st.subheader("🗞️ Latest News")
            for _, row in df.iterrows():
                st.markdown(f"**{row['title']}**")
                if row['description']:
                    st.write(row['description'])
                st.write(f"📅 {row['timestamp']}")
                st.write(f"[🔗 Read more]({row['link']})")
                st.markdown(f"**Sentiment:** `{row['sentiment']}`")
                st.markdown("---")

            sentiment_counts = df["sentiment"].value_counts()
            colors = ['green', 'red', 'gray']
            fig, ax = plt.subplots()
            sentiment_counts.plot.pie(autopct='%1.1f%%', startangle=140, colors=colors, ax=ax)
            ax.set_ylabel('')
            ax.set_title("Sentiment Distribution")
            st.pyplot(fig)
        else:
            st.error("❌ Required fields not found in the news data.")
