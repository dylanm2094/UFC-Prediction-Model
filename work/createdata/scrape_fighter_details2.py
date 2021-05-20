import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlopen
import requests
from pathlib import Path
import os
from createdata.print_progress import print_progress
from createdata.make_soup import make_soup
from typing import List, Dict, Tuple

HEADER = ['Height', 'Weight', 'Reach', 'Stance', 'DOB']
BASE_PATH = Path(os.getcwd())/'../data'
CSV_PATH = BASE_PATH/'fighter_details_new.csv'

def get_fight_links(event_links: List[str]) -> Dict[str, List[str]]:
	if isinstance(event_links, list):
		return get_event_and_fight_links(event_links)
	else:
		return get_event_and_fight_links(list[event_links])

def get_event_and_fight_links(event_links: List[str]) -> Dict[str, List[str]]:
	event_and_fight_links = {}
	for link in event_links:
		event_fights = []
		soup = make_soup(link)
		for row in soup.findAll('tr', {'class': 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'}):
			href = row.get('data-link')
			event_fights.append(href)
		event_and_fight_links[link] = event_fights
	return event_and_fight_links

def get_fight(event_and_fight_links: Dict[str, List[str]]) -> str:
	dicts = []
	links_dict = {}

	l = len(event_and_fight_links)
	print('Scraping all fight data: ')
	print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')

	for index, (event,fights) in enumerate(event_and_fight_links.items()):
		
		for fight in fights:
			fight_soup = make_soup(fight)
			fight_details = get_fighter_name_and_link(fight_soup)
			dicts.append(fight_details)

	for d in dicts:
		for k, v in d.items():
			links_dict.setdefault(k,[]).append(v)
			links_dict[k] = links_dict[k][0]	

	print(links_dict)
	print_progress(index + 1, l, prefix = 'Progress:', suffix = 'Complete')

	return links_dict

def get_fighter_name_and_link(fight_soup: BeautifulSoup) -> str:
	fighter_name_and_link = {} 
	fighter_name = ''

	for a in fight_soup.findAll('a', {'style':'color:#B10101'},href=True):
		fighter_name = a.text
		fighter_name_and_link[fighter_name] = a['href']
		fighter_name = ''
	return fighter_name_and_link

def get_fighter_name_and_details(links_dict: Dict[str, List[str]]) -> Dict[str, List[str]]:
	fighter_name_and_details = {}

	l = len(links_dict)
	print('Scraping all fighter data: ')
	print_progress(0, l, prefix = 'Progress:', suffix = 'Complete')

	for index, (fighter_name, fighter_url) in enumerate(links_dict.items()):
	    another_soup = make_soup(fighter_url)
	    divs = another_soup.findAll('li', {'class':"b-list__box-list-item b-list__box-list-item_type_block"})
	    data = []
	    for i, div in enumerate(divs):
	        if i == 5:
	            break
	        data.append(div.text.replace('  ', '').replace('\n', '').replace('Height:', '').replace('Weight:', '')\
	                   .replace('Reach:', '').replace('STANCE:', '').replace('DOB:', ''))
	    
	    fighter_name_and_details[fighter_name] = data
	    print_progress(index + 1, l, prefix = 'Progress:', suffix = 'Complete')

	return fighter_name_and_details

def create_fighter_data_csv(event_link) -> None:
	fighter_group_urls = get_fight_links(event_link)
	fighter_name_and_details = get_fighter_name_and_details(get_fight(fighter_group_urls))
	
	df = pd.DataFrame(fighter_name_and_details).T.replace('--', value=np.NaN).replace('', value=np.NaN)
	df.columns = HEADER
	df.to_csv(CSV_PATH.as_posix(), index_label = 'fighter_name')