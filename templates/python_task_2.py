import pandas as pd


def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    # Write your logic here
    pivot_df = df.pivot(index='id_start', columns='id_end', values='distance').fillna(0)
    distance_matrix = pivot_df + pivot_df.T
    for col in distance_matrix.columns:
        distance_matrix.at[col, col] = 0
    for i in distance_matrix.index:
        for j in distance_matrix.columns:
            if distance_matrix.at[i, j] == 0 and i != j:
                route1 = df[(df['id_start'] == i) & (df['id_end'] == j)]['distance'].values
                route2 = df[(df['id_start'] == j) & (df['id_end'] == i)]['distance'].values
                if len(route1) > 0 and len(route2) > 0:
                    distance_matrix.at[i, j] = route1[0] + route2[0]
                    distance_matrix.at[j, i] = route1[0] + route2[0]


    return distance_matrix


def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    # Write your logic here
    unrolled_data = []
    for id_start in df.index:
        for id_end in df.columns:
            if id_start != id_end:
                distance = df.at[id_start, id_end]
                unrolled_data.append({'id_start': id_start, 'id_end': id_end, 'distance': distance})
                df = pd.DataFrame(unrolled_data)
        return df


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
    # Write your logic here
        reference_rows = df[df['id_start'] == reference_id]
    if reference_rows.empty:
        raise ValueError(f"Reference ID {reference_id} not found in the DataFrame.")
    reference_avg_distance = reference_rows['distance'].mean()
    threshold = 0.1 * reference_avg_distance
    filtered_rows = df[(df['distance'] >= reference_avg_distance - threshold) &
                       (df['distance'] <= reference_avg_distance + threshold)]
    unique_ids = filtered_rows['id_start'].unique()
    result_df = pd.DataFrame({'id_start': unique_ids})

    return result_df.sort_values('id_start')



def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Wrie your logic here
    rate_coefficients = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}
    for vehicle_type, rate in rate_coefficients.items():
        result_df[vehicle_type] = result_df['distance'] * rate
    return result_df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    # Write your logic here
weekday_time_ranges = [(time(0, 0, 0), time(10, 0, 0)),
                           (time(10, 0, 0), time(18, 0, 0)),
                           (time(18, 0, 0), time(23, 59, 59))]

    weekend_time_ranges = [(time(0, 0, 0), time(23, 59, 59))]

    weekday_discount_factors = [0.8, 1.2, 0.8]
    weekend_discount_factor = 0.7
    result_df['start_day'] = result_df['end_day'] = result_df['start_time'] = result_df['end_time'] = None
    for index, row in result_df.iterrows():
        id_start, id_end = row['id_start'], row['id_end']
        for day in range(7):
            result_df.at[index, 'start_day'] = result_df.at[index, 'end_day'] = (pd.Timestamp.today() + pd.DateOffset(days=day)).day_name()
            for i, (start_time, end_time) in enumerate(weekday_time_ranges if day < 5 else weekend_time_ranges):
                result_df.at[index, 'start_time'] = start_time
                result_df.at[index, 'end_time'] = end_time
                discount_factor = weekday_discount_factors[i] if day < 5 else weekend_discount_factor
                for vehicle_type in ['moto', 'car', 'rv', 'bus', 'truck']:
                    result_df.at[index, vehicle_type] *= discount_factor

    return result_df
