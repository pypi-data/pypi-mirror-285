import pandas as pd
from collections import *
from urllib.parse import urlparse
from  tldextract import extract
import re
def heuristics_1(df):
    """
    Heuristic 1 : For every file, we look for an about page if it exists, else we use the main page (shortest url).
    Processes a DataFrame to add URL length, sort by filename and URL length, and split into 'about' and 'non-about' DataFrames.

    Parameters:
    df (pd.DataFrame): The input DataFrame with columns 'filename', 'url', 'title', 'web_text_content'.

    Returns:
    pd.DataFrame: The processed DataFrame.
    """
    # Add a column for URL length
    df['url length'] = df['url'].str.len()

    # Sort the DataFrame by filename and URL length
    df.sort_values(['filename', 'url length'], inplace=True)

    # Split DataFrame into 'about' and 'non-about' DataFrames
    about = df[df['url'].str.contains('about', na=False, case=False)].drop_duplicates('filename')
    non_about = df[~df['filename'].isin(about['filename'])].drop_duplicates('filename')

    # Combine the two DataFrames
    final_data = pd.concat([about, non_about]).reset_index(drop=True)
    #new column to be fed into the api
    final_data['api_content'] = final_data['web_text_content']
    #clean up
    final_data.drop('url length', axis=1, inplace=True)
    #drop duplicates in the final data
    final_data.drop_duplicates('filename', inplace=True)
    return final_data
def get_registered_domain(url):
    """Extract the registered domain from a URL."""
    parsed_url = urlparse(url)
    domain = extract(parsed_url.netloc).registered_domain
    return domain
def heuristics_2(df):
    """
    Heuristic 2: For every file, obtain the base page by taking the shortest URL of all the webpages in the warc file,
    then append the URL (root domain name) to the end of the web content separated by '||' to get the full URL.

    Parameters:
    df (pd.DataFrame): The input DataFrame with columns 'filename', 'url', 'title', 'web_text_content'.

    Returns:
    pd.DataFrame: The processed DataFrame with new column 'api_content' containing the new data to be fed into the API.
    """
    # Extract domains for all URLs
    df['domain'] = df['url'].apply(get_registered_domain)

    # Group by filename
    grouped = df.groupby('filename')

    # Function to get row with shortest URL
    def get_shortest_url_row(group):
        return group.loc[group['url'].str.len().idxmin()]

    # Apply function to each group
    shortest_urls = grouped.apply(get_shortest_url_row)

    # Reset index to flatten the DataFrame
    shortest_urls = shortest_urls.reset_index(drop=True)

    # Create api_content column
    shortest_urls['api_content'] = shortest_urls['web_text_content'] + ' || ' + shortest_urls['domain']

    # Select and return relevant columns
    result = shortest_urls[['filename', 'title', 'web_text_content','url','api_content']]
    
    return result
