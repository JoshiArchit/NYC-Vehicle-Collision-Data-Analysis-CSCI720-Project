"""
Filename : dataAnalysis.py
Author : Archit Joshi, Parth Sethia
Description : Analysis of the NYC crash dataset
Language : python3
"""
import warnings
import psycopg2
import pandas as pd
from matplotlib import pyplot as plt
from analyseData import separateData
import matplotlib.patches as mpatches


def connectDB():
    """
    Helper function to connect to a database db_720 to load NYC Crash data to.
    If database doesn't exist, the function will create the database and
    re-attempt to estabilish connection.

    :return: database connection object
    """
    host = 'localhost'
    username = 'postgres'
    password = 'Archit@2904'
    port = '5432'
    database = 'db_720'

    try:
        # Attempt to connect to the existing database
        conn = psycopg2.connect(database=database, user=username,
                                password=password, host=host,
                                port=port)
        return conn
    except psycopg2.Error as e:
        print("Connection error, check credentials or run createDB.py")


def dayWithMostAccidents(connection):
    """
    This function will find the day of the week which has most number of accidents
    :param connection: connection object
    """

    # aggregation script to find the day which has maximum number of accidents
    aggregation_script = "select trim(to_char(crash_date, 'Day')) as Day, " \
                         "count(*) as count " \
                         "from nyc_crashes " \
                         "group by Day " \
                         "order by count desc"
    try:
        connection_cursor = connection.cursor()
        connection_cursor.execute(aggregation_script)
        result = connection_cursor.fetchone()
    except psycopg2.Error as e:
        print(e)
        return False
    connection.cursor().close()
    print("5. Which day of the week has the most accidents?")
    print("Answer:", result[0])
    print()


def hourWithMostAccidents(connection):
    """
    This function will find the hour of the day which has most accidents
    :param connection: connection object
    """

    # aggregation script to find the hour of the day which has most number of accidents
    aggregation_script = "select trim(split_part(crash_time, ':', 1)) as hour, " \
                         "count(*) as count " \
                         "from nyc_crashes " \
                         "group by hour " \
                         "order by count desc;"
    try:
        connection_cursor = connection.cursor()
        connection_cursor.execute(aggregation_script)
        result = connection_cursor.fetchone()
    except psycopg2.Error as e:
        print(e)
        return False
    connection.cursor().close()
    print("6. Which hour of the day has the most accidents?")
    print("Answer:", result[0])
    print()


def twelveDaysWithMostAccidentsIn2020(connection):
    """
    This function will calculate top 12 days of 2020 which had most number of accidents
    :param connection: connection object
    :return:
    """

    # aggregation script to calculate top 12 days of 2020 which had most number of accidents
    aggregation_script = "select case " \
                         "when extract(Month from x.crash_date)=7 then concat('July ', extract(Day from x.crash_date)) " \
                         "when extract(Month from x.crash_date) =6 then concat('June ', extract(Day from x.crash_date)) " \
                         "end from (" \
                         "select crash_date, count(*) as count from nyc_crashes " \
                         "where extract(year from crash_date) = '2020' " \
                         "group by crash_date " \
                         "order by count desc limit 12) x " \
                         "order by x.crash_date;"
    try:
        connection_cursor = connection.cursor()
        connection_cursor.execute(aggregation_script)
        result = connection_cursor.fetchall()
    except psycopg2.Error as e:
        print(e)
        return False
    connection.cursor().close()
    # initialization
    june = []
    july = []
    # removing the name of month from the date
    for days in result:
        if 'June' in days[0]:
            june.append(days[0].replace("June ", ""))
        elif "July" in days[0]:
            july.append(days[0].replace("July ", ""))
    print(
        "7. In the year 2020, which 12 days had the most accidents?\nCan you speculate about why this is?")
    print("Ans: ", ", ".join(day for day in june), "June", "\n     ",
          ", ".join(day for day in july), "July")


def top100ConsecutiveDaysWithMostAccidents(connection):
    """
    This function will find top 100 consecutive days with most accidents
    :param connection: connection object
    """

    # aggregation script to count accidents on every day
    aggregation_script = "select crash_date, " \
                         "count(*) as number_of_crash " \
                         "from nyc_crashes " \
                         "where crash_date between '2019-01-01' and '2020-10-31' " \
                         "group by crash_date " \
                         "order by crash_date;"

    try:
        connection_cursor = connection.cursor()
        connection_cursor.execute(aggregation_script)
        result = connection_cursor.fetchall()
    except psycopg2.Error as e:
        print(e)
        return False
    connection.cursor().close()

    print(
        "4. For the year of January 2019 to October of 2020, which 100 consecutive days had the most accidents?")
    all_days = []
    accidents_in_a_day = []
    max_accidents = 0
    start_index_for_max_accidents = None

    # logic to find top 100 consecutive days with most accidents
    for values in result:
        all_days.append(str(values[0]))
        accidents_in_a_day.append(values[1])

    for index in range(0, 122):
        total_accidents_in_current_range = sum(
            accidents_in_a_day[index:index + 100])
        if total_accidents_in_current_range > max_accidents:
            max_accidents = total_accidents_in_current_range
            start_index_for_max_accidents = index
    print("Answer: The 100 consecutive days with most accidents start from",
          all_days[start_index_for_max_accidents], "till",
          all_days[start_index_for_max_accidents + 99])
    print()


