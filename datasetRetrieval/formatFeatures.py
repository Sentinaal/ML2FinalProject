import pandas as pd


def calculate_uPER(row, league_stats, player_num):
    # Dynamically construct column names based on player number
    min_col = f'Player_{player_num}_MIN'
    three_p_col = f'Player_{player_num}_ThreePM'
    ast_col = f'Player_{player_num}_AST'
    fg_col = f'Player_{player_num}_FGM'
    fga_col = f'Player_{player_num}_FGA'
    ft_col = f'Player_{player_num}_FTM'
    fta_col = f'Player_{player_num}_FTA'
    tov_col = f'Player_{player_num}_TOV'
    orb_col = f'Player_{player_num}_OREB'
    reb_col = f'Player_{player_num}_REB'
    stl_col = f'Player_{player_num}_STL'
    blk_col = f'Player_{player_num}_BLK'
    pf_col = f'Player_{player_num}_PF'
    team_ast_col = 'AST_team'  # Ensure this column exists or is calculated
    team_fg_col = 'FGM_team'  # Ensure this column exists or is calculated
    
    # Constants from the league statistics
    factor = (2 / 3) - (0.5 * (league_stats['AST'] / league_stats['FG'])) / (2 * (league_stats['FG'] / league_stats['FT']))
    VOP = league_stats['PTS'] / (league_stats['FGA'] - league_stats['ORB'] + league_stats['TOV'] + 0.44 * league_stats['FTA'])
    DRB_pct = (league_stats['TRB'] - league_stats['ORB']) / league_stats['TRB']

    # Unadjusted PER calculation using dynamic column references
    uPER = (1 / row[min_col]) * (
        row[three_p_col] +
        (2/3) * row[ast_col] +
        (2 - factor * (row[team_ast_col] / row[team_fg_col])) * row[fg_col] +
        (row[ft_col] * 0.5 * (1 + (1 - (row[team_ast_col] / row[team_fg_col])) + (2/3) * (row[team_ast_col] / row[team_fg_col]))) -
        VOP * row[tov_col] -
        VOP * DRB_pct * (row[fga_col] - row[fg_col]) -
        VOP * 0.44 * (0.44 + (0.56 * DRB_pct)) * (row[fta_col] - row[ft_col]) +
        VOP * (1 - DRB_pct) * (row[reb_col] - row[orb_col]) +
        VOP * DRB_pct * row[orb_col] +
        VOP * row[stl_col] +
        VOP * DRB_pct * row[blk_col] -
        row[pf_col] * ((league_stats['FT'] / league_stats['PF']) - 0.44 * (league_stats['FTA'] / league_stats['PF']) * VOP)
    )
    return uPER

# Ensure data is numeric and replace non-numeric values with zero
def safe_numeric_conversion(df, cols):
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col].fillna(0, inplace=True)

def calculate_ratings(df):
        # Calculate possessions for Team and Opponent
        df['Poss_team'] = df['FGA_team'] - df['OREB_team'] + df['TOV_team'] + 0.44 * df['FTA_team']
        df['Poss_opponent'] = df['FGA_opponent'] - df['OREB_opponent'] + df['TOV_opponent'] + 0.44 * df['FTA_opponent']
        
        # Calculate Offensive and Defensive Ratings
        df['ORtg_team'] = 100 * (df['PTS_team'] / df['Poss_team'])
        df['DRtg_team'] = 100 * (df['PTS_opponent'] / df['Poss_team'])
        df['ORtg_opponent'] = 100 * (df['PTS_opponent'] / df['Poss_opponent'])
        df['DRtg_opponent'] = 100 * (df['PTS_team'] / df['Poss_opponent'])
        
        # Calculate Net Ratings
        df['NetRtg_team'] = df['ORtg_team'] - df['DRtg_team']
        df['NetRtg_opponent'] = df['ORtg_opponent'] - df['DRtg_opponent']

        # Insert columns after 'PlusMinus_team' and 'PlusMinus_opponent'
        # Insert Team Ratings
        plus_minus_team_index = df.columns.get_loc('PlusMinus_team') + 1
        for col in ['ORtg_team', 'DRtg_team', 'NetRtg_team', 'Poss_team']:
            df.insert(plus_minus_team_index, col, df.pop(col))
            plus_minus_team_index += 1

        # Insert Opponent Ratings
        plus_minus_opp_index = df.columns.get_loc('PlusMinus_opponent') + 1
        for col in ['ORtg_opponent', 'DRtg_opponent', 'NetRtg_opponent', 'Poss_opponent']:
            df.insert(plus_minus_opp_index, col, df.pop(col))
            plus_minus_opp_index += 1



