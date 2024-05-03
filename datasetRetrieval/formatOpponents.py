import pandas as pd

def main(df):
    #get the data
    data = df
    
    # # Load the dataset
    # file_path = 'data/processed_games_sorted_by_date.csv'
    # data = pd.read_csv(file_path)

    # Creating a dictionary to map each team's stats on a given date to their opponent
    team_stats_columns = [col for col in data.columns if '_team' in col and col != 'MIN_team']  # Exclude 'MIN_team' as it's the same for both teams
    opponent_stats_mapping = {col: col.replace('_team', '_opponent') for col in team_stats_columns}

    # For each game, find the opponent and copy their stats
    for idx, row in data.iterrows():
        # Find the opponent row on the same date
        opponent_row = data[(data['Team'] == row['Opponent']) & (data['Date'] == row['Date'])]
        if not opponent_row.empty:
            # Copy the stats from opponent row to the current row
            for team_stat, opponent_stat in opponent_stats_mapping.items():
                data.loc[idx, opponent_stat] = opponent_row[team_stat].values[0]

    # Display the updated dataframe to verify changes
    data.head()

    return data

    # # Save the updated dataframe to a new CSV file
    # data.to_csv('data/processed_games_sorted_by_date_with_opponent_stats.csv', index=False)


if __name__ == '__main__':
    main()