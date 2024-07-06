import streamlit as st
import pandas as pd

# Set the page configuration to use the full width of the screen
st.set_page_config(layout="wide")

# Load the data
df = pd.read_csv('/Users/esser/Downloads/combined_players_updated.csv')

# Drop rows where all elements are NaN
df = df.dropna(how='all')

# Custom CSS for increasing font size and making the text bigger
st.markdown("""
    <style>
    .dataframe {
        font-size: 20px !important;
    }
    .stDataFrame {
        width: 100% !important;
        height: 600px !important;
    }
    .player-info {
        font-size: 24px !important;
        font-weight: bold;
    }
    .info-label {
        font-size: 24px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Streamlit app
st.title("Player Search and Connections")

player_name = st.text_input("Enter player name:")

if player_name:
    matching_players = df[df['FullName'].str.contains(player_name, case=False, na=False)]
    if not matching_players.empty:
        if len(matching_players) > 1:
            st.write("Multiple players found. Please select the player:")
            player_selection = st.selectbox("Select a player:", matching_players['FullName'].unique())
            player_data = matching_players[matching_players['FullName'] == player_selection]
        else:
            player_data = matching_players
        
        if not player_data.empty:
            st.write("Player Information:")
            player_info = player_data.iloc[0]
            st.markdown(f"""
                <div style='display: flex; justify-content: space-between;' class='player-info'>
                    <div><span class='info-label'>Full Name:</span> {player_info['FullName']}</div>
                    <div><span class='info-label'>Nationality:</span> {player_info['Nationality']}</div>
                    <div><span class='info-label'>College:</span> {player_info['College']}</div>
                    <div><span class='info-label'>High School:</span> {player_info['HighSchool']}</div>
                    <div><span class='info-label'>Team:</span> {player_info['Team']}</div>
                    <div><span class='info-label'>Team Location:</span> {player_info['Team_Location']}</div>
                    <div><span class='info-label'>League:</span> {player_info['League']}</div>
                    <div><span class='info-label'>Age:</span> {player_info['Age']}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Get player information
            nationality = player_info['Nationality']
            college = player_info['College']
            high_school = player_info['HighSchool']
            team = player_info['Team']
            team_location = player_info['Team_Location']
            league = player_info['League']
            age = player_info['Age']
            
            with st.expander("Connections"):
                if pd.notna(college) and pd.notna(age):
                    st.write(f"**College with Age Range (±1 year):** {college}")
                    age_range_df = df[(df['College'] == college) & (df['Age'].between(age - 1, age + 1))]
                    st.dataframe(age_range_df, width=1500, height=600)

                if pd.notna(nationality):
                    st.write(f"**Nationality:** {nationality}")
                    st.dataframe(df[df['Nationality'] == nationality], width=1500, height=600)
                
                if pd.notna(college):
                    st.write(f"**College:** {college}")
                    st.dataframe(df[df['College'] == college], width=1500, height=600)
                
                if pd.notna(high_school):
                    st.write(f"**High School:** {high_school}")
                    st.dataframe(df[df['HighSchool'] == high_school], width=1500, height=600)
                
                if pd.notna(team) and pd.notna(league):
                    st.write(f"**Team:** {team} in {league}")
                    st.dataframe(df[(df['Team'] == team) & (df['League'] == league)], width=1500, height=600)
                
                if pd.notna(team_location):
                    st.write(f"**Team Location:** {team_location}")
                    st.dataframe(df[df['Team_Location'] == team_location], width=1500, height=600)
        else:
            st.write("No player found with that name.")
    else:
        st.write("No player found with that name.")
else:
    st.write("Please enter a player name.")
  
