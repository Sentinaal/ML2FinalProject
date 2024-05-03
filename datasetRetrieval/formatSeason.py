import pandas as pd

# Create a mapping dictionary for team names
team_mapping = {
    'Philadelphia': 'PHI',
    'Boston': 'BOS',
    'LALakers': 'LAL',
    'GoldenState': 'GSW',
    'Washington': 'WAS',
    'Indiana': 'IND',
    'Orlando': 'ORL',
    'Detroit': 'DET',
    'NewYork': 'NYK',
    'Memphis': 'MEM',
    'NewOrleans': 'NOP',
    'Brooklyn': 'BKN',
    'Cleveland': 'CLE',
    'Toronto': 'TOR',
    'Houston': 'HOU',
    'Atlanta': 'ATL',
    'Chicago': 'CHI',
    'Miami': 'MIA',
    'Charlotte': 'CHA',
    'SanAntonio': 'SAS',
    'OklahomaCity': 'OKC',
    'Minnesota': 'MIN',
    'Denver': 'DEN',
    'Utah': 'UTA',
    'Dallas': 'DAL',
    'Phoenix': 'PHX',
    'Sacramento': 'SAC',
    'Milwaukee': 'MIL',
    'Portland': 'POR',
    'LAClippers': 'LAC',
}

# Function to split 'Match Up' into 'Team', 'Opponent', and 'Location'
def split_match_up(match_up):
    if '@' in match_up:
        team, opponent = match_up.split(' @ ')
        location = 'V'
    else:
        team, opponent = match_up.split(' vs. ')
        location = 'H'
    return pd.Series([team, opponent, location])

# Function to assign the appropriate year based on the date in df2
def parse_date(date_int):
    date_str = str(date_int).zfill(4)
    month = int(date_str[:2])
    day = int(date_str[2:])
    if month >= 10:
        year = 2019
    else:
        year = 2020
    return pd.to_datetime(f'{year}-{month}-{day}', format='%Y-%m-%d')

def process_game(game_data):
    # Save the game data to a csv
    #game_data.to_csv('game_data.csv', index=False)
    base_data = game_data.iloc[0][:34]  # Assuming base_data contains game-related info
    new_row = pd.Series(base_data).to_dict()
    
    # Limit the number of players processed to 6
    num_players = min(6, game_data.shape[0])  # Ensure we do not exceed 6 players even if more are available
    
    for i in range(1, num_players + 1):  # Adjust range to iterate only up to 6
        player_prefix = f'Player_{i}_'
        player_name_column = f'Player_{i}'
        row = game_data.iloc[i-1]  # Adjust to 0-indexed, as `i` starts from 1
        new_row[player_name_column] = getattr(row, 'PLAYER', 'Unknown')
        
        player_data = [
            'WL', 'MIN', 'PTS', 'FGM', 'FGA', 'FGP', 
            'ThreePM', 'ThreePA', 'ThreePP', 'FTM', 'FTA', 'FTP', 
            'OREB', 'DREB', 'REB', 'AST', 'STL', 
            'BLK', 'TOV', 'PF', 'PlusMinus', 'FP'
        ]
        
        for col in player_data:
            column_name = player_prefix + col
            if hasattr(row, col):
                new_row[column_name] = getattr(row, col)
    
    return pd.DataFrame([new_row])


