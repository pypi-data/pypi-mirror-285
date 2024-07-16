import json

import gandai as ts
from gandai import secrets
from openai import OpenAI

client = OpenAI(
    api_key=secrets.access_secret_version("OPENAI_KEY"),
)

## gpt4


def ask_gpt4(messages: list, temperature=0.0) -> json:
    chat_completion = client.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        # model="gpt-4",
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    #
    print(chat_completion.usage)
    return json.loads(chat_completion.choices[0].message.content)


HOW_TO_ENRICH = """
To update an attribute for a company you will create an event with the company's domain
of type "update". This will update that company's meta field 

here is an example update event

{
    "domain": "lol.com",
    "actor_key": "chatgpt",
    "type": "update",
    "data": {
        "contact_name": "Bob"
    }
}

Here are all the fields you can use for event['data']

c.data->>'gpt_description' as gpt_description, -- a description of the company for use by private equity research analyst to understand the company.

You will fill out the description field with a description of the company. 
The description will be a comprehensive description of the company for use 
by private equity research analyst to understand the company.

c.data->>'employees' as employees, -- the INTEGER number of employees at the company. prefer the grata estimate. this is an integer.
c.data->>'ownership' as ownership, -- one of ["bootstrapped","investor_backed","public","public_subsidiary","private_subsidiary","private_equity","private_equity_add_on"] 
c.data->>'headquarters' as headquarters,
c.data->>'city' as city,
c.data->>'state' as state,
c.data->>'designation' as designation,
c.data->>'products' as products, -- products are physical goods sold by the company. do not list services here. A brand is not a product, do not list brands here.
c.data->>'services' as services, -- services are intangible goods offered by the company. do not list products here.
c.data->>'end_customer' as end_customer, -- what types of customers does the company serve. If commercial, what industry(s). do not list specific customers here.
c.data->>'geographies' as geographies, -- geographies are the areas where the company does business. 
c.data->>'year_founded' as year_founded,
c.data->>'linkedin' as linkedin, -- linkedinUrl 
c.data->>'linkedin_range' as linkedin_range,
c.data->>'industry' as industry,
c.data->>'revenue_estimates' as revenue_estimates,
c.data->>'location_count' as location_count,
c.data->>'business_models' as business_models,
c.data->>'facility_size' as facility_size,
c.data->>'contact_name' as contact_name,
c.data->>'contact_title' as contact_title,
c.data->>'contact_email' as contact_email,
c.data->>'contact_phone' as contact_phone,
c.data->>'contact_address' as contact_address,

For fields that are lists, you will use a csv string 
For these lists, such as products or services, try to stick to top 5 or less areas of focus.


If you are unsure, just leave that key out of the response data

"""


HOW_TO_RESPOND = """
You will respond with an JSON object that looks like this:
{
    "events": List[Event],
}
"""

HOW_TO_GOOGLE_MAPS = """
To search the Google Maps Places API
You will respond with this
{"events": List[asdict(Event)]}

Unless otherwise directed you will return 10 centroids

There are 20 results per centroid
So if the user asks for 100 results you will return the count divided by 20

Give me the query strings you would use to search for 
Each query string should be small enough for a Google Maps search

For example to search throughout Dallas you might use:
dentists in Dallas, TX
dentists in Highland Park, TX
dentists in Grapevine, TX
dentists in Plano, TX

Now give me the queries that you would use

Here's some Event examples:
[{
    "type": "maps",
    "search_uid": 1700,
    "actor_key": "7138248581",
    "data": {
        "query": "dentists in Dallas, TX"
    }
}]

"""

HOW_TO_IMPORT = """
// example Import(Event)
{
    "search_uid": 19696114,
    "domain": null,
    "actor_key": "4805705555",
    "type": "import",
    "data": {
        "stage": "advance",
        "domains": [
            "buybits.com",
            "lidoradio.com",
            "rocklandcustomproducts.com",
            "sigmasafety.ca",
        ],
    },
}

Here are the stages along with their labels:
The only valid stages are labelMap.keys()
const labelMap = {
    "land": "Landing",
    "create": "Inbox",
    "advance": "Review",
    "validate": "Validated",
    "send": "Client Inbox",
    "client_approve": "Client Approved",
    "sync": "Synced",
    "reject": "Reject",
    "conflict": "Conflict",
    "client_conflict": "Client Conflict",
    "client_reject": "Client Reject"
}
"""

HOW_TO_TRANSITION = """
To move a target to a different stage you will create an event with the targets domain 
and the stage you want to move it to.

domain should include domain only, no subdomain or protocol

// example Event
{
    "search_uid": 19696114,
    "domain": "acme.com",
    "actor_key": "5558248581",
    "type": "send",
    "data": {"key": "value"},
}


Here are the stages along with their labels:
The only valid event types are the labelMap.keys()
const labelMap = {
    "land": "Landing",
    "create": "Inbox",
    "advance": "Review",
    "validate": "Validated",
    "send": "Client Inbox",
    "client_approve": "Client Approved",
    "sync": "Synced",
    "reject": "Reject",
    "conflict": "Conflict",
    "client_conflict": "Client Conflict",
    "client_reject": "Client Reject"
}
"""