def categorize_time_frame(hour):
    """
    Function to categorize the time into time frames
    :param hour: hour of the day based on 24 hrs clock
    :return:
    """
    if 0 <= hour <= 5:
        return 'Night'
    elif 6 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 17:
        return 'Afternoon'
    elif 18 <= hour <= 24:
        return 'Evening'


def dataChangeByTimeFrameFromTwoYears(crash_data_2019, crash_data_2020):
    """
    This function will find out what changed in two years based on time and will create a pie chart
    :param crash_data_2019: crash data from year 2019
    :param crash_data_2020: crash data from year 2020
    """
    # Create legend
    legend_patches = [
        mpatches.Patch(color='orange', label='Morning --> 06:00 to 11:59'),
        mpatches.Patch(color='blue', label='Afternoon --> 12:00 to 17:59 '),
        mpatches.Patch(color='green', label='Evening --> 18:00 to 23:59'),
        mpatches.Patch(color='red', label='Night --> 00:00 to 05:59')
    ]

    # converting the varchar data format to datetime
    crash_data_2019['crash_time'] = pd.to_datetime(
        crash_data_2019['crash_time'])

    # getting the hour from the crash time
    crash_data_2019['time_frame'] = crash_data_2019[
        'crash_time'].dt.hour.apply(categorize_time_frame)

    # performing aggregation and getting percentage of crash in each time frame
    result2019 = crash_data_2019.groupby('time_frame').agg(
        accident_count=('crash_time', 'count'),
        percentage=('crash_time',
                    lambda x: round(len(x) * 100.0 / len(crash_data_2019), 1))
    ).reset_index()

    result2019 = result2019.sort_values(by='percentage', ascending=False)

    # 2020 data
    crash_data_2020['crash_time'] = pd.to_datetime(
        crash_data_2020['crash_time'])
    crash_data_2020['time_frame'] = crash_data_2020[
        'crash_time'].dt.hour.apply(categorize_time_frame)
    result2020 = crash_data_2020.groupby('time_frame').agg(
        accident_count=('crash_time', 'count'),
        percentage=('crash_time',
                    lambda x: round(len(x) * 100.0 / len(crash_data_2020), 1))
    ).reset_index()

    result2020 = result2020.sort_values(by='percentage', ascending=False)

    # Generating pie charts
    fig, axs = plt.subplots(1, 2, figsize=(16, 8))
    # pie chart for 2019
    axs[0].pie(result2019['percentage'], labels=result2019['time_frame'],
               autopct='%1.1f%%', startangle=90)
    axs[0].set_title('Distribution of Accidents by Time Frame (2019)')

    # Pie chart for 2020
    axs[1].pie(result2020['percentage'], labels=result2020['time_frame'],
               autopct='%1.1f%%', startangle=90)
    axs[1].set_title('Distribution of Accidents by Time Frame (2020)')

    # Add legend
    plt.legend(handles=legend_patches, title="Time Blocks", loc="upper left",
               bbox_to_anchor=(0, 1), bbox_transform=plt.gcf().transFigure)

    plt.show()


def dataChangeByZipcodeFromTwoYears(crash_data_2019, crash_data_2020):
    """
    This function will find out what changed in two years based on region
    :param crash_data_2019: crash data from year 2019
    :param crash_data_2020: crash data from year 2020
    :return:
    """
    crash_data_2019['year'] = crash_data_2019['crash_date'].dt.year
    crash_data_2020['year'] = crash_data_2020['crash_date'].dt.year

    region_accidents_count_2019 = crash_data_2019.groupby(
        ['zip_code', 'year']).size().reset_index(name='count')
    region_accidents_count_2020 = crash_data_2020.groupby(
        ['zip_code', 'year']).size().reset_index(name='count')

    plot_time_series_for_accidents(region_accidents_count_2019,
                                   region_accidents_count_2020)


def plot_time_series_for_accidents(region_accidents_count_2019,
                                   region_accidents_count_2020):
    """
    This function will create plot time series for accidents for the year 2019 and 2020
    :param region_accidents_count_2019: accidents count in 2019 segregated by region
    :param region_accidents_count_2020: accidents count in 2020 segregated by region
    """
    plt.figure(figsize=(10, 6))
    plt.plot(region_accidents_count_2019['zip_code'],
             region_accidents_count_2019['count'], label='2019 Accidents',
             marker='o')
    plt.plot(region_accidents_count_2020['zip_code'],
             region_accidents_count_2020['count'], label='2020 Accidents',
             marker='o')

    plt.title('Accidents Over Time (2019 vs 2020)')
    plt.xlabel('Zip Code')
    plt.ylabel('Number of Accidents')
    plt.xticks(rotation=90)
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    """
    This is the main function
    """
    conn = connectDB()
    warnings.filterwarnings("ignore",
                            message="pandas only supports SQLAlchemy connectable.*")
    dataframe = pd.read_sql("SELECT * FROM nyc_crashes", conn)
    crash_data_2019, crash_data_2020 = separateData(dataframe)
    # dataChangeByZipcodeFromTwoYears(crash_data_2019, crash_data_2020)
    dataChangeByTimeFrameFromTwoYears(crash_data_2019, crash_data_2020)
    # top100ConsecutiveDaysWithMostAccidents(conn)
    # dayWithMostAccidents(conn)
    # hourWithMostAccidents(conn)
    # twelveDaysWithMostAccidentsIn2020(conn)


if __name__ == '__main__':
    main()