def main():
    # Load DataFrames
    df1 = pd.read_csv('data/nba2020_boxscore.csv')
    df2 = pd.read_csv('data/nba2020_odds.csv')
    player_data = pd.read_csv('data/nba2020_player_boxscore.csv')

    # Convert 'Game Date' to datetime format in df1
    df1['Date'] = pd.to_datetime(df1['Game Date'], format='%m/%d/%Y')

    # Split 'Match Up' into separate columns in df1
    df1[['Team', 'Opponent', 'Location']] = df1['Match Up'].apply(split_match_up)

    # Convert 'Date' column in df2 to datetime format with the assigned year
    df2['Date'] = df2['Date'].apply(parse_date)

    # Find the common date range
    df1_first_date = df1['Date'].min()
    df1_last_date = df1['Date'].max()
    df2_first_date = df2['Date'].min()
    df2_last_date = df2['Date'].max()
    common_start_date = max(df1_first_date, df2_first_date)
    common_end_date = min(df1_last_date, df2_last_date)

    print(f'Common date range: {common_start_date} to {common_end_date}')

    # Filter df1 and df2 based on the common date range
    df1 = df1[(df1['Date'] >= common_start_date) & (df1['Date'] <= common_end_date)].copy()
    df2 = df2[(df2['Date'] >= common_start_date) & (df2['Date'] <= common_end_date)].copy()

    #print df1 date and df2 date
    # print(df1['Date'])
    # print(df2['Date'])


    # Map the team names in df2 to match the ones in df1
    df2['Team'] = df2['Team'].map(team_mapping)

    # Merge df1 and df2 based on 'Date' and 'Team'
    df1['Location'] = df1['Location'].map({'V': 'V', 'H': 'H'})

    test_merge = pd.merge(df1[['Date', 'Team']], df2[['Date', 'Team']], on=['Date', 'Team'], how='inner')
    print(test_merge['Date'].nunique())
    merged_df = pd.merge(df1, df2, left_on=['Team', 'Date', 'Location'], right_on=['Team', 'Date', 'VH'])
    print(merged_df)

    # print(df1['Date'].nunique())
    # print(df2['Date'].nunique())
    # print(merged_df['Date'].nunique())


    # Specify the desired column order
    column_order = ['Team', 'Opponent', 'Location', 'Date', 'WL', 'Match Up', 'MIN', 'PTS', 'FGM', 'FGA', 'FGP',
                    'ThreePM', 'ThreePA', 'ThreePP', 'FTM', 'FTA', 'FTP', 'OREB', 'DREB', 'REB', 'AST', 'STL',
                    'BLK', 'TOV', 'PF', 'PlusMinus', '1st', '2nd', '3rd', '4th', 'Final', 'Open', 'Close',
                    'ML', '2H']

    # Reindex the DataFrame with the specified column order
    merged_df = merged_df.reindex(columns=column_order)

    # Convert 'Date' columns to datetime objects for proper merging
    merged_df['Date'] = pd.to_datetime(merged_df['Date'], format='%Y-%m-%d')

    # Load the player data
    player_data['Date'] = pd.to_datetime(player_data['GAME DATE'], format='%m/%d/%Y')
    player_data['Team'] = player_data['TEAM']
    player_data['MIN'] = pd.to_numeric(player_data['MIN'], errors='coerce')

    # Sort by 'Date', 'Team', and 'MIN', then get top 6 players
    player_data_sorted = player_data.sort_values(by=['Date', 'Team', 'MIN'], ascending=[True, True, False])
    top_six_players = player_data_sorted.groupby(['Date', 'Team']).head(6)


    # Merge the DataFrames on 'Date' and 'Team'
    merged_top_players = pd.merge(merged_df, top_six_players, on=['Date', 'Team'], how='inner')

    # Rename columns to distinguish between team and player data
    column_renames = {col: col.replace('_x', '_team') if '_x' in col else col.replace('_y', '') for col in merged_top_players.columns}
    merged_top_players.rename(columns=column_renames, inplace=True)

    # Drop unnecessary columns
    columns_to_drop = ['Match Up', 'GAME DATE', 'MATCH UP', 'TEAM']
    merged_top_players.drop(columns=columns_to_drop, inplace=True)
    #merged_top_players.to_csv('processed_games_sorted_by_date.csv', index=False)


    #print(merged_top_players.head())
    #save to csv

    # Group by each game using team, opponent, and date to ensure unique games are processed together
    grouped = merged_top_players.groupby(['Team', 'Opponent', 'Date'])

    #print(grouped.head())

    # Apply the processing function to each group (each unique game)
    processed_games = grouped.apply(process_game).reset_index(drop=True)

    # Sort the DataFrame by the 'Date' column
    processed_games = processed_games.sort_values(by='Date')

    # # Drop unnecessary columns
    # processed_games = processed_games.drop(columns=['PLAYER'])

    #processed_games.to_csv('processed_games.csv', index=False)

    return processed_games

    # # Save the final DataFrame to CSV
    # processed_games.to_csv('data/processed_games_sorted_by_date.csv', index=False)

    # # Print sample data to verify the output
    # print(processed_games.head())

if __name__ == '__main__':
    main()