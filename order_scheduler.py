from datetime import datetime
import time
from order_automation import order_automation
import asyncio
from typing import List
import json
import requests

def get_current_time():

    url = "http://worldtimeapi.org/api/timezone/Africa/Lagos"
    api_response = requests.get(url)
    print(api_response.text)
    # extract time and format to datetime object
    return json.dumps(api_response.text)

async def schedule_single_order(drug_name, number_of_order, delivery_time):
    datetime_format = "%Y-%m-%d %H:%M:%S"
    order_time = datetime.strptime(delivery_time, datetime_format)
    current_time = get_current_time()
    print(current_time)

    # Calculate the time difference until the order_time
    time_difference = order_time - current_time
    if time_difference.total_seconds() > 0:
        print(f"Waiting for {time_difference.total_seconds()} seconds until {order_time}")
        await asyncio.sleep(time_difference.total_seconds())
        print("Placing order now!")
        ordering = order_automation([(drug_name, number_of_order)])
        return ordering
    else:
        return (f'Cannot place order for {drug_name} because order time has passed!')

async def schedule_orders(items):
    order_tasks = []

    for drugs_dict in items:
        dict_keys = list(drugs_dict.keys())
        drug_name = drugs_dict[dict_keys[0]]
        number_of_order = drugs_dict[dict_keys[1]]
        delivery_time = drugs_dict[drugs_dict[2]]

        order_tasks.append(schedule_single_order(drug_name, number_of_order, delivery_time))

    await asyncio.gather(*order_tasks)

def main(items:list):
    loop = asyncio.get_event_loop()

    loop.run_until_complete(schedule_orders([('Postinor *2 Tabs', 3, '2024-01-29 08:12:2'),
                                             ('Ellaone 30Mg *1Tab', 4, '2024-01-29 08:12:2')]))


