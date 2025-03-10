"""Test cases for the web application."""

from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest_asyncio
from aiohttp import web
from aioswitcher.api import Command, DeviceState
from aioswitcher.schedule import Days
from assertpy import assert_that
from pytest import fixture, mark

from .. import webapp

pytestmark = mark.asyncio

fake_devicetype_powerplug_qparams = f"{webapp.KEY_TYPE}=plug"
fake_devicetype_touch_qparams = f"{webapp.KEY_TYPE}=touch"
fake_devicetype_runner_qparams = f"{webapp.KEY_TYPE}=runner"
fake_devicetype_single_runner_dual_light_qparams = f"{webapp.KEY_TYPE}=runners11"
fake_devicetype_breeze_qparams = f"{webapp.KEY_TYPE}=breeze"
fake_device_qparams = f"{webapp.KEY_ID}=ab1c2d&{webapp.KEY_IP}=1.2.3.4"
fake_device_login_key_qparams = f"{webapp.KEY_LOGIN_KEY}=18"
fake_device_index_qparams = f"{webapp.KEY_INDEX}=0"
fake_device_token_qparams = f"{webapp.KEY_TOKEN}=zvVvd7JxtN7CgvkD1Psujw=="
fake_serialized_data = {"fake": "return_dict"}

# /switcher/get_state?id=ab1c2d&ip=1.2.3.4
get_state_uri = f"{webapp.ENDPOINT_GET_STATE}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}"
# /switcher/get_state?id=ab1c2d&ip=1.2.3.4&key=18
get_state_uri2 = f"{webapp.ENDPOINT_GET_STATE}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/turn_on?id=ab1c2d&ip=1.2.3.4
turn_on_uri = f"{webapp.ENDPOINT_TURN_ON}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}"
# /switcher/turn_on?id=ab1c2d&ip=1.2.3.4&key=18
turn_on_uri2 = f"{webapp.ENDPOINT_TURN_ON}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/turn_off?id=ab1c2d&ip=1.2.3.4
turn_off_uri = f"{webapp.ENDPOINT_TURN_OFF}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}"
# /switcher/turn_off?id=ab1c2d&ip=1.2.3.4&key=18
turn_off_uri2 = f"{webapp.ENDPOINT_TURN_OFF}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/set_name?id=ab1c2d&ip=1.2.3.4
set_name_uri = f"{webapp.ENDPOINT_SET_NAME}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}"
# /switcher/set_name?id=ab1c2d&ip=1.2.3.4&key=18
set_name_uri2 = f"{webapp.ENDPOINT_SET_NAME}?{fake_devicetype_powerplug_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/set_auto_shutdown?id=ab1c2d&ip=1.2.3.4
set_auto_shutdown_uri = f"{webapp.ENDPOINT_SET_AUTO_SHUTDOWN}?{fake_devicetype_touch_qparams}&{fake_device_qparams}"
# /switcher/set_auto_shutdown?id=ab1c2d&ip=1.2.3.4&key=18
set_auto_shutdown_uri2 = f"{webapp.ENDPOINT_SET_AUTO_SHUTDOWN}?{fake_devicetype_touch_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/get_schedules?id=ab1c2d&ip=1.2.3.4
get_schedules_uri = f"{webapp.ENDPOINT_GET_SCHEDULES}?{fake_devicetype_touch_qparams}&{fake_device_qparams}"
# /switcher/get_schedules?id=ab1c2d&ip=1.2.3.4&key=18
get_schedules_uri2 = f"{webapp.ENDPOINT_GET_SCHEDULES}?{fake_devicetype_touch_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/delete_schedule?id=ab1c2d&ip=1.2.3.4
delete_schedule_uri = f"{webapp.ENDPOINT_DELETE_SCHEDULE}?{fake_devicetype_touch_qparams}&{fake_device_qparams}"
# /switcher/delete_schedule?id=ab1c2d&ip=1.2.3.4&key=18
delete_schedule_uri2 = f"{webapp.ENDPOINT_DELETE_SCHEDULE}?{fake_devicetype_touch_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/create_schedule?id=ab1c2d&ip=1.2.3.4
create_schedule_uri = f"{webapp.ENDPOINT_CREATE_SCHEDULE}?{fake_devicetype_touch_qparams}&{fake_device_qparams}"
# /switcher/create_schedule?id=ab1c2d&ip=1.2.3.4&key=18
create_schedule_uri2 = f"{webapp.ENDPOINT_CREATE_SCHEDULE}?{fake_devicetype_touch_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/set_shutter_position?id=ab1c2d&ip=1.2.3.4
set_position_uri = f"{webapp.ENDPOINT_SET_POSITION}?{fake_devicetype_runner_qparams}&{fake_device_qparams}"
# /switcher/set_shutter_position?id=ab1c2d&ip=1.2.3.4&key=18
set_position_uri2 = f"{webapp.ENDPOINT_SET_POSITION}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/set_shutter_position?id=ab1c2d&ip=1.2.3.4&index=0&token=zvVvd7JxtN7CgvkD1Psujw==
set_position_uri3 = f"{webapp.ENDPOINT_SET_POSITION}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_index_qparams}&{fake_device_token_qparams}"
# /switcher/turn_on_light?id=ab1c2d&ip=1.2.3.4&index=0&token=zvVvd7JxtN7CgvkD1Psujw==
turn_on_light_uri = f"{webapp.ENDPOINT_TURN_ON_LIGHT}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_index_qparams}&{fake_device_token_qparams}"
# /switcher/turn_off_light?id=ab1c2d&ip=1.2.3.4&index=0&token=zvVvd7JxtN7CgvkD1Psujw==
turn_off_light_uri = f"{webapp.ENDPOINT_TURN_OFF_LIGHT}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_index_qparams}&{fake_device_token_qparams}"
# /switcher/get_breeze_state?id=ab1c2d&ip=1.2.3.4
get_breeze_state_uri = f"{webapp.ENDPOINT_GET_BREEZE_STATE}?{fake_devicetype_breeze_qparams}&{fake_device_qparams}"
# /switcher/get_breeze_state?id=ab1c2d&ip=1.2.3.4&key=18
get_breeze_state_uri2 = f"{webapp.ENDPOINT_GET_BREEZE_STATE}?{fake_devicetype_breeze_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/get_shutter_state?id=ab1c2d&ip=1.2.3.4
get_shutter_state_uri = f"{webapp.ENDPOINT_GET_SHUTTER_STATE}?{fake_devicetype_runner_qparams}&{fake_device_qparams}"
# /switcher/get_shutter_state?id=ab1c2d&ip=1.2.3.4&key=18
get_shutter_state_uri2 = f"{webapp.ENDPOINT_GET_SHUTTER_STATE}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/get_shutter_state?id=ab1c2d&ip=1.2.3.4&index=0&token=zvVvd7JxtN7CgvkD1Psujw==
get_shutter_state_uri3 = f"{webapp.ENDPOINT_GET_SHUTTER_STATE}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_index_qparams}&{fake_device_token_qparams}"
# /switcher/get_light_state?id=ab1c2d&ip=1.2.3.4&index=0&token=zvVvd7JxtN7CgvkD1Psujw==
get_light_state_uri = f"{webapp.ENDPOINT_GET_LIGHT_STATE}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_index_qparams}&{fake_device_token_qparams}"
# /switcher/stop_shutter?id=ab1c2d&ip=1.2.3.4
get_stop_shutter_uri = f"{webapp.ENDPOINT_POST_STOP_SHUTTER}?{fake_devicetype_runner_qparams}&{fake_device_qparams}"
# /switcher/stop_shutter?id=ab1c2d&ip=1.2.3.4&key=18
get_stop_shutter_uri2 = f"{webapp.ENDPOINT_POST_STOP_SHUTTER}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"
# /switcher/stop_shutter?id=ab1c2d&ip=1.2.3.4&index=0&token=zvVvd7JxtN7CgvkD1Psujw==
get_stop_shutter_uri3 = f"{webapp.ENDPOINT_POST_STOP_SHUTTER}?{fake_devicetype_runner_qparams}&{fake_device_qparams}&{fake_device_index_qparams}&{fake_device_token_qparams}"
# /switcher/control_breeze_device?id=ab1c2d&ip=1.2.3.4
set_control_breeze_device_uri = f"{webapp.ENDPOINT_CONTROL_BREEZE_DEVICE}?{fake_devicetype_breeze_qparams}&{fake_device_qparams}"
# /switcher/control_breeze_device?id=ab1c2d&ip=1.2.3.4&key=18
set_control_breeze_device_uri2 = f"{webapp.ENDPOINT_CONTROL_BREEZE_DEVICE}?{fake_devicetype_breeze_qparams}&{fake_device_qparams}&{fake_device_login_key_qparams}"


