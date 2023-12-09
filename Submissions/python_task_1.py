import pandas as pd


def generate_car_matrix(df)->pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    
    df = df.pivot(index='id_1', columns='id_2', values='car').fillna(0)
    for index in df.index:
        df.loc[index][index] = 0
    
    return df


def get_type_count(df)->dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    
    categories = ['low', 'medium', 'high']
    
    df['car_type'] = pd.cut(df['car'], bins=[0, 15, 25, float('inf')], labels=categories)
    type_count = df['car_type'].value_counts().to_dict()
    type_count = dict(sorted(type_count.items()))

    return type_count


def get_bus_indexes(df)->list:
    """
    Returns the indexes where the 'bus' values are greater than twice the mean.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of indexes where 'bus' values exceed twice the mean.
    """
    
    bus_mean = df['bus'].mean()

    bus_indexes = df[df['bus'] > (2 * bus_mean)].index.tolist()
    bus_indexes.sort()
    

    return bus_indexes


def filter_routes(df)->list:
    """
    Filters and returns routes with average 'truck' values greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: List of route names with average 'truck' values greater than 7.
    """

    route_avg_truck = df.groupby('route')['truck'].mean()
    selected_routes = route_avg_truck[route_avg_truck > 7].index.tolist()
    selected_routes.sort()

    return selected_routes



def multiply_matrix(matrix)->pd.DataFrame:
    """
    Multiplies matrix values with custom conditions.

    Args:
        matrix (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Modified matrix with values multiplied based on custom conditions.
    """
    matrix = matrix.applymap(lambda x: round(x * 0.75, 1) if x > 20 else round(x * 1.25, 1))

    return matrix


def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
    df['startDay'] = pd.to_datetime(df['startDay'], format='%A')
    df['endDay'] = pd.to_datetime(df['endDay'], format='%A')
    df['startTime'] = pd.to_timedelta(df['startTime'])
    df['endTime'] = pd.to_timedelta(df['endTime'])
 
    df['startTimestamp'] = df['startDay'] + df['startTime']
    df['endTimestamp'] = df['endDay'] + df['endTime']

    result = df.groupby(['id', 'id_2']).apply(lambda x: (x['endTimestamp'] - x['startTimestamp']).dt.total_seconds().sum() >= 7*24*60*60)
    
    return result