def main(df):
    # Load your datasets
    # player_df = pd.read_csv('updated_game_data_with_raptor.csv')
    league_df = pd.read_csv('data/league_averages.csv')
    player_df = df

    # Adjust the 'Season' format in league_df to just the year (e.g., '2023' from '2022-2023')
    league_df['season'] = league_df['Season'].apply(lambda x: int(x.split('-')[1]))
    #add the 20 in front of the season
    league_df['season'] = league_df['season'] + 2000
    league_df.set_index('season', inplace=True)



    # Applying the function
    for i in range(1, 7):
        player_column = f'Player_{i}_'
        player_df[f'{player_column}uPER'] = player_df.apply(
            lambda row: calculate_uPER(row, league_df.loc[row['season']], i),
            axis=1
        )
        
        # Find the index of the FP column for this player and insert uPER column right after it
        fp_column_index = player_df.columns.get_loc(f'{player_column}FP')
        # Ensure the uPER column follows the FP column
        cols = list(player_df.columns)
        uPER_col_index = cols.index(f'{player_column}uPER')
        cols.insert(fp_column_index + 1, cols.pop(uPER_col_index))
        player_df = player_df[cols]


    # Assuming 'player_df' is your main DataFrame containing team game stats
    calculate_ratings(player_df)

    # Define player, team, and opponent stats
    player_stats = [f'Player_{i}_{stat}' for i in range(1, 7) for stat in ['PTS', 'AST', 'REB', 'TOV', 'ThreePP', 'FGP', 'FTP', 'uPER', 'FP', 'MIN', 'raptor_offense', 'raptor_defense', 'raptor_total']]
    team_stats = ['PTS_team', 'AST_team', 'REB_team', 'TOV_team', 'FGP_team', 'ThreePP_team', 'FTP_team', 'ORtg_team', 'DRtg_team', 'NetRtg_team']
    opponent_stats = ['PTS_opponent', 'AST_opponent', 'REB_opponent', 'TOV_opponent', 'FGP_opponent', 'ThreePP_opponent', 'FTP_opponent', 'ORtg_opponent', 'DRtg_opponent', 'NetRtg_opponent']

    safe_numeric_conversion(player_df, player_stats + team_stats + opponent_stats)

    # Calculate rolling averages and insert them next to each stat
    window_size = 3
    for stat in team_stats + opponent_stats:
        rolling_col_name = f'{stat}_rolling_avg'
        group_col = 'Team' if 'team' in stat else 'Opponent'
        player_df[rolling_col_name] = player_df.groupby(group_col)[stat].transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())

        # Insert rolling average column next to the original stat
        stat_index = player_df.columns.get_loc(stat)
        player_df.insert(stat_index + 1, rolling_col_name, player_df.pop(rolling_col_name))

    # Special handling for players to ensure correct grouping
    for i in range(1, 7):
        for stat in ['PTS', 'AST', 'REB', 'TOV', 'ThreePP', 'FGP', 'FTP', 'uPER', 'FP', 'MIN', 'raptor_offense', 'raptor_defense', 'raptor_total']:
            col = f'Player_{i}_{stat}'
            rolling_col = f'{col}_rolling_avg'
            group_col = f'Player_{i}'
            if col in player_df.columns and group_col in player_df.columns:
                player_df[rolling_col] = player_df.groupby(group_col)[col].transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
                # Insert rolling average column next to the original stat
                col_index = player_df.columns.get_loc(col)
                player_df.insert(col_index + 1, rolling_col, player_df.pop(rolling_col))

    return player_df

    # # Save the updated DataFrame
    # player_df.to_csv('updated_game_data_with_features.csv', index=False)
    # print("Updated DataFrame with features saved successfully.")

if __name__ == '__main__':
    main()