@pytest_asyncio.fixture
async def api_client(aiohttp_client):
    # create application
    app = web.Application(middlewares=[webapp.error_middleware])
    app.add_routes(webapp.routes)
    # return client from application
    return await aiohttp_client(app)


@fixture
def api_connect():
    with patch(
        "aioswitcher.api.SwitcherApi.connect", return_value=AsyncMock()
    ) as connect:
        yield connect


@fixture
def api_disconnect():
    with patch("aioswitcher.api.SwitcherApi.disconnect") as disconnect:
        yield disconnect


@fixture
def response_serializer():
    with patch.object(
        webapp, "_serialize_object", return_value=fake_serialized_data
    ) as serializer:
        yield serializer


@fixture
def response_mock():
    return Mock()


@mark.parametrize(
    "api_uri",
    [
        (get_state_uri),
        (get_state_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.get_state")
async def test_successful_get_state_get_request(
    api_get_state,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub api_get_state to return mock response
    api_get_state.return_value = response_mock
    # send get request for get_state endpoint
    response = await api_client.get(api_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_get_state.assert_called_once_with()
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.get_state", side_effect=Exception("blabla"))
async def test_erroneous_get_state_get_request(
    api_get_state, response_serializer, api_connect, api_disconnect, api_client
):
    # send get request for get_state endpoint
    response = await api_client.get(get_state_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_get_state.assert_called_once_with()
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri, json_body, expected_values",
    [
        (turn_on_uri, dict(), (Command.ON, 0)),
        # &minutes=15
        (turn_on_uri, {webapp.KEY_MINUTES: "15"}, (Command.ON, 15)),
        (turn_on_uri2, dict(), (Command.ON, 0)),
        # &minutes=15
        (turn_on_uri2, {webapp.KEY_MINUTES: "15"}, (Command.ON, 15)),
    ],
)
@patch("aioswitcher.api.SwitcherApi.control_device")
async def test_successful_turn_on_post_request(
    api_control_device,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
    json_body,
    expected_values,
):
    # stub api_control_device to return mock response
    api_control_device.return_value = response_mock
    # send post request for turn_on endpoint
    response = await api_client.post(api_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    api_control_device.assert_called_once_with(expected_values[0], expected_values[1])
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.control_device", side_effect=Exception("blabla"))
async def test_erroneous_turn_on_post_request(
    api_control_device, response_serializer, api_connect, api_disconnect, api_client
):
    # send post request for turn_on endpoint
    response = await api_client.post(turn_on_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_control_device.assert_called_once_with(Command.ON, 0)
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri",
    [
        (turn_off_uri),
        (turn_off_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.control_device")
async def test_successful_turn_off_post_request(
    api_control_device,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub api_control_device to return mock response
    api_control_device.return_value = response_mock
    # send post request for turn_off endpoint
    response = await api_client.post(api_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_control_device.assert_called_once_with(Command.OFF)
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.control_device", side_effect=Exception("blabla"))
async def test_erroneous_turn_off_post_request(
    api_control_device, response_serializer, api_connect, api_disconnect, api_client
):
    # send post request for turn_off endpoint
    response = await api_client.post(turn_off_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_control_device.assert_called_once_with(Command.OFF)
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri",
    [
        (set_name_uri),
        (set_name_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.set_device_name")
async def test_successful_set_name_patch_request(
    api_set_device_name,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub api_set_device_name to return mock response
    api_set_device_name.return_value = response_mock
    # send patch request for set_name endpoint
    response = await api_client.patch(api_uri, json={webapp.KEY_NAME: "newFakedName"})
    # verify mocks calling
    api_connect.assert_called_once()
    api_set_device_name.assert_called_once_with("newFakedName")
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.set_device_name", side_effect=Exception("blabla"))
async def test_erroneous_set_name_patch_request(
    api_set_device_name, response_serializer, api_connect, api_disconnect, api_client
):
    # send patch request for set_name endpoint
    response = await api_client.patch(
        set_name_uri, json={webapp.KEY_NAME: "newFakedName"}
    )
    # verify mocks calling
    api_connect.assert_called_once()
    api_set_device_name.assert_called_once_with("newFakedName")
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@patch("aioswitcher.api.SwitcherApi.set_device_name")
async def test_set_name_faulty_no_name_patch_request(
    api_set_device_name, response_serializer, api_connect, api_disconnect, api_client
):
    # send patch request for set_name endpoint
    response = await api_client.patch(set_name_uri)
    # verify mocks calling
    api_connect.assert_not_called()
    api_set_device_name.assert_not_called()
    response_serializer.assert_not_called()
    api_disconnect.assert_not_called()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry(
        {"error": "failed to get name from body as json"}
    )


@mark.parametrize(
    "api_uri, json_body, expected_timedelta",
    [
        (set_auto_shutdown_uri, {webapp.KEY_HOURS: "2"}, timedelta(hours=2)),
        (
            set_auto_shutdown_uri,
            {webapp.KEY_HOURS: "2", webapp.KEY_MINUTES: "30"},
            timedelta(hours=2, minutes=30),
        ),
        (set_auto_shutdown_uri2, {webapp.KEY_HOURS: "2"}, timedelta(hours=2)),
        (
            set_auto_shutdown_uri2,
            {webapp.KEY_HOURS: "2", webapp.KEY_MINUTES: "30"},
            timedelta(hours=2, minutes=30),
        ),
    ],
)
@patch("aioswitcher.api.SwitcherApi.set_auto_shutdown")
async def test_successful_set_auto_shutdown_patch_request(
    api_set_auto_shutdown,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
    json_body,
    expected_timedelta,
):
    # stub api_set_auto_shutdown to return mock response
    api_set_auto_shutdown.return_value = response_mock
    # send patch request for set_auto_shutdown endpoint
    response = await api_client.patch(api_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    api_set_auto_shutdown.assert_called_once_with(expected_timedelta)
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.set_auto_shutdown")
async def test_set_auto_shutdown_with_faulty_no_hours_patch_request(
    api_set_auto_shutdown, response_serializer, api_connect, api_disconnect, api_client
):
    # send patch request for set_auto_shutdown endpoint
    response = await api_client.patch(set_auto_shutdown_uri)
    # verify mocks calling
    api_connect.assert_not_called()
    api_set_auto_shutdown.assert_not_called()
    response_serializer.assert_not_called()
    api_disconnect.assert_not_called()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry(
        {"error": "failed to get hours from body as json"}
    )


@patch(
    "aioswitcher.api.SwitcherApi.set_auto_shutdown",
    side_effect=Exception("blabla"),
)
async def test_erroneous_set_auto_shutdown_patch_request(
    api_set_auto_shutdown, response_serializer, api_connect, api_disconnect, api_client
):
    # send patch request for set_auto_shutdown endpoint
    response = await api_client.patch(set_auto_shutdown_uri, json={webapp.KEY_HOURS: 2})
    # verify mocks calling
    api_connect.assert_called_once()
    api_set_auto_shutdown.assert_called_once_with(timedelta(hours=2))
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri",
    [
        (get_schedules_uri),
        (get_schedules_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.get_schedules")
async def test_successful_get_schedules_get_request(
    api_get_schedules,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub mock response to return a set of two mock schedules
    schedule1 = schedule2 = Mock()
    response_mock.schedules = {schedule1, schedule2}
    # stub api_get_schedules to return mock response
    api_get_schedules.return_value = response_mock
    # send get request for get_schedules endpoint
    response = await api_client.get(api_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_get_schedules.assert_called_once_with()
    response_serializer.assert_called_once_with(schedule1)
    response_serializer.assert_called_once_with(schedule2)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.get_schedules", side_effect=Exception("blabla"))
async def test_erroneous_get_schedules_get_request(
    api_get_schedules, response_serializer, api_connect, api_disconnect, api_client
):
    # send get request for get_schedules endpoint
    response = await api_client.get(get_schedules_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    api_get_schedules.assert_called_once_with()
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri",
    [
        (delete_schedule_uri),
        (delete_schedule_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.delete_schedule")
async def test_successful_delete_schedule_delete_request(
    api_delete_schedule,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub api_delete_schedule to return mock response
    api_delete_schedule.return_value = response_mock
    # send delete request for delete_schedule endpoint
    response = await api_client.delete(api_uri, json={webapp.KEY_SCHEDULE: "5"})
    # verify mocks calling
    api_connect.assert_called_once()
    api_delete_schedule.assert_called_once_with("5")
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.delete_schedule")
async def test_delete_schedule_with_faulty_no_schedule_delete_request(
    api_delete_schedule, response_serializer, api_connect, api_disconnect, api_client
):
    # send delete request for delete_schedule endpoint
    response = await api_client.delete(delete_schedule_uri)
    # verify mocks calling
    api_connect.assert_not_called()
    api_delete_schedule.assert_not_called()
    response_serializer.assert_not_called()
    api_disconnect.assert_not_called()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry(
        {"error": "failed to get schedule from body as json"}
    )


@patch("aioswitcher.api.SwitcherApi.delete_schedule", side_effect=Exception("blabla"))
async def test_errorneous_delete_schedule_delete_request(
    api_delete_schedule, response_serializer, api_connect, api_disconnect, api_client
):
    # send delete request for delete_schedule endpoint
    response = await api_client.delete(
        delete_schedule_uri, json={webapp.KEY_SCHEDULE: "5"}
    )
    # verify mocks calling
    api_connect.assert_called_once()
    api_delete_schedule.assert_called_once_with("5")
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri, json_body, expected_values",
    [
        (
            create_schedule_uri,
            {webapp.KEY_START: "14:00", webapp.KEY_STOP: "15:30"},
            ("14:00", "15:30", set()),
        ),
        (
            create_schedule_uri,
            {
                webapp.KEY_START: "13:30",
                webapp.KEY_STOP: "14:00",
                webapp.KEY_DAYS: ["Sunday", "Monday", "Friday"],
            },
            ("13:30", "14:00", {Days.SUNDAY, Days.MONDAY, Days.FRIDAY}),
        ),
        (
            create_schedule_uri,
            {
                webapp.KEY_START: "18:15",
                webapp.KEY_STOP: "19:00",
                webapp.KEY_DAYS: [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
            },
            (
                "18:15",
                "19:00",
                {
                    Days.SUNDAY,
                    Days.MONDAY,
                    Days.TUESDAY,
                    Days.WEDNESDAY,
                    Days.THURSDAY,
                    Days.FRIDAY,
                    Days.SATURDAY,
                },
            ),
        ),
        (
            create_schedule_uri2,
            {webapp.KEY_START: "14:00", webapp.KEY_STOP: "15:30"},
            ("14:00", "15:30", set()),
        ),
        (
            create_schedule_uri2,
            {
                webapp.KEY_START: "13:30",
                webapp.KEY_STOP: "14:00",
                webapp.KEY_DAYS: ["Sunday", "Monday", "Friday"],
            },
            ("13:30", "14:00", {Days.SUNDAY, Days.MONDAY, Days.FRIDAY}),
        ),
        (
            create_schedule_uri2,
            {
                webapp.KEY_START: "18:15",
                webapp.KEY_STOP: "19:00",
                webapp.KEY_DAYS: [
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
            },
            (
                "18:15",
                "19:00",
                {
                    Days.SUNDAY,
                    Days.MONDAY,
                    Days.TUESDAY,
                    Days.WEDNESDAY,
                    Days.THURSDAY,
                    Days.FRIDAY,
                    Days.SATURDAY,
                },
            ),
        ),
    ],
)
@patch("aioswitcher.api.SwitcherApi.create_schedule")
async def test_successful_create_schedule_post_request(
    api_create_schedule,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
    json_body,
    expected_values,
):
    # stub api_delete_schedule to return mock response
    api_create_schedule.return_value = response_mock
    # send post request for create schedule endpoint
    response = await api_client.post(api_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    api_create_schedule.assert_called_once_with(
        expected_values[0], expected_values[1], expected_values[2]
    )
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@mark.parametrize(
    "missing_key_json_body,expected_error_msg",
    [
        ({webapp.KEY_START: "18:15"}, "'stop'"),
        ({webapp.KEY_STOP: "19:00"}, "'start'"),
    ],
)
@patch("aioswitcher.api.SwitcherApi.create_schedule")
async def test_create_schedule_with_faulty_missing_key_post_request(
    api_create_schedule,
    response_serializer,
    api_connect,
    api_disconnect,
    api_client,
    missing_key_json_body,
    expected_error_msg,
):
    # send post request for create schedule endpoint
    response = await api_client.post(create_schedule_uri, json=missing_key_json_body)
    # verify mocks calling
    api_connect.assert_not_called()
    api_create_schedule.assert_not_called()
    response_serializer.assert_not_called()
    api_disconnect.assert_not_called()
    # assert expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": expected_error_msg})


@patch("aioswitcher.api.SwitcherApi.create_schedule", side_effect=Exception("blabla"))
async def test_errorneous_create_schedule(
    api_create_schedule, response_serializer, api_connect, api_disconnect, api_client
):
    json_body = {webapp.KEY_START: "11:00", webapp.KEY_STOP: "11:15"}
    # send post request for create schedule endpoint
    response = await api_client.post(create_schedule_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    api_create_schedule.assert_called_once_with("11:00", "11:15", set())
    response_serializer.assert_not_called()
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(500)
    assert_that(await response.json()).contains_entry({"error": "blabla"})


@mark.parametrize(
    "api_uri, json_body, expected_values",
    [
        (
            set_position_uri,
            {webapp.KEY_POSITION: "25"},
            (
                25,
                0,
            ),
        ),
        (
            set_position_uri2,
            {webapp.KEY_POSITION: "25"},
            (
                25,
                0,
            ),
        ),
        (
            set_position_uri3,
            {webapp.KEY_POSITION: "25"},
            (
                25,
                0,
            ),
        ),
    ],
)
@patch("aioswitcher.api.SwitcherApi.set_position")
async def test_set_position_post_request(
    set_position,
    response_serializer,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
    json_body,
    expected_values,
):
    # stub set_position to return mock response
    set_position.return_value = response_mock
    # send post request for create schedule endpoint
    response = await api_client.post(api_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    set_position.assert_called_once_with(expected_values[0], expected_values[1])
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@mark.parametrize(
    "api_uri, json_body, expected_values",
    [
        (turn_on_light_uri, dict(), (DeviceState.ON, 0)),
    ],
)
@patch("aioswitcher.api.SwitcherApi.set_light")
async def test_successful_turn_on_light_post_request(
    set_light,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
    json_body,
    expected_values,
):
    # stub api_turn_on_light to return mock response
    set_light.return_value = response_mock
    # send post request for turn_on_light endpoint
    response = await api_client.post(api_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    set_light.assert_called_once_with(expected_values[0], expected_values[1])
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@mark.parametrize(
    "api_uri, json_body, expected_values",
    [
        (turn_off_light_uri, dict(), (DeviceState.OFF, 0)),
    ],
)
@patch("aioswitcher.api.SwitcherApi.set_light")
async def test_successful_turn_off_light_post_request(
    set_light,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
    json_body,
    expected_values,
):
    # stub api_turn_off_light to return mock response
    set_light.return_value = response_mock
    # send post request for turn_off_light endpoint
    response = await api_client.post(api_uri, json=json_body)
    # verify mocks calling
    api_connect.assert_called_once()
    set_light.assert_called_once_with(expected_values[0], expected_values[1])
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@mark.parametrize(
    "api_uri",
    [
        (get_breeze_state_uri),
        (get_breeze_state_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.get_breeze_state")
async def test_successful_get_breeze_state_get_request(
    get_breeze_state,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub mock response to return a set mocked state
    state = Mock()
    response_mock = state
    # stub api_get_schedules to return mock response
    get_breeze_state.return_value = response_mock
    # send get request for get_schedules endpoint
    response = await api_client.get(api_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    get_breeze_state.assert_called_once_with()
    response_serializer.assert_called_once_with(state)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(fake_serialized_data).is_subset_of(await response.json())


@mark.parametrize(
    "api_uri",
    [
        (get_shutter_state_uri),
        (get_shutter_state_uri2),
        (get_shutter_state_uri3),
    ],
)
@patch("aioswitcher.api.SwitcherApi.get_shutter_state")
async def test_successful_get_shutter_state_get_request(
    get_shutter_state,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub mock response to return a set mocked state
    state = Mock()
    response_mock = state
    # stub api_get_schedules to return mock response
    get_shutter_state.return_value = response_mock
    # send get request for get_schedules endpoint
    response = await api_client.get(api_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    get_shutter_state.assert_called_once_with(0)
    response_serializer.assert_called_once_with(state)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(fake_serialized_data).is_subset_of(await response.json())


@mark.parametrize(
    "api_uri",
    [
        (get_stop_shutter_uri),
        (get_stop_shutter_uri2),
        (get_stop_shutter_uri3),
    ],
)
@patch("aioswitcher.api.SwitcherApi.stop_shutter")
async def test_stop_shutter_post_request(
    stop_shutter, response_serializer, api_connect, api_disconnect, api_client, api_uri
):
    # stub set_position to return mock response
    stop_shutter.return_value = response_mock
    # send post request for create schedule endpoint
    response = await api_client.post(api_uri, json={})
    # verify mocks calling
    api_connect.assert_called_once()
    stop_shutter.assert_called_once_with(0)
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@mark.parametrize(
    "api_uri",
    [
        (set_control_breeze_device_uri),
        (set_control_breeze_device_uri2),
    ],
)
@patch("aioswitcher.api.SwitcherApi.control_breeze_device")
async def test_control_breeze_device_patch_request(
    control_breeze_device,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub api_set_device_name to return mock response
    control_breeze_device.return_value = response_mock
    # send patch request for control_breeze_device endpoint
    response = await api_client.patch(
        api_uri,
        json={
            webapp.KEY_DEVICE_STATE: "on",
            webapp.KEY_THERMOSTAT_MODE: "auto",
            webapp.KEY_TARGET_TEMP: 25,
            webapp.KEY_FAN_LEVEL: "low",
            webapp.KEY_THERMOSTAT_SWING: "off",
            webapp.KEY_CURRENT_DEVICE_STATE: "off",
            webapp.KEY_REMOTE_ID: "AUX07001",
        },
    )
    # verify mocks calling
    api_connect.assert_called_once()
    control_breeze_device.assert_called_once()
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.control_breeze_device")
async def test_control_breeze_device_patch_request_only_device_state(
    control_breeze_device,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
):
    # stub api_set_device_name to return mock response
    control_breeze_device.return_value = response_mock
    # send patch request for control_breeze_device endpoint
    response = await api_client.patch(
        set_control_breeze_device_uri,
        json={webapp.KEY_DEVICE_STATE: "on", webapp.KEY_REMOTE_ID: "AUX07001"},
    )
    # verify mocks calling
    api_connect.assert_called_once()
    control_breeze_device.assert_called_once()
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@patch("aioswitcher.api.SwitcherApi.control_breeze_device")
async def test_control_breeze_device_patch_request_only_target_temp(
    control_breeze_device,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
):
    # stub api_set_device_name to return mock response
    control_breeze_device.return_value = response_mock
    # send patch request for control_breeze_device endpoint
    response = await api_client.patch(
        set_control_breeze_device_uri,
        json={webapp.KEY_TARGET_TEMP: 25, webapp.KEY_REMOTE_ID: "AUX07001"},
    )
    # verify mocks calling
    api_connect.assert_called_once()
    control_breeze_device.assert_called_once()
    response_serializer.assert_called_once_with(response_mock)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(await response.json()).contains_entry(fake_serialized_data)


@mark.parametrize(
    "api_uri",
    [
        (get_light_state_uri),
    ],
)
@patch("aioswitcher.api.SwitcherApi.get_light_state")
async def test_successful_get_light_state_get_request(
    get_light_state,
    response_serializer,
    response_mock,
    api_connect,
    api_disconnect,
    api_client,
    api_uri,
):
    # stub mock response to return a set mocked state
    state = Mock()
    response_mock = state
    # stub api_get_light_state to return mock response
    get_light_state.return_value = response_mock
    # send get request for get_light_state endpoint
    response = await api_client.get(api_uri)
    # verify mocks calling
    api_connect.assert_called_once()
    get_light_state.assert_called_once_with(0)
    response_serializer.assert_called_once_with(state)
    api_disconnect.assert_called_once()
    # assert the expected response
    assert_that(response.status).is_equal_to(200)
    assert_that(fake_serialized_data).is_subset_of(await response.json())
