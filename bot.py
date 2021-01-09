from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import matplotlib.pyplot as plt

#This is the url we will be scraping the headlines from
#After t= in the url, any ticker can be added in to scrape info for that ticker
finviz_url = 'https://finviz.com/quote.ashx?t='

#These are the tickers we will be using in this script
tickers = ['AMZN', 'FB', 'TSLA']

#This is the dictionary we're going to add all of our news data too
news_tables = {}

#This for loop iterates through our tickers array 
for ticker in tickers:

    #This appends our tickers from the ticker to the finviz url
    url = finviz_url + ticker

    #This is our request variable that requests the data from our url
    req = Request(url=url, headers={'user-agent': 'my-app'})

    #We use this to open our request
    response = urlopen(req)
    
    #we use beutiful soup to parse through the html code of our link
    html = BeautifulSoup(response, features='html.parser')

    #This gets us the news table object from the html code which holds all of the headlines
    news_table = html.find(id='news-table')

    #Here we add the news table object to the news tables dictionary with each ticker as an individual key
    news_tables[ticker] = news_table



parsed_data = []

#We are going to iterate over our news table dictionary
for ticker, news_table in news_tables.items():
    
    for row in news_table.findAll('tr'):

        #Get the title of the news in each row
        title = row.a.text


        date_data = row.td.text.split(' ')

        #If the length of the date is 1 then it is a timestamp, else it is a date so it should come before the time
        if len(date_data) == 1:
            time = date_data[0]
        else:
            date = date_data[0]
            time = date_data[1]

        parsed_data.append([ticker, date, time, title])

#Create a pandas dataframe with our info
df = pd.DataFrame(parsed_data, columns=['ticker', 'date', 'time', 'title'])


#Initialize vader
vader = SentimentIntensityAnalyzer()


#Create a lambda fucntion to apply the polarity score 
f = lambda title: vader.polarity_scores(title)['compound']

#Create a new column with the name compound and apply the function to get the polarity score
df['compound'] = df['title'].apply(f)
df['date'] = pd.to_datetime(df.date).dt.date



plt.figure(figsize=(10,8))

#This will give us the mean of the tickers sentiment for the dates and unstack the data
mean_df = df.groupby(['ticker', 'date']).mean().unstack()


#This essentially removes the compund column and pairs the dates with the compound scores
mean_df = mean_df.xs('compound',axis='columns').transpose()

#We now plot the info in a bar chart
mean_df.plot(kind='bar')
plt.show()

