# generate python code to obtain daily weather reports from palo alto, california for 1960 to 2000.  from these data, compute the maximum temperature in each month, and plot the timeseries of maximum monthly temperatures over that time period.
# please read the api key from a file called "noaa_api_key.txt"
# api doesn't work, labels seem to be wrong

import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def fetch_weather_data(api_key, start_year, end_year):
    base_url = "https://www.ncei.noaa.gov/access/services/data/v1"
    palo_alto_station_id = "GHCN:USC00046642"
    dataset = "GHCN"
    start_date = f"{start_year}-01-01"
    end_date = f"{end_year}-12-31"

    params = {
        "dataset": dataset,
        "stations": palo_alto_station_id,
        "startDate": start_date,
        "endDate": end_date,
        "dataTypes": "TMAX",
        "units": "metric",
        "format": "csv",
        "token": api_key,
    }

    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        raise ValueError("Failed to fetch weather data: " + response.text)

    return pd.read_csv(pd.StringIO(response.text))


def main():
    with open("noaa_api_key.txt", "r") as api_key_file:
        api_key = api_key_file.read().strip()

    start_year = 1960
    end_year = 2000
    weather_data = fetch_weather_data(api_key, start_year, end_year)

    weather_data["DATE"] = pd.to_datetime(weather_data["DATE"])
    weather_data["YEAR"] = weather_data["DATE"].dt.year
    weather_data["MONTH"] = weather_data["DATE"].dt.month

    max_monthly_temps = weather_data.groupby(["YEAR", "MONTH"])["TMAX"].max().reset_index()
    max_monthly_temps["DATE"] = max_monthly_temps.apply(lambda row: datetime(row["YEAR"], row["MONTH"], 1), axis=1)

    plt.figure(figsize=(15, 5))
    plt.plot(max_monthly_temps["DATE"], max_monthly_temps["TMAX"])
    plt.xlabel("Time")
    plt.ylabel("Max Monthly Temperature (°C)")
    plt.title(f"Maximum Monthly Temperatures in Palo Alto, CA ({start_year}-{end_year})")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    main()
