import pandas as pd
import os
import wget
import numpy as np
from tqdm import tqdm

file = './data/voting_data/2016-precinct-president.csv'

df = pd.read_csv(file, encoding='latin1')

url = "https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt"
if os.path.exists('./data/fips.txt'):
    os.remove('./data/fips.txt')
wget.download(url, out='./data')


with open('./data/fips.txt') as f:
    state_file = f.readlines()[16:67]
with open('./data/fips.txt') as f:
    county_file = f.readlines()[72:3267]

state_dict = {}
for txt in state_file:
    data = txt.split()
    if len(data) == 2:
        state_dict[data[0]] = data[1].lower().capitalize()
    elif len(data) == 3:
        state_dict[data[0]] = data[1].lower().capitalize() + ' ' + data[2].lower().capitalize()
    elif len(data) == 4:
        state_dict[data[0]] = data[1].lower().capitalize() + ' ' + data[2].lower().capitalize() + ' ' + data[3].lower().capitalize()
    else:
        raise Exception('state name length invalid: {}'.format(data))

county_dict = {}
for txt in county_file:
    data = txt.split()
    county_dict[data[0]] = data[1]

state_county_dict = {}
for state_key in state_dict.keys():
    temp_dict = {}
    for key, value in county_dict.items():
        if int(key) > int(state_key)*1000 and int(key) < (int(state_key)+1)*1000:
            temp_dict[key] = value
    state_county_dict[state_key] = temp_dict

county_fips_list = []

for state in state_county_dict.keys():
    county_fips_list = county_fips_list + list(state_county_dict[state].keys())


state_list = []
county_list = []
fips_list = []
total_vote_list = []
lib_vote_list = []
lib_rate_list = []


for county_fips in tqdm(county_fips_list):
    try:
        state = state_dict[county_fips[:2]]
        county = county_dict[county_fips]
        fips = float(county_fips)

        county_df = df.loc[df['county_fips'] == fips] 
        total_vote = np.sum(county_df['votes'].to_numpy())
        lib_vote = np.sum(county_df.loc[county_df['candidate'] == 'Gary Johnson']['votes'].to_numpy())
        
        lib_rate = float(lib_vote) / float(total_vote)

        state_list.append(state)
        county_list.append(county)
        fips_list.append(county_fips)
        total_vote_list.append(total_vote)
        lib_vote_list.append(lib_vote)
        lib_rate_list.append(lib_rate)

    except:
        continue


new_df = {}

new_df['county fips'] = fips_list
new_df['state'] = state_list
new_df['county'] = county_list
new_df['total votes'] = total_vote_list
new_df['vote for libertarian'] = lib_vote_list
new_df['vote for libertarian rate'] = lib_rate_list


new_df = pd.DataFrame(data=new_df)

new_df.to_csv(f"./data/voting_data/vote_lib_data.csv", index=False)
