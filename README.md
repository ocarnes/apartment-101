# README
## Intro ##
The goal of Apartment 101 is to help people shop for a first apartment based on income level and apartment features. The American Consumer Credit Counseling organization advocates that 35 percent of your gross income should go toward your housing and debt service [[1]](https://www.quicken.com/taking-inventory-your-personal-finances-how-much-your-paycheck-should-you-budget-bills-s). Apartment 101 calculates a recommended range for rent based on annual income and debt, which it then uses to search for available units.

| Monthly Salary | Monthly Student Loan Payment | Housing Percent | Max Recommended Living Expenses|
|:-------------:|:-------------:|:-----:|:-----:|
| $50,000 / 12  | -$250         | x0.35 | **=$1370.6** |

Apartment listings have been scraped from Apartments.com based on location and desired rent using a modified version of Adina Stoica's scraper found here [[2]](https://github.com/adinutzyc21/apartments-scraper). Once a user starts selecting potential apartments, further recommendations are provided based on similarities to the original selections.

### Contents ###
1. [Data collection](#data-collection)
2. [Data cleaning](#data-cleaning)
3. [Feature selection](#feature-selection)
4. [Recommendations](#recommendations)
5. [Recommendation optimization](#recommendation-optimization)
6. [Production](#production)
7. [Future steps](#future-steps)


## Data Collection ##
The data collection step involved scraping listings based on the city of interest and maximum rent. The [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) python package was used to parse text scraped
from Apartments.com. Once scraped, data is warehoused in

## Data Cleaning ##
Data was then cleaned by filling in missing data (usually square footage), in addition to filtering for fraudulent listings. Examples of fraudulent listings can be seen below where rent is listed way below average for the area, pictures are too high quality for a single listing, units are often listed as fully furnished, and instructions specify communicating via email rather than by phone or text.

![Fraudulent Listing](/img/Fraud.png)

Descriptions and pictures are often pulled from real for sale ads so a quick google search of the description and / or the email provided can often prove fraudulence when in doubt. For the purpose of this project, however, listings with outlier price / sq ft values were dropped for simplicity.

## Feature Selection ##
Apartments.com provides a lot of features but they are unevenly filled out and placed in random locations throughout the listing. Apartment 101 currently selects city, description, rent, and square footage for features, in addition to calculating distance from a chosen point of interest (if you want to live near work or family, for instance).  

## Recommendations ##
For this project, content-based filtering was selected because we are trying to make predictions based on similarities between items rather than between items and people.

![Item-item similarity](/img/item-item-similarity.png)

In terms of apartments in Denver, for example, viewing [Welton Park](https://www.apartments.com/welton-park-denver-co/957rr74/) resulted in the following recommendations:

| Recommendation| Apartment     | Price | Size |
|:-------------:| ------------- | ----- | ----- |
| Original      |[Welton Park](https://www.apartments.com/welton-park-denver-co/957rr74/) | $945  |  576 sqft |
|       1       |[The Ogden Arms Apartments](https://www.apartments.com/the-ogden-arms-apartments-denver-co/zxlmzyz/) | $1035| 625 sqft |
|       2       |[The Vines](https://www.apartments.com/the-vines-denver-co/6bzm3kr/)|   $1295 | 800 sqft |
|       3       |[330 E 10th Ave](https://www.apartments.com/330-e-10th-ave-denver-co/hc6c8n1/)|    $995 | 605 sqft |
|       4       |[1148 Washington St.](https://www.apartments.com/1148-washington-st-denver-co-unit-6/t8q6858/)|    $975 | 600 sqft |
|       5       |[1320 E 14th Ave](https://www.apartments.com/1320-e-14th-ave-denver-co-unit-03/ds1tkgk/)|    $1000 | 600 sqft

## Recommendation Optimization ##


## Production ##
As a final touch, I've created a Flask app for a more interactive experience of Apartment 101, which can be found [here](website). Users can input salary and debt data for rent customization, or they can simply proceed to listings based on predefined city and price range limits.

## Future Steps ##
1. Perform further nlp on apartment descriptions for better identification of fraudulent listing_scraper
2. Add features like pets, parking, and in-unit washer/dryers using a combination of provided feature listings and further nlp (features sometimes listed in description rather than as features)
3. Complete flask app for real-time salary and debt computations
