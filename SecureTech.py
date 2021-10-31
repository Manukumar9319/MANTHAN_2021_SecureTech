import pandas as pd
import numpy as np
from textblob import TextBlob
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image
import folium
from wordcloud import WordCloud
import itertools
import snscrape.modules.twitter as sntwitter

st.set_page_config(layout="wide")


def folium_map():
    df = pd.read_csv(
        'res/part1.csv')[['Police Station', 'Latitude', 'Longitude', 'Event Type']]
    dfP1 = df[df['Police Station'] == 'PS1'].reset_index()
    dfP2 = df[df['Police Station'] == 'PS2'].reset_index()
    dfP3 = df[df['Police Station'] == 'PS3'].reset_index()
    dfP4 = df[df['Police Station'] == 'PS4'].reset_index()
    m = folium.Map(location=[df.Latitude.mean(),
                             df.Longitude.mean()], zoom_start=11, control_scale=True)
    group1 = folium.FeatureGroup(
        name='<span style=\\"color: red;\\">PS1 C1 circle (Blue)</span>')
    group2 = folium.FeatureGroup(
        name='<span style=\\"color: blue;\\">PS2 C1 circle (Green)</span>')
    group3 = folium.FeatureGroup(
        name='<span style=\\"color: red;\\">PS3 C2 circle (Red)</span>')
    group4 = folium.FeatureGroup(
        name='<span style=\\"color: blue;\\">PS4 C2 circle (Black)</span>')

    for i, j in enumerate(zip(dfP1.Latitude, dfP1.Longitude)):
        location = [j[0], j[1]]
        folium.CircleMarker(location, radius=1,
                            popup=dfP1['Event Type'][i]).add_to(group1)
    group1.add_to(m)

    for i, j in enumerate(zip(dfP2.Latitude, dfP2.Longitude)):
        location = [j[0], j[1]]
        folium.CircleMarker(
            location, radius=1, popup=dfP2['Event Type'][i], color='green').add_to(group2)
    group2.add_to(m)

    for i, j in enumerate(zip(dfP3.Latitude, dfP3.Longitude)):
        location = [j[0], j[1]]
        folium.CircleMarker(
            location, radius=1, popup=dfP3['Event Type'][i], color='red').add_to(group3)
    group3.add_to(m)

    for i, j in enumerate(zip(dfP4.Latitude, dfP4.Longitude)):
        location = [j[0], j[1]]
        folium.CircleMarker(
            location, radius=1, popup=dfP4['Event Type'][i], color='black').add_to(group4)
    group4.add_to(m)

    folium.map.LayerControl('topright', collapsed=False).add_to(m)
    return folium_static(m)


folium_map()
noTweets = st.slider('No. of tweets', min_value=10, max_value=700, value=200)
with st.spinner('Wait for it...'):
    inputT = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(
        f'near:"Mumbai" within:100km ').get_items(), noTweets))

inputT = inputT[inputT.lang == 'en']

with st.expander("Word Cloud"):
    tw_mask = np.array(Image.open("res/images.jpg").convert('1'))

    def transform_format(val):
        if val == 0:
            return val
        else:
            return 255
    transformed_wine_mask = np.ndarray(
        (tw_mask.shape[0], tw_mask.shape[1]), np.int32)

    for i in range(len(tw_mask)):
        transformed_wine_mask[i] = list(map(transform_format, tw_mask[i]))
    wc = WordCloud(background_color="white", max_words=1000, mask=transformed_wine_mask,
                   width=300, contour_color='firebrick', contour_width=2)

    wc.generate(' '.join(inputT.content.values).replace('https', ''))
    st.image(wc.to_array(), width=370)


def getSentiment(text_list):
    no, positive, neutral, negative = 0, 0, 0, 0
    for j, i in enumerate(text_list):

        score = TextBlob(i).sentiment.polarity
        if score < 0:
            usr_neg.append((j, score))
            negative += 1
        elif score == 0:
            neutral += 1
        else:
            positive += 1
    return positive, neutral, negative


positive, neutral, negative = getSentiment(inputT.content)

usr_neg = []
neg_df = pd.DataFrame(usr_neg, columns=['ind', 'score'])
neg_df.set_index('ind', inplace=True)

final_df = inputT.join(neg_df, how='left').sort_values(
    'score', ascending=True).dropna(subset=['score'])

with st.expander("Sentiment Graph"):
    co1, _ = st.columns(2)
    with co1:
        st.bar_chart(pd.DataFrame([[positive, neutral, negative]], columns=[
                     "POSITIVE", "NEUTRAL", "NEGATIVE"]))

st.warning('This is a warning')
col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 3, 1])
with col1:
    st.subheader("username")
with col2:
    st.subheader("Location")
with col3:
    st.subheader("Date")
with col4:
    st.subheader("ReplyCount")
with col5:
    st.subheader("\tURL")
with col6:
    st.subheader("Profile Pic")


def displayDetails(x):
    with col1:
        st.write(x['user']['username'])
    with col2:
        try:
            st.write(x['user']['location'])
        except:
            st.write('NO location')
    with col3:
        st.write(x['date'])
    with col4:
        st.write(x['replyCount'])
    with col5:
        st.write(x['url'])
    with col6:
        try:
            st.image(x['user']['profileImageUrl'])
        except:
            st.write('NO Image')


final_df.apply(displayDetails, axis=1)
