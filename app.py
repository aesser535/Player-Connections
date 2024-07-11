import streamlit as st
import pandas as pd
import re

# Set the page configuration to use the full width of the screen
st.set_page_config(layout="wide")

# Load the DataFrames
df_combined = pd.read_csv('combined_players_updated.csv')
df_nfl = pd.read_csv('nfl_players_sorted_2019_2023.csv')

# Drop rows where all elements are NaN
df_combined = df_combined.dropna(how='all')

# Function to standardize names
def standardize_name(name):
    if pd.isna(name):
        return ''
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower().strip()

# Apply the function to create standardized names in both DataFrames
df_combined['standard_name'] = df_combined['FullName'].apply(standardize_name)
df_nfl['standard_name'] = df_nfl['name'].apply(standardize_name)

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

# Define the function to get teammates for NFL data
def get_teammates(player_name, df_nfl):
    # Filter the DataFrame to get the specific player
    player_df = df_nfl[df_nfl['standard_name'] == player_name]
    
    if player_df.empty:
        return pd.DataFrame()  # Return an empty DataFrame if no data found
    
    # Get the teams and seasons the player was part of
    player_teams_seasons = player_df[['team', 'season']]

    # Find all players who shared the same team and season
    teammates = df_nfl.merge(player_teams_seasons, on=['team', 'season'])
    
    # Filter out the specified player from the teammates list
    teammates = teammates[teammates['standard_name'] != player_name]
    
    # Calculate the duration (in seasons) each teammate played with the specified player
    teammates_duration = teammates.groupby('name').agg({'season': 'nunique', 'team': 'first'}).reset_index()
    teammates_duration.rename(columns={'season': 'seasons_played_together'}, inplace=True)

    # Sort by seasons_played_together in descending order
    teammates_duration = teammates_duration.sort_values(by='seasons_played_together', ascending=False)

    return teammates_duration

# Streamlit app
st.title("Player Search and Connections")

player_name = st.text_input("Enter player name:")

if player_name:
    standardized_name = standardize_name(player_name)
    matching_players = df_combined[df_combined['standard_name'].str.contains(standardized_name, case=False, na=False)]
    
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
                    age_range_df = df_combined[(df_combined['College'] == college) & (df_combined['Age'].between(age - 1, age + 1))]
                    st.dataframe(age_range_df, width=1500, height=600)

                if pd.notna(nationality):
                    st.write(f"**Nationality:** {nationality}")
                    st.dataframe(df_combined[df_combined['Nationality'] == nationality], width=1500, height=600)
                
                if pd.notna(college):
                    st.write(f"**College:** {college}")
                    st.dataframe(df_combined[df_combined['College'] == college], width=1500, height=600)
                
                if pd.notna(high_school):
                    st.write(f"**High School:** {high_school}")
                    st.dataframe(df_combined[df_combined['HighSchool'] == high_school], width=1500, height=600)
                
                if pd.notna(team) and pd.notna(league):
                    st.write(f"**Team:** {team} in {league}")
                    st.dataframe(df_combined[(df_combined['Team'] == team) & (df_combined['League'] == league)], width=1500, height=600)
                
                if pd.notna(team_location):
                    st.write(f"**Team Location:** {team_location}")
                    st.dataframe(df_combined[df_combined['Team_Location'] == team_location], width=1500, height=600)
                
                # Add NFL teammates information if the player is in the NFL
                if league == 'NFL':
                    st.write(f"**NFL Teammates:**")
                    teammates = get_teammates(standardized_name, df_nfl)
                    if not teammates.empty:
                        st.dataframe(teammates, width=1500, height=600)
                    else:
                        st.write(f"No teammates data found for player: {player_name}")
        else:
            st.write("No player found with that name.")
    else:
        st.write("No player found with that name.")
else:
    st.write("Please enter a player name.")

