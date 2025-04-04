from jinja2 import Template
import time


def html_popup(row_values, template_path="templates/map/popup.html"):
    """
    Renders an HTML popup using the provided row values and an HTML template.

    Args:
        row_values (dict): A dictionary containing the data to be rendered in the popup.
            Expected keys include:
                - "name" (str): The name to be displayed.
                - "date" (str): The date to be displayed.
                - "start_date" (datetime, optional): The start date and time.
                - "type" (str): The type to be displayed.
                - "metadata" (dict): A dictionary containing additional metadata.
                    Expected keys in metadata include:
                        - "distance" (float, optional): The distance value.
                        - "total_elevation_gain" (float, optional): The total elevation gain.
                        - "moving_time" (int, optional): The moving time in seconds.
                        - "elapsed_time" (int, optional): The total elapsed time in seconds.
                        - "average_speed" (float, optional): The average speed.
                        - "max_speed" (float, optional): The maximum speed.
                        - "average_heartrate" (float, optional): The average heart rate.
                        - "max_heartrate" (float, optional): The maximum heart rate.
                        - "average_temp" (float, optional): The average temperature.
                        - "elevation_profile" (str, optional): The elevation profile.
                        - "average_watts" (float, optional): The average power in watts.
                        - "weighted_average_watts" (float, optional): The weighted average power in watts.
                        - "max_watts" (float, optional): The maximum power in watts.

        template_path (str, optional): The file path to the HTML template. Defaults to "/templates/map/popup.html".

    Returns:
        str: The rendered HTML popup as a string.
    """

    # Extract metadata with default values
    metadata = row_values.get("metadata", {})
    distance = metadata.get("distance")
    elevation_gain = metadata.get("total_elevation_gain")
    moving_time = metadata.get("moving_time")
    elapsed_time = metadata.get("elapsed_time")
    average_speed = metadata.get("average_speed")
    max_speed = metadata.get("max_speed")
    average_heartrate = metadata.get("average_heartrate")
    max_heartrate = metadata.get("max_heartrate")
    average_temp = metadata.get("average_temp")
    elevation_profile = metadata.get("elevation_profile")
    average_watts = metadata.get("average_watts")
    weighted_average_watts = metadata.get("weighted_average_watts")
    max_watts = metadata.get("max_watts")

    # Formatting
    formatted_moving_time = (
        time.strftime("%H:%M:%S", time.gmtime(moving_time))
        if moving_time is not None
        else None
    )
    formatted_elapsed_time = (
        time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        if elapsed_time is not None
        else None
    )
    start_time = (
        row_values["start_date"].time() if row_values.get("start_date") else None
    )
    distance = "{:.2f}".format(distance) if distance is not None else None
    elevation_gain = (
        "{:.0f}".format(elevation_gain) if elevation_gain is not None else None
    )
    average_speed = (
        "{:.2f}".format(average_speed) if average_speed is not None else None
    )
    max_speed = "{:.2f}".format(max_speed) if max_speed is not None else None
    average_heartrate = (
        "{:.0f}".format(average_heartrate) if average_heartrate is not None else None
    )
    max_heartrate = (
        "{:.0f}".format(max_heartrate) if max_heartrate is not None else None
    )
    average_temp = "{:.1f}".format(average_temp) if average_temp is not None else None

    average_watts = (
        "{:.0f}".format(average_watts) if average_watts is not None else None
    )
    weighted_average_watts = (
        "{:.0f}".format(weighted_average_watts)
        if weighted_average_watts is not None
        else None
    )
    max_watts = "{:.1f}".format(max_watts) if max_watts is not None else None

    # Load the HTML template from the file
    with open(template_path, "r") as file:
        html_template = file.read()

    # Render the template with the data
    html_popup = Template(html_template).render(
        name=row_values["name"],
        date=row_values["date"],
        start_time=start_time,
        type=row_values["type"],
        distance=distance,
        elevation_gain=elevation_gain,
        moving_time=formatted_moving_time,
        total_time=formatted_elapsed_time,
        average_speed=average_speed,
        max_speed=max_speed,
        average_heartrate=average_heartrate,
        max_heartrate=max_heartrate,
        average_temp=average_temp,
        elevation_profile=elevation_profile,
        average_watts=average_watts,
        weighted_average_watts=weighted_average_watts,
        max_watts=max_watts,
    )

    return html_popup
