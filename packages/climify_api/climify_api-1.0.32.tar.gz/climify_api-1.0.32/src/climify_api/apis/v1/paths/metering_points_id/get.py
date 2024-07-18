from collections import defaultdict
from dataclasses import dataclass
import typing_extensions
import urllib3
from urllib3._collections import HTTPHeaderDict

from datetime import date, datetime, timedelta  # noqa: F401
from dateutil.relativedelta import relativedelta
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401
from pandas import DataFrame, concat
from typing import List
from pydantic import parse_raw_as
from varname import nameof
import pytz


from climify_api.apis.PathBase import PathBase  # noqa: F401

from climify_api.exceptions import ApiValueError, ClimifyApiException
from climify_api.api_client import ClimifyApiResponse, ClimifyApiResponseWithoutDeserialization
from climify_api.models import SensorDataExtDto

PATH = 'metering-points/{id}'

def convert_values_to_dataFrame(data: List[SensorDataExtDto]) -> DataFrame:
    """Converts the sensor values to pandas DataFrames inplace.

    :param data: List of sensor data DTOs with sensor data as list of Data models
    :type data: List[SensorDataExtDto]
    :return: The list of sensor data with the updated data values
    :rtype: DataFrame
    """
    if len(data) == 0:
        return data
    
    for sensor in data:
        variables = list(sensor.data[0].values.keys())
        columns = [nameof(sensor.data[0].time)] + variables
        values = [[row.time] + [row.values[col] for col in variables] for row in sensor.data]
        sensor.data = DataFrame(values, columns = columns)

    return data

class GetMeteringPointValuesById(PathBase):
    def get_metering_point_values_by_id(
        self,
        metering_point_id: int,
        from_datetime: datetime = datetime.today() - relativedelta(month=1),
        to_datetime: datetime = datetime.today(),
        as_dataframe: bool = False,
        access_token: str = None,
        stream: bool = False,
        timeout: typing.Optional[typing.Union[int, typing.Tuple]] = None,
        skip_deserialization: bool = False,
    ) -> ClimifyApiResponse[List[SensorDataExtDto]]:
        """Returns metering values from devices associated with the given metering point.

        from_datetime and to_datetime:
            The default time period of the data is 3 months. 
            Thus the sensor period is always the last 3 months unless *both* time period variables are specified.
            The storage time is 3 years for the data, from_datetime must therefore be later than this point.

        :param metering_point_id: Location identifier
        :type metering_point_id: int
        :param from_datetime: Start time for wanted sensor data period
        :type from_datetime: datetime
        :param to_datetime: End time for wanted sensor data period
        :type to_datetime: datetime
        :param as_dataframe: If True, will convert the data of the devices to pandas DataFrames, defaults to False.
        :type as_dataframe: bool, optional
        :param access_token: Access token to use for the request
        :type access_token: str, optional
        :param stream: Toggles streaming, defaults to False
        :type stream: bool, optional
        :param timeout: How long to wait for a request in seconds, defaults to None
        :type timeout: typing.Optional[typing.Union[int, typing.Tuple]], optional
        :param skip_deserialization: Toggles whether or not to skip deserialize of the byte response, defaults to False
        :type skip_deserialization: bool, optional

        :raises ApiValueError: Will be raised if invalid inputs are provided
        :raises ClimifyApiException: Will be raised if an error occurred while calling the API

        :return: A response with a body containing the list of devices with their data
        :rtype: ClimifyApiResponse[List[SensorDataExtDto]]
        """
        # Validate input
        if metering_point_id is None:
            raise ApiValueError("Location id was given as None. A valid location id must be provided.")

        if from_datetime > to_datetime:
            raise ApiValueError(f'Given {nameof(from_datetime)} was later than the given {nameof(to_datetime)}. Please provide a valid time period.')

        if from_datetime.tzinfo != pytz.UTC:
            from_datetime = from_datetime.astimezone(pytz.UTC)
        
        if to_datetime.tzinfo != pytz.UTC:
            to_datetime = to_datetime.astimezone(pytz.UTC)

        if from_datetime < datetime.now(pytz.UTC) - relativedelta(years=3):
            raise ApiValueError(f'The given value of {nameof(from_datetime)} is longer than 3 years ago. Data storage limit is 3 years, please provide a value within this limit.')

        # Make rest request
        usedPath = PATH.replace('{id}',str(metering_point_id))

        requests = []
        subRequestToTime = to_datetime
        subRequestFromTime = max(subRequestToTime - relativedelta(months=3), from_datetime)

        while subRequestFromTime >= from_datetime:
            query_parameters = []
            for name, value in (
                ('dateTimeFrom', subRequestFromTime.replace(tzinfo=None).isoformat()+'Z' if subRequestFromTime else None), # Sets timezone to None, to remove +HH:MM
                ('dateTimeTo', subRequestToTime.replace(tzinfo=None).isoformat()+'Z' if subRequestToTime else None)
            ):
                if value:
                    query_parameters.append(f"{name}={value}")

            if len(query_parameters) > 0:
                requests.append("?" + "&".join(query_parameters))

            if subRequestFromTime == from_datetime:
                break

            subRequestToTime = subRequestFromTime - relativedelta(seconds=1)
            subRequestFromTime = max(subRequestToTime - relativedelta(months=3), from_datetime)
            
        bodies = []
        for request in requests:
            requestPath = usedPath+request
            response = self.api_client.call_api(
                resource_path=requestPath,
                method='GET',
                access_token=access_token,
                stream=stream,
                timeout=timeout
            )

            # Format response
            if not 200 <= response.status <= 299:
                raise ClimifyApiException(
                    status=response.status,
                    reason=response.reason,
                    api_response=response
                )
        
            if skip_deserialization:
                bodies.append(response.data)
                continue
            
            deserialized_body = parse_raw_as(List[SensorDataExtDto],response.data) if response.data\
                                else []
            
            # Sort observations on time
            for sensor in deserialized_body:
                sensor.data = sorted(sensor.data, key=lambda x: x.time)

            if as_dataframe:
                deserialized_body = convert_values_to_dataFrame(deserialized_body)
            
            bodies.append(deserialized_body)

        if skip_deserialization:
            response.data = bodies
            return ClimifyApiResponseWithoutDeserialization(response=response)

        sensors = {}
        for body in bodies:
            for sensor in body:
                if sensor.devId not in sensors:
                    sensors[sensor.devId] = sensor
                    continue

                sensor_data = sensors[sensor.devId]
                if as_dataframe:
                    sensor_data.data = concat([sensor_data.data, sensor.data], ignore_index=True)
                else:
                    sensor_data.data += sensor.data

        deserialized_body = list(sensors.values())

        return ClimifyApiResponse[List[SensorDataExtDto]](
            response=response,
            status=response.status,
            body=deserialized_body,
            headers=response.headers
        )