HOW_TO_GOOGLE = """

To search Google, you will create an Event object.

@dataclass
class Google(Event):
    search_uid: int  # fk # add index
    actor_key: str  # fk
    type: str  
    data: dict = field(default_factory=dict)
    id: int = field(default=None)  # pk
    # created: int = field(init=False)

List[Event] examples asdict:

[{
  'search_uid': 200,
  'domain': null,
  'actor_key': '3125740050',
  'type': 'google',
  'data': {'q': '"golf cart" AND audio'},
  'created': 1697813193},
{
  'search_uid': 5255570,
  'domain': null,
  'actor_key': '3102835279',
  'type': 'google',
  'data': {'q': '"commercial" AND "door" AND ("repair" OR "maintenance" OR "replacement") AND "new York City"'},
  'created': 1697814555}]

The type is 'google'
You will not set the id or created fields.
The default count is 10

"""


HOW_TO_SEARCH_GRATA_API = """

Search
POST
https://search.grata.com
/api/v1.3/search/
Returns Grata-powered search results based on an input search query. If you're using any the filters in the UI that are not presented below, the results may differ.

Request
Headers
Authorization
string
required
Token

Content-Type
string
application/json

Body

application/json

application/json
Search input criteria for company search.

Criteria inputs for company search query.

include
array[string]
String used for keyword search. This is an array of keywords

Example:
["CRM, proptech"]
exclude
array[string]
Keywords to exclude from the search.

op
string
The operation performed on the keywords (any or all). 'Any' indicates that any of the specified keywords can be included within a company's website. 'All' indicates that all of the specified keywords should be included within a company's website.

Allowed values:
any
all
Example:
any
page_token
string
String used for pagination. The initial response body for a given search will contain a page_token that can be used for additional results. Insert the page token string into the request body.

lists
array[string]
Grata list IDs to search within.

industry_classifications
object
Industry classification code for the company. Pass the industry NAICS code or Grata's specific software industry code listed in the mapping doc - https://grata.stoplight.io/docs/grata/branches/v1.3/42ptq2xej8i5j-software-industry-code-mapping

include
array[number]
exclude
array[number]
end_customer
array[string]
End vertical that the company sells to.

Allowed values:
b2b
b2c
information_technology
professional_services
electronics
commercial_and_residential_services
hospitality_and_leisure
media
finance
industrials
transportation
education
agriculture
healthcare
government
consumer_product_and_retail
ownership
array[string]
Ownership types to search and sort on.

Allowed values:
bootstrapped
investor_backed
public
public_subsidiary
private_subsidiary
private_equity
private_equity_add_on
business_models
array[string]
Business models to search on.

Allowed values:
software
software_enabled
services
hardware
content_and_publishing
investment_banks_and_business_brokers
education
directory
job_site
staffing_and_recruiting
private_equity_and_venture_capital
private_schools
retailer
manufacturer
distributor
producer
marketplace
hospitals_and_medical_centers
colleges_and_universities
government
us_federal_agencies
nonprofit_and_associations
religious_institutions
is_funded
boolean
Indicates whether or not the company has received outside funding.

funding_size
array[number]
Range of funding the company has received in USD. Ranges can only start and begin with the following values: 0, 5000000, 10000000, 20000000, 50000000, 100000000, 200000000, 500000000, 500000001. 500000001 equates to maximum.

>= 2 items
<= 2 items
funding_stage
array[string]
Allowed values:
early_stage_funding
late_stage_funding
private_equity_backed
other_funding
pre_ipo_funding
employees_change_time
string
The interval for employee growth rate.

Allowed values:
month
quarter
six_month
annual
grata_employees_estimates_range
array[number]
The range of employee counts based on Grata Employee estimates. Inputting 100,001 as the maximum value will search for all employee sizes above the minimum. [100,100001] will search for all companies with 100 or more employees

employees_on_professional_networks_range
array[number]
The range of employee counts listed on professional networks. Inputting 100,001 as the maximum value will search for all employee sizes above the minimum. [100,100001] will search for all companies with 100 or more employees

employees_change
array[number]
Range of % employee growth.

year_founded
array[number]
Range of founding years.

headquarters
object
Headquarter locations supports all countries and US city/states. State cannot be left blank if city is populated. Country cannot be other than United States if searching for city/state.

include
array[object]
exclude
array[object]
Responses
200
400
401
404
405
429
500
OK

Body

application/json

application/json
companies
array[object]
name
string
Name of the company.

company_uid
string
Unique alphanumeric Grata ID for the company (case-sensitive).

url
string
URL to the company's Grata profile.

domain
string
Domain of the company.

description
string
Description of the company.

company-basic
Export
companies
array[object]
name
string
Name of the company.

company_uid
string
Unique alphanumeric Grata ID for the company (case-sensitive).

url
string
URL to the company's Grata profile.

domain
string
Domain of the company.

description
string
Description of the company.

{
  "companies": [
    {
      "name": "Slack",
      "company_uid": "7W46XUJT",
      "url": "https://search.gratadata.com/search?c=MDKZCCG3",
      "domain": "slack.com",
      "description": "Slack is a global collaboration hub that makes people’s working lives simpler, more pleasant and more productive. From global Fortune 100 companies to corner markets, businesses and teams of every kind use Slack to bring the right people together with all the right information. Slack is headquartered in San Francisco California and has nine offices around the world. Slack is where work flows. It's where the people you need, the information you share, and the tools you use come together to get things done."
    }
  ]
}

search-filters
Export
Criteria inputs for company search query.

headquarters
.
exclude[]
include
array[string]
String used for keyword search. This is an array of keywords

Example:
["CRM, proptech"]
exclude
array[string]
Keywords to exclude from the search.

op
string
The operation performed on the keywords (any or all). 'Any' indicates that any of the specified keywords can be included within a company's website. 'All' indicates that all of the specified keywords should be included within a company's website.

Allowed values:
any
all
Example:
any
page_token
string
String used for pagination. The initial response body for a given search will contain a page_token that can be used for additional results. Insert the page token string into the request body.

lists
array[string]
Grata list IDs to search within.

industry_classifications
object
Industry classification code for the company. Pass the industry NAICS code or Grata's specific software industry code listed in the mapping doc - https://grata.stoplight.io/docs/grata/branches/v1.3/42ptq2xej8i5j-software-industry-code-mapping

include
array[number]
exclude
array[number]
end_customer
array[string]
End vertical that the company sells to.

Allowed values:
b2b
b2c
information_technology
professional_services
electronics
commercial_and_residential_services
hospitality_and_leisure
media
finance
industrials
transportation
education
agriculture
healthcare
government
consumer_product_and_retail
ownership
array[string]
Ownership types to search and sort on.

Allowed values:
bootstrapped
investor_backed
public
public_subsidiary
private_subsidiary
private_equity
private_equity_add_on
business_models
array[string]
Business models to search on.

Allowed values:
software
software_enabled
services
hardware
content_and_publishing
investment_banks_and_business_brokers
education
directory
job_site
staffing_and_recruiting
private_equity_and_venture_capital
private_schools
retailer
manufacturer
distributor
producer
marketplace
hospitals_and_medical_centers
colleges_and_universities
government
us_federal_agencies
nonprofit_and_associations
religious_institutions
is_funded
boolean
Indicates whether or not the company has received outside funding.

funding_size
array[number]
Range of funding the company has received in USD. Ranges can only start and begin with the following values: 0, 5000000, 10000000, 20000000, 50000000, 100000000, 200000000, 500000000, 500000001. 500000001 equates to maximum.

>= 2 items
<= 2 items
funding_stage
array[string]
Allowed values:
early_stage_funding
late_stage_funding
private_equity_backed
other_funding
pre_ipo_funding
employees_change_time
string
The interval for employee growth rate.

Allowed values:
month
quarter
six_month
annual
grata_employees_estimates_range
array[number]
The range of employee counts based on Grata Employee estimates. Inputting 100,001 as the maximum value will search for all employee sizes above the minimum. [100,100001] will search for all companies with 100 or more employees

employees_on_professional_networks_range
array[number]
The range of employee counts listed on professional networks. Inputting 100,001 as the maximum value will search for all employee sizes above the minimum. [100,100001] will search for all companies with 100 or more employees

employees_change
array[number]
Range of % employee growth.

year_founded
array[number]
Range of founding years.

headquarters
object
Headquarter locations supports all countries and US city/states. State cannot be left blank if city is populated. Country cannot be other than United States if searching for city/state.

include
array[object]
city
string or null
Example:
Los Angeles
state
string or null
Example:
California
country
string
Example:
United States
exclude
array[object]
city
string or null
Example:
New York
state
string or null
Example:
New York
country
string
Example:
United States

import requests

import gandai as ts
from gandai import secrets

HEADERS = {
    "Authorization": secrets.access_secret_version("GRATA_API_TOKEN"),
    "Content-Type": "application/json",
}


messages = [
        {
            "role": "system",
            "content": HOW_TO_SEARCH_GRATA_API
        },
        
        {
            "role": "user",
            "content": "Find me private hvac companies in Alabama",
        },
    ]

api_filters: dict = ts.gpt.ask_gpt4(messages)
print(api_filters)

response = requests.post(
    "https://search.grata.com/api/v1.3/search/",
    headers=HEADERS,
    json={
        "include": api_filters["include"],
        "exclude": api_filters["exclude"],
        "grata_employees_estimates_range": api_filters["grata_employees_estimates_range"],  
        "headquarters": {
            "include": api_filters["headquarters"]["include"],
            "exclude": api_filters["headquarters"]["exclude"],
        }
    },
)


response


You will respond with the API filters for searching Grata API as a JSON object.


"""
