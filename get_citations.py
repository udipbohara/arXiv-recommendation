import time 
import pandas as pd 
import requests
import pickle 
from datetime import datetime 
import json 

#papers > 2018
df = pd.read_csv('selected_papers.csv')
to_check = set(df.id.to_list())
prefix='arXiv:'

size_batches = 1000
batches = [df[i:i+size_batches] for i in range(0,df.shape[0],size_batches)]
batch = 0

papers_checked = []

for dfs in batches: 
    main = {}
    papers = list(set(dfs.id.to_list()))
    for paper in papers:
        if paper in main.keys() or paper in papers_checked:
            continue
        papers_checked.append(paper)
        p_id = paper
        response = requests.get(f'https://api.semanticscholar.org/v1/paper/{prefix}{p_id}').json()

        if 'error' in response:
            continue
        if 'Forbidden' in response.values():
            print(datetime.now())
            print('Total papers checked: ', len(papers_checked))
            print('Total found: ', len(main))
            print('Rate Limit Reached: Sleeping for 5 Minutes')
            print('===========================')
            time.sleep(61*5)
            print("---------")
            print('resumed')
            print("---------")
            p_id = paper
            response = requests.get(f'https://api.semanticscholar.org/v1/paper/{prefix}{p_id}').json()
            if 'error' in response:
                continue
            if 'Forbidden' in response.values():
                print('Trying again...')
                print('=====')
                time.sleep(60*2)
                continue
        
        try:
            references = [r['arxivId']  for r in response['references']]
        except KeyError:
            continue

        citations = [c['arxivId'] for c in response['citations']]
        retrieved_citations = set([i for i in references + citations if i])
        found = list(to_check.intersection(retrieved_citations))
        if found != []:
            #print(f'Found {len(found)} papezs for : {p_id}')
            main[p_id] = found
            

    pickle.dump(main, open( f"/Users/udipbohara/Desktop/recommendation_engine/citations/main_dict{batch}.pkl", "wb" ) )
    print('Checked all papers! Wrote File to disk.')

    df = pd.DataFrame([(Source,Target ) for Source,j in main.items() for Target in j], 
                    columns=['Source','Target'])


    df.to_csv(f'/Users/udipbohara/Desktop/recommendation_engine/citations/citations_batch{batch}.csv', index=False)

    print(f'Complete! Wrote batch {batch} of {len(batches)} file')
    batch+=1 

