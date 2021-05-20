from createdata.scrape_fight_links import get_all_links
from createdata.scrape_fight_data import create_fight_data_csv
from createdata.scrape_fighter_details import create_fighter_data_csv
import pickle
import os
from pathlib import Path

EVENT_AND_FIGHT_LINKS_PATH = Path(os.getcwd())/'../data/event_and_fight_links.pickle'
event_and_fight_links = pickle.load( open(EVENT_AND_FIGHT_LINKS_PATH.as_posix(),"rb") )
new_event_and_fight_links = get_all_links()
create_fight_data_csv(event_and_fight_links)
create_fighter_data_csv()
