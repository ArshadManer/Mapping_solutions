import pandas as pd
import numpy as np
from datetime import time

def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    pivot = df.pivot(index='id_start', columns='id_end', values='distance')

    distance_matrix = pivot.add(pivot.transpose(), fill_value=0)

    for i in range(len(distance_matrix)):
        distance_matrix.iloc[i,i] = 0

    for i in range(len(distance_matrix)):
        for j in range(i+1, len(distance_matrix)):
            if pd.isnull(distance_matrix.iat[i, j]):
                distance_matrix.iat[i, j] = distance_matrix.iloc[i, :j].sum() + distance_matrix.iloc[:i, j].sum()
                distance_matrix.iat[j, i] = distance_matrix.iat[i, j]

    return distance_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    series = df.unstack()
    unrolled_df = series.reset_index()

    unrolled_df.columns = ['id_start', 'id_end', 'distance']
    unrolled_df = unrolled_df[unrolled_df['id_start'] != unrolled_df['id_end']]

    return unrolled_df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                            of the reference ID's average distance.
    """
    avg_distances = df.groupby('id_start')['distance'].mean()
    reference_avg_distance = avg_distances[reference_id]


    threshold = 0.10 * reference_avg_distance
    ids_within_threshold = avg_distances[(avg_distances >= reference_avg_distance - threshold) | 
                                        (avg_distances <= reference_avg_distance + threshold)].index.tolist()

    ids_within_threshold.sort()
    
    return pd.DataFrame(ids_within_threshold,columns=["Ids"])


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}
    for vehicle_type, rate_coefficient in rate_coefficients.items():
        df[vehicle_type] = df['distance'] * rate_coefficient

    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    times = [time(hour, minute) for hour in range(24) for minute in range(0, 60, 30)]
    
    new_df = pd.DataFrame()
    
    for start_day in days:
        for end_day in days:
            for start_time in times[:-1]:
                end_time = times[times.index(start_time) + 1]
                
                temp_df = df.copy()
            
                temp_df['start_day'] = start_day
                temp_df['end_day'] = end_day
                temp_df['start_time'] = start_time
                temp_df['end_time'] = end_time
                
                vehicles = ["moto","car","rv","bus","truck"]
                discount_factor = None

                if start_day in days[:5] and end_day in days[:5]:  # Weekdays
                    if start_time < time(10, 0) or end_time > time(18, 0):
                        discount_factor = 0.8
                    elif start_time >= time(10, 0) and end_time <= time(18, 0):
                        discount_factor = 1.2
                else:  # Weekends
                    discount_factor = 0.7
                
                for vehicle in vehicles:
                    temp_df[vehicle] *=discount_factor
                
                new_df = pd.concat([new_df, temp_df])
    
    return new_df
