import pandas as pd

    # Define RAPTOR columns to merge
raptor_columns = ['poss', 'mp', 'raptor_box_offense', 'raptor_box_defense', 'raptor_box_total',
                    'raptor_onoff_offense', 'raptor_onoff_defense', 'raptor_onoff_total',
                    'raptor_offense', 'raptor_defense', 'raptor_total', 'war_total',
                    'war_reg_season', 'war_playoffs', 'predator_offense', 'predator_defense',
                    'predator_total', 'pace_impact']

# Function to standardize team names
def standardize_team_names(team_name):
    mapping = {'PHX': 'PHO', 'BKN': 'BRK'}
    return mapping.get(team_name, team_name)

# Function to standardize player names
def standardize_player_names(player_name):
    player_name = player_name.upper().replace('.', '').replace(" JR", "").replace(" SR", "").strip()
    return player_name

# Function to merge RAPTOR data into game data for each player
def merge_player_raptor_data(game_df, raptor_df, player_column, common_players):
    # Calculate the insertion index for new columns
    fp_column = f'{player_column}_FP'
    if fp_column in game_df.columns:
        insert_loc = game_df.columns.get_loc(fp_column) + 1
    else:
        insert_loc = len(game_df.columns)  # If 'FP' column not found, append at the end

    # Initialize a dictionary to hold the new data
    new_data = {f'{player_column}_{col}': pd.Series(index=game_df.index, dtype='float64') for col in raptor_columns}

    # Iterate over each row by index to set the new data
    for idx in game_df.index:
        player_name = game_df.at[idx, player_column]
        team = game_df.at[idx, 'Team']
        season = game_df.at[idx, 'season']

        if player_name in common_players:
            key = (player_name, team, season)
            if key in raptor_df.index:
                player_data = raptor_df.loc[key, :]
                if isinstance(player_data, pd.DataFrame):
                    player_data = player_data.iloc[0]  # Handle potential duplicates

                for col in raptor_columns:
                    new_data[f'{player_column}_{col}'].at[idx] = player_data[col]

    # Create DataFrame from the dictionary
    new_columns_df = pd.DataFrame(new_data)
    
    # Slice the original DataFrame and concatenate the new columns at the correct position
    left = game_df.iloc[:, :insert_loc]
    right = game_df.iloc[:, insert_loc:]
    game_df = pd.concat([left, new_columns_df, right], axis=1)

    return game_df

def main(df):
    # Load datasets
    raptor_df = pd.read_csv('data/modern_RAPTOR_by_team.csv')
    raptor_df = raptor_df[raptor_df['season_type'] == 'RS']
    # game_df = pd.read_csv('data/processed_games_sorted_by_date_with_opponent_stats.csv')
    game_df = df

    print(game_df.columns)
    # Process game_df date and season
    game_df['Date'] = pd.to_datetime(game_df['Date'])
    game_df['season'] = game_df['Date'].dt.year + (game_df['Date'].dt.month > 8)

    # Normalize names and teams in game_df
    player_columns = ['Player_1', 'Player_2', 'Player_3', 'Player_4', 'Player_5', 'Player_6']
    for col in player_columns:
        game_df[col] = game_df[col].apply(standardize_player_names)
    game_df['Team'] = game_df['Team'].apply(standardize_team_names)

    # Set indices for raptor_df and normalize text fields
    raptor_df['player_name'] = raptor_df['player_name'].apply(standardize_player_names)
    raptor_df['team'] = raptor_df['team'].apply(standardize_team_names)
    raptor_df.set_index(['player_name', 'team', 'season'], inplace=True)
    raptor_df.sort_index(inplace=True)  # Sorting the index to avoid performance warnings

    # Get unique players from game_df and raptor_df
    players = game_df[player_columns].stack().unique()
    raptor_players = raptor_df.index.get_level_values('player_name').unique()

    # Find common players between both datasets
    common_players = set(raptor_players).intersection(players)

    # Apply the merge function for each player column
    for player_col in player_columns:
        game_df = merge_player_raptor_data(game_df, raptor_df, player_col, common_players)

    return game_df

    # # Save the merged data to CSV
    # game_df.to_csv('updated_game_data_with_raptor.csv', index=False)
    # print("Data merge completed and file saved.")


if __name__ == "__main__":
    main()