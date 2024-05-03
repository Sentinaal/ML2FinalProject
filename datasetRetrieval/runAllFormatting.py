
import formatSeason
import formatRaptor
import formatFeatures
import formatOpponents

def run_all():
    season_data = formatSeason.main()
    #display the data
    print(season_data)
    opponent_data = formatOpponents.main(season_data)
    
    raptor_data = formatRaptor.main(opponent_data)
    features_data = formatFeatures.main(raptor_data)
    #save this test df
    features_data.to_csv('finalData/NBA2020.csv', index=False)
    print("All processing complete")

if __name__ == "__main__":
    run_all()