def heuristics_3(df):
    """
    Heuristic 3 : Building on Heuristic 2, we obtain the base page by taking the shortest url of all the webpages in the warc file,
    we then pass the webcontent into our regrex function before appending the url(root domain name) to the end of the webcontent seperated by || to get the full url.

    Parameters:
    df (pd.DataFrame): The input DataFrame with columns 'filename', 'url', 'title', 'web_text_content'.

    Returns:
    pd.DataFrame: The processed DataFrame with new column 'api_content containing the new_data to be fed into the api'.
    TODO:
    Investigate the runtime for the extracting the base url for each file, and see if it can be optimized.
    """
    def preprocess_text(text):
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+', '', text)
        text = re.sub(r'http?://\S+', '', text)
        
        # Remove punctuation (except apostrophes for contractions)
        text = re.sub(r'[^\w\s\'.]', '', text)

        return text
    # Function to clean text using regex patterns
    def clean_text(text):
        # General boilerplate patterns
        boilerplate_patterns = [
            # Navigation and menu sections
            r'(?:home|about|servic|product|resourc|contact|faq|blog|galleri|portfolio|team|news)\s*(?:us)?\s*(?:\||•|\n)',
            r'(?:navig|menu|site\s*map)\s*(?:\||•|\n)',
            
            # Footer sections
            r'(?:useful|quick|popular)\s+link.*?(?=\n\n|\Z)',
            r'(?:contact|connect|find)\s+us.*?(?=\n\n|\Z)',
            r'(?:address|locat).*?(?:\d{5,}|\w+,\s*\w{2,})',
            r'(?:phone|tel|mobil).*?(?:\+\d{1,4}\s*)?\d{3,}[-\s]?\d{3,}[-\s]?\d{3,4}',
            r'(?:email|e-mail).*?\S+@\S+\.\S+',
            r'(?:follow|join|connect\s*with)\s+us\s+on.*?(?:facebook|twitter|linkedin|instagram)',
            
            # Copyright and legal
            r'copyright.*?(?:all|no)\s+right\s+reserv',
            r'(?:privaci|term|cooki)\s+(?:polici|of\s+(?:use|servic))',
            r'(?:power|design)\s+by.*?(?=\n|\Z)',

            r'copyright.*?(?:all|no)\s+right\s+reserv',  # Updated to match the specific pattern
            r'(?:privaci|term|cooki)\s+(?:polici|of\s+(?:use|servic))',
            r'(?:power|design)\s+by.*?(?=\n|\Z)',
            
            # Company info
            r'compani\s+(?:name|registr|number).*?(?:\d{6,}\w?|\w+\s+llc|inc|ltd)',
            
            # Operating hours
            r'(?:hour|open).*?(?:mon|tue|wed|thu|fri|sat|sun).*?(?:close|open).*?(?:holiday|weekend)',
            
            # Call to action
            r'(?:book|schedul|make)\s+(?:an\s+)?(?:appoint|consult).*?(?:\d{3,}[-\s]\d{3,}[-\s]\d{3,4}|\Z)',
            r'(?:sign|subscrib)\s+(?:up|now)\s+for.*?(?:newslett|updat)',
            r'(?:follow|like|share)\s+(?:us|thi)\s+on\s+(?:facebook|twitter|linkedin|instagram)'
            # html
            r'<script\s+type=\'text/javascript\'>.*',  # Remove everything after '<script type='text/javascript'>'
            r'<blockquote\s+class="wp-embedded-content">.*',  # Remove everything after '<blockquote class="wp-embedded-content">'
            r'<!--.*?-->.*',  # Matches HTML comments
            r'</script.*?>.*',  # Matches script tags and their contents
            r'<iframe.*?>.*'  # Matches iframe tags and their contents
        ]
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)

        # Remove unwanted patterns
        unwanted_patterns = [
            r'IMG\d+.*',  # Remove 'IMG_' followed by digits
            r'better-\d+-\d+[×x]\d+',  # Pattern for 'better-4-300×200'
            r'©\s*copyright\s*\d{4}.*?(?:all|no)\s+rights?\s+reserved.*?(?=\n|\Z)',  # Pattern for copyright
            r'photostream',  # Remove 'Photostream'
            r'\d{1,2}\s+[a-z]{3}\s+\d{2}',  # Pattern for '06 FEB 19'
            r'^top$',  # Remove 'Top' at the end of the text
            # Remove sequences of digits longer than 1 characters,preserve for the listed content
            r'\b\d{2,}\b'
            
            r'0 Comments',
            r'WordPress Embed',
            r'HTML Embed',
            r'Copy and paste this.*',
            
            
            r'nothing\s*found\s*for',
            r'search_term_string',
            r'back\s*back',
            r'sampl\s*text\s*\d+\s*:',
            r'read\s+more\s*»',
            r'«\s*previou\s+post',
            r'next\s+post\s*»',
            r'share\s+thi\s+post',
            r'tag:.*?(?=\n|\Z)',
            r'categori:.*?(?=\n|\Z)'
            
            
        ]
        for pattern in unwanted_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Remove duplicate lines
        lines = text.split('\n')
        unique_lines = []
        for line in lines:
            if line.strip() and line.strip() not in unique_lines:
                unique_lines.append(line.strip())
        text = '\n'.join(unique_lines)
        
        # Extract main content
        main_content_patterns = [
            # Look for sections with headings and paragraphs
            r'(?:<h[1-6]>|\n\n)[^<>\n]{10,}(?:</h[1-6]>|\n\n)(?:<p>|\n\n)[^<>\n]{50,}(?:</p>|\n\n)',
            # Look for numbered or bulleted lists
            r'(?:\d+\.|•|\*)\s+[A-Z][^.!?]{10,}[.!?](?:\s+(?:\d+\.|•|\*)\s+[A-Z][^.!?]{10,}[.!?]){2,}',
            # Look for long paragraphs (often the main content)
            r'(?:<p>|\n\n)[^<>\n]{200,}(?:</p>|\n\n)',
            # Look for sections with a title followed by substantial text
            r'(?:Title|Heading):\s*[^\n]{10,}\n[^\n]{200,}'
        ]
        extracted_text = ""
        for pattern in main_content_patterns:
            matches = re.finditer(pattern, text, flags=re.DOTALL | re.IGNORECASE | re.MULTILINE)
            for match in matches:
                extracted_text += match.group(0) + "\n\n"

        # If no main content found, use the original text
        if not extracted_text:
            return text.strip()

        return extracted_text.strip()
    # Extract domains for all URLs
    df['domain'] = df['url'].apply(get_registered_domain)

    # Group by filename
    grouped = df.groupby('filename')

    # Function to get row with shortest URL
    def get_shortest_url_row(group):
        return group.loc[group['url'].str.len().idxmin()]
    def lower(text):
        text = text.lower()
        return text
    # Apply function to each group
    shortest_urls = grouped.apply(get_shortest_url_row)

    # Reset index to flatten the DataFrame
    shortest_urls = shortest_urls.reset_index(drop=True)
    shortest_urls['temp'] = shortest_urls['web_text_content'].apply(preprocess_text)
    # Create api_content column
    shortest_urls['temp'] = shortest_urls['temp'].apply(lower)
    shortest_urls['api_content'] = shortest_urls['temp'] + ' || ' + shortest_urls['domain']
    #remove temp
    shortest_urls.drop('temp', axis=1, inplace=True)
    # Select and return relevant columns
    result = shortest_urls[['filename', 'title', 'web_text_content','url','api_content']]
    return result
