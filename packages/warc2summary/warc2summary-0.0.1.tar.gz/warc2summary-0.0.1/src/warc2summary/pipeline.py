#takes in a dataframe from warc processor and transforms it into a dataframe that can be used for the api_calls
#contains fields: filename, web_text_content, title_tag, url, api_content(which is sent into api)

import pandas as pd
import openai
from openai import OpenAI
import json
import pandas as pd
import re
from tqdm import tqdm
import instructor
from pydantic import BaseModel
from urllib.parse import urlparse
from tldextract import extract

#check the column names are inside the dataframe
def check_columns(df,columns):
    return all([col in df.columns for col in columns])

def dropnull(df,subset):
    return df.dropna(subset=subset)

def transform_warc(df, heuristic):
    #drop rows with null values in web_text_content and url and filename
    important_identifier = ['web_text_content','url','filename']
    #remove rows with null values in the important_identifier
    df = df.dropna(subset=important_identifier)
    df = heuristic(df)
    df.rename(columns={'title':'title_tag'},inplace=True)
    return df

#takes a api call and returns the content of the api call
#zero shot version to obtain abstract and title
#assume OPEN_AI_API_KEY is set in a .env file
def batch_prompt(df, prompt ,max_tokens=150,temperature=0.5,top_p=0.95,frequency_penalty=0.0,presence_penalty=0.0,model="gpt-4o",debug=False):
    class title_abstract(BaseModel):
        title: str
        abstract: str
        # Patch the OpenAI client
    client = instructor.from_openai(OpenAI())
    titles = []
    abstracts = []

    # Iterate through each row in the dataframe
    for index, row in tqdm(df.iterrows(), total=len(df)):
        content = row['api_content']    
        response = client.chat.completions.create(
            model=model,
            response_format={ "type": "json_object" },
            response_model=title_abstract,
            messages=[
                {"role": 'system', "content": prompt},
                {"role": 'user', "content": content}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        
        print(response)     
        #assume pydantic does job properly
        #convert string to  object
        title = response.title
        abstract = response.abstract    
        titles.append(title)
        abstracts.append(abstract)
    # Add the generated titles and abstracts to the dataframe
    df['gen_title'] = titles
    df['gen_abstract'] = abstracts
    #copy a copy of df into memory then return a trimed dataframe if debug is True
    if debug:
        df_copy = df.copy()
        return df_copy
    #trim the dataframe
    df = df[['filename', 'url', 'api_content', 'gen_title', 'gen_abstract']]
    return df

def get_domain(x):
        if '|' in x:
            x = x.split('|')[0]
        #we strip the url of the query parameters to its based registered domain
        domain = urlparse(x).netloc
        domain = extract(domain)
        domain = domain.registered_domain
        return domain
#prep human data for merging
#df contains the human generated data as in the open data
def prep_human_data(df):
    #drop rows with null values in web_text_content and url and filename
    important_identifier = ['is_version_of','title','abstract']
    #check if the columns are in the dataframe
    if df.columns.isin(important_identifier).any():
        #remove rows with null values in the important_identifier
        df = df.dropna(subset=important_identifier)
        #the the base url
        df['url'] = df['is_version_of'].apply(get_domain)
        df.rename(columns={'title':'human_title','abstract':'human_abstract'})
        return df
    else:
        raise ValueError('Columns not in dataframe')

#merge the human generated data with the api generated data
def merge(df_api, df_human):
    #merge the two dataframes
    #we use the url to merge the two dataframes
    #we use the url col as a merge key
    # copy url col in df_api to maintain the original url

    df_api['ori_url'] = df_api['url']
    df_api['url'] = df_api['url'].apply(get_domain)
    #do a merge on the url
    df= pd.merge(df_api,df_human,how='left',on='url')
    # Function to get the shortest URL from a list of URLs
    df.dropna(subset=['is_version_of'],inplace=True)
    def get_shortest_url(urls):
        return min(urls, key=len)

    # Split the 'is_version_of' column by '|' and apply the get_shortest_url function to each row
    #print(df['is_version_of'].str.split('|'))
    df['shortest_url'] = df['is_version_of'].str.split('|').apply(get_shortest_url)

    # Group the DataFrame by 'url', sort within each group, and keep the first row
    result = (df.sort_values(['url', 'shortest_url'])
                .groupby('url', sort=False)
                .apply(lambda group: group.loc[group['shortest_url'] == group['shortest_url'].min(), :])
                .reset_index(drop=True))
    #rename title and abstract from human df to human_title and human_abstract
    result.rename(columns={'title':'human_title','abstract':'human_abstract'},inplace=True)
    # retain only the necessary columns
    result = result[['filename', 'ori_url', 'api_content', 'gen_title', 'gen_abstract', 'human_title', 'human_abstract']]
    return result
#we need to clean the data human to ensure that the data does not contains nulls
#merge with the human generated data


def execute_pipeline(warc_df,human_df,prompt,heuristic,max_tokens=1000,temperature=0.5,top_p=0.95,frequency_penalty=0.0,presence_penalty=0.0,model="gpt-4o",debug=False):
    #check if the columns are in the dataframe
    if not check_columns(warc_df,['web_text_content','url','filename']):
        raise ValueError('Columns not in dataframe')
    #transform the dataframe
    warc_df = transform_warc(warc_df,heuristic)
    #batch prompt
    warc_df = batch_prompt(warc_df,prompt)
    #prep human data
    human_df = prep_human_data(human_df)
    #merge the data
    merged_df = merge(warc_df,human_df)
    return merged_df
    
