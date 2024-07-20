"""
A module that provides high-level functions to perform actions on UAVs.
"""

import logging
import time
from copy import deepcopy
from typing import Optional, TypeVar, Union

from pymavlink.dialects.v20.ardupilotmega import (
    MAV_AUTOPILOT_INVALID,
    MAV_CMD_COMPONENT_ARM_DISARM,
    MAV_CMD_DO_REPOSITION,
    MAV_CMD_DO_SET_HOME,
    MAV_CMD_DO_SET_SERVO,
    MAV_CMD_REQUEST_MESSAGE,
    MAV_DATA_STREAM_ALL,
    MAV_DATA_STREAM_EXTENDED_STATUS,
    MAV_DATA_STREAM_POSITION,
    MAV_DATA_STREAM_RAW_CONTROLLER,
    MAV_DATA_STREAM_RAW_SENSORS,
    MAV_DATA_STREAM_RC_CHANNELS,
    MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
    MAV_MODE_FLAG_SAFETY_ARMED,
    MAV_STATE_ACTIVE,
    MAV_TYPE_ONBOARD_CONTROLLER,
    MAVLINK_MSG_ID_HOME_POSITION,
    MAVLink_encapsulated_data_message,
    MAVLink_heartbeat_message,
    MAVLink_message,
    MAVLink_mission_request_list_message,
    MAVLink_play_tune_message,
    MAVLink_request_data_stream_message,
)

from albatros.enums import ConnectionType
from albatros.telem import ComponentAddress
from albatros.telem.drivers import (
    DirectConnectionDriver,
    RedisConnectionDriver,
    TelemDriver,
    TestDriver,
)

from .enums import (
    CommandResult,
    CopterFlightModes,
    FixType,
    MissionResult,
    MissionType,
    PlaneFlightModes,
)
from .nav.position import PositionGPS, PositionNED, ned2geo
from .outgoing.commands import (
    get_command_int_message,
    get_command_long_message,
    get_mission_clear_message,
)
from .outgoing.param_messages import (
    get_param_request_list_message,
    get_param_request_read_message,
    get_param_set_message,
)
from .telem.message_models import (
    CommandACK,
    EncapsulatedData,
    Heartbeat,
    HomePosition,
    MavMessage,
    MissionACK,
    MissionCount,
    MissionCurrent,
    NavControllerOutput,
    ParamValue,
)
from .telem.uav_data import UAVData

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="MavMessage")


TIMEOUT_S = 0.5
HEARTBEAT_TIMEOUT_S = 5
CHECK_PERIOD_S = 0.01

MAX_DATA_SIZE_BYTES = 252
UINT16_MAX = 0xFFFF
UINT32_MAX = 0xFFFFFFFF


class UAV:
    """Provides generic UAV activities that are common to drones and planes."""

    def __init__(
        self,
        uav_addr: ComponentAddress = ComponentAddress(system_id=1, component_id=1),
        my_addr: ComponentAddress = ComponentAddress(system_id=1, component_id=191),
        connection_type: ConnectionType = ConnectionType.DIRECT,
        device: Optional[str] = "udpin:0.0.0.0:14550",
        baud_rate: Optional[int] = 115200,
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> None:
        self._uav_addr = uav_addr
        self._my_addr = my_addr
        self._driver: TelemDriver
        self.data = UAVData(uav_addr)

        if connection_type == ConnectionType.DIRECT:
            if not device or not baud_rate:
                raise ValueError
            self._driver = DirectConnectionDriver(
                self._my_addr, self.data, device, baud_rate
            )

        elif connection_type == ConnectionType.REDIS:
            if not host or not port:
                raise ValueError
            self._driver = RedisConnectionDriver(self._my_addr, self.data, host, port)

        elif connection_type == ConnectionType.TEST:
            self._driver = TestDriver(self._my_addr, self.data)
        else:
            raise NotImplementedError

        if not self._driver.make_connection():
            raise TimeoutError

        self.request_data_stream(MAV_DATA_STREAM_ALL, 1)
        self.request_data_stream(MAV_DATA_STREAM_POSITION, 10)
        self.request_data_stream(MAV_DATA_STREAM_RAW_CONTROLLER, 10)
        self.request_data_stream(MAV_DATA_STREAM_RAW_SENSORS, 2)
        self.request_data_stream(MAV_DATA_STREAM_EXTENDED_STATUS, 2)
        self.request_data_stream(MAV_DATA_STREAM_RC_CHANNELS, 2)

    def get_flight_mode(self) -> Union[PlaneFlightModes, CopterFlightModes]:
        raise NotImplementedError

    # ----- GPS related methods -------

    def get_gps_fix_type(self) -> FixType:
        """Get GPS fix type."""
        if self.data.gps_raw_int.less_than(time_ms=1_000):
            return self.data.gps_raw_int.fix_type
        return FixType.NO_GPS

    def get_gps_hdop(self) -> float:
        """Get GPS HDOP horizontal dilution of position."""
        if self.data.gps_raw_int.less_than(time_ms=1_000):
            return self.data.gps_raw_int.eph / 100.0
        return UINT16_MAX / 100.0

    def get_visible_sats_count(self) -> int:
        """Number of satellites visible."""
        if self.data.gps_raw_int.less_than(time_ms=1_000):
            return self.data.gps_raw_int.satellites_visible
        return 0

    def get_position_uncertainty(self) -> float:
        """Position uncertainty.

        Returns:
            Position uncertainty in meters. `UINT16_MAX / 1000.0` if unknown.
        """
        if self.data.gps_raw_int.less_than(time_ms=1_000):
            return self.data.gps_raw_int.h_acc / 1_000.0
        return UINT32_MAX / 1_000.0

    def get_last_known_gps_position(self) -> PositionGPS:
        """Get last known raw position from GPS.

        Returns:
            Latitude, longitude and altitude (MSL). Positive for up.
        """
        return PositionGPS.from_int(
            self.data.gps_raw_int.lat,
            self.data.gps_raw_int.lon,
            self.data.gps_raw_int.alt,
        )

    def wait_gps_fix(self) -> None:
        """Wait for GPS 3D fix.

        Fix type must be at least `3D_FIX`.
        """
        while (
            self.get_gps_fix_type() < FixType.GPS_3D_FIX
            or self.get_last_known_gps_position().lat_int == 0
            or self.get_last_known_gps_position().lon_int == 0
        ):
            time.sleep(CHECK_PERIOD_S)

    # ------- Telem waiting related methods -------

    def wait_heartbeat(self) -> Heartbeat:
        """Wait for next heartbeat message.

        Raises:
            `TimeoutError`: if there is no `Heartbeat` for 5 seconds.
        """
        clock_start = time.time()
        while time.time() - clock_start < HEARTBEAT_TIMEOUT_S:
            time_dif = time.time() - self.data.heartbeat.timestamp_ms / 1_000.0

            if time_dif < CHECK_PERIOD_S:
                heartbeat = deepcopy(self.data.heartbeat)
                self.data.heartbeat.timestamp_ms = 0
                return heartbeat
            time.sleep(CHECK_PERIOD_S)

        raise TimeoutError

    def wait_command_ack(self) -> CommandACK:
        """Wait for command execution status.

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        return self.wait_message(CommandACK())

    def wait_encapsulated_data(
        self, timeout_s: Optional[float] = None
    ) -> EncapsulatedData:
        """Wait for next encapsulated data."""

        return self.data.encapsulated_data.get(timeout=timeout_s)

    def wait_message(self, message_obj: T) -> T:
        """Wait for next message.

        Parameters:
            message_obj: object of the message to wait for.

        Returns:
            T: requested message object.

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        if not hasattr(self.data, message_obj.get_object_name()):
            raise AttributeError(
                f"UAVData has no attribute with class name {message_obj.__name__}"  # type: ignore
            )

        clock_start = time.time()
        while time.time() - clock_start < TIMEOUT_S:
            msg: MavMessage = getattr(self.data, message_obj.get_object_name())
            time_since_last_message = time.time() - msg.timestamp_ms / 1_000.0

            if time_since_last_message < CHECK_PERIOD_S:
                coppied_msg = deepcopy(msg)
                msg.timestamp_ms = 0
                setattr(self, message_obj.get_object_name(), msg)
                return coppied_msg  # type: ignore
            time.sleep(CHECK_PERIOD_S)

        raise TimeoutError

    # ------- Arming related methods -------

    def is_armed(self) -> bool:
        """Check whether the UAV is armed.

        Returns:
            `True` if vehicle is armed.
        """
        armed_flag = self.data.heartbeat.base_mode & MAV_MODE_FLAG_SAFETY_ARMED
        return bool(armed_flag)

    def arm(self) -> bool:
        """Arms motors."""
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_COMPONENT_ARM_DISARM,
            param1=1,
        )

        self._driver.send(msg)
        logger.info("Arm command sent.")
        self.wait_heartbeat()

        return self.is_armed()

    def disarm(self) -> bool:
        """Disarms motors."""
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_COMPONENT_ARM_DISARM,
            param1=0,
        )

        self._driver.send(msg)
        logger.info("Disarm command sent.")

        try:
            return self.wait_command_ack().result == CommandResult.ACCEPTED
        except TimeoutError:
            return False

    # ------- Parameters related methods -------

    def fetch_one_param(self, param_id: str) -> ParamValue:
        """Fetch single parameter from UAV

        Parameters:
            param_id: string that identifies the parameter.
        """
        msg = get_param_request_read_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            param_id=param_id.encode("ascii"),
            param_index=-1,
        )

        self._driver.send(msg)
        logger.debug("Param request read message sent.")
        return self.wait_message(ParamValue())

    def request_all_parameters(self) -> None:
        """Send a command to request values of every parameter from the uav.
        If you need specific parameters, you should use request_one_parameter instead
        """
        msg = get_param_request_list_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
        )

        self._driver.send(msg)
        logger.debug("Param request list message sent.")

    def set_parameter(self, param_id: str, new_value: float) -> bool:
        """Set a parameter to the specified value.

        Parameters:
            param_id: string that identifies the parameter.
            new_value: new parameter value.
        """
        msg = get_param_set_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            param_id=param_id.encode("ascii"),
            param_value=new_value,
        )

        self._driver.send(msg)
        logger.debug("Param set message sent.")
        return abs(self.wait_message(ParamValue()).param_value - new_value) < 0.0001

    # ------- Mission protocol related methods -------

    def get_mission_status(self) -> MissionCurrent:
        """Get loaded mission status."""
        return self.data.mission_current

    def get_reached_mission_item(self) -> int:
        """Get last reached mission item id."""
        return self.data.mission_item_reached.seq

    def get_mission_ack(self) -> MissionACK:
        """Get uploaded mission status code.

        Returns:
            MisionACK object containing a status code.
        """
        # try:
        #     return self.wait_message(MissionACK()).type
        # except TimeoutError:
        #     return MissionResult.ERROR

        clock_start = time.time()
        while True:
            time_dif = time.time() * 1000 - self.data.mission_ack.timestamp_ms
            if time_dif < 100:
                self.data.mission_ack.timestamp_ms = 0
                return self.data.mission_ack
            time.sleep(0.1)
            if time.time() - clock_start > 0.250:
                raise TimeoutError

    def get_mission_items_count(
        self, mission_type: MissionType = MissionType.MISSION
    ) -> int:
        """Get mission items count.

        Args:
            mission_type: Mission type

        Returns:
            mission items count or `-1` if `TimeoutError`
        """
        msg = MAVLink_mission_request_list_message(
            self._uav_addr.system_id, self._uav_addr.component_id, mission_type.value
        )

        self._driver.send(msg)
        logger.debug("MISSION_REQUEST_LIST message sent")

        try:
            return self.wait_message(MissionCount()).count

        except TimeoutError:
            return -1

    def clear_mission(self) -> bool:
        """Clear uploaded mission."""
        msg = get_mission_clear_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
        )

        self._driver.send(msg)
        logger.info("mission_clear_all message sent.")

        try:
            if self.get_mission_ack().type == MissionResult.ACCEPTED:
                self._mission_count = 0
                return True
            return False
        except TimeoutError:
            return False

    # ------- Other methods -------

    def set_servo(self, instance_number: int, pwm: int) -> bool:
        """Set a servo to a desired `PWM` value.

        Parameters:
            instance_number: servo number.
            pwm: `PWM` value to set.
        """
        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_DO_SET_SERVO,
            param1=instance_number,
            param2=pwm,
        )

        self._driver.send(msg)
        logger.info("Set servo command sent.")

        try:
            return self.wait_command_ack().result == CommandResult.ACCEPTED
        except TimeoutError:
            return False

    def fly_to_gps_position(self, lat: float, lon: float, alt_m: float) -> bool:
        """Reposition the vehicle to a specific WGS84 global position.

        Parameters:
            lat: Latitude of the target point.
            lon: Longitude of the target point.
            alt_m: Altitude of the target point in meters.

        Works only in `Guided` mode.
        """
        wp = PositionGPS(lat, lon, alt_m)
        msg = get_command_int_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_DO_REPOSITION,
            x=wp.lat_int,
            y=wp.lon_int,
            z=wp.alt_m,
        )

        self._driver.send(msg)
        logger.info("Flight to point command sent.")

        try:
            return self.wait_command_ack().result == CommandResult.ACCEPTED
        except TimeoutError:
            return False

    def get_corrected_position(self) -> PositionGPS:
        """Get the vehicle position corrected for the distance
        the vehicle traveled after the message was received.
        """
        movement_time = (
            time.time() - self.data.global_position_int.timestamp_ms / 1_000.0
        )
        north_shift = movement_time * self.data.global_position_int.vx / 100.0
        east_shift = movement_time * self.data.global_position_int.vy / 100.0
        z_shift = movement_time * self.data.global_position_int.vz / 100.0
        corrected_altitude = (
            z_shift + self.data.global_position_int.relative_alt / 1_000.0
        )
        last_known_position = PositionGPS.from_int(
            self.data.global_position_int.lat,
            self.data.global_position_int.lon,
        )
        shift_vector = PositionNED(north_shift, east_shift, corrected_altitude)
        return ned2geo(last_known_position, shift_vector)

    def request_data_stream(self, stream_id: int, message_rate_hz: int) -> None:
        """Request a messages stream.

        Parameters:
            stream_id: ID of the requested data stream,
            message_rate_hz: requested message rate in Hz,
        """
        msg = MAVLink_request_data_stream_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            req_stream_id=stream_id,
            req_message_rate=message_rate_hz,
            start_stop=1,
        )
        logger.debug("Data stream requested.")
        self._driver.send(msg)

    def request_message(self, message_id: int) -> CommandResult:
        """Request single message from UAV.
        Message will be send to requester address.

        Parameters:
            message_id: ID of requested message.
        """
        msg = get_command_long_message(
            self._uav_addr.system_id,
            self._uav_addr.component_id,
            MAV_CMD_REQUEST_MESSAGE,
            param1=message_id,
            param7=1,
        )

        self._driver.send(msg)
        logger.debug("Message requested.")
        return self.wait_command_ack().result

    def fetch_home_position(self) -> PositionGPS:
        """Fetch home location"""
        if self.request_message(MAVLINK_MSG_ID_HOME_POSITION) != CommandResult.ACCEPTED:
            raise RuntimeError

        response = self.wait_message(HomePosition())
        return PositionGPS(response.latitude, response.longitude, response.altitude)

    def send_raw_mavlink_message(self, msg: MAVLink_message) -> None:
        """Send raw MAVLink message.

        Parameters:
            msg: raw MAVLink messae to send.
        """
        self._driver.send(msg)

    def send_encapsulated_data(self, data: bytes, seq: int = 0) -> None:
        """Send encapsulated data to broadcast.

        Parameters:
            data: data bytes.
            seq: sequence number (starting with 0 on every transmission).
        """

        data_size_bytes = len(data)
        if data_size_bytes > MAX_DATA_SIZE_BYTES:
            raise ValueError(f"Max allowed data size is {MAX_DATA_SIZE_BYTES}")

        bytes_to_send = bytes([data_size_bytes])
        bytes_to_send += data
        bytes_to_send += bytes([0x42]) * (MAX_DATA_SIZE_BYTES - data_size_bytes)
        msg = MAVLink_encapsulated_data_message(seq, bytes_to_send)

        logger.debug("Encapsulated data message sent.")
        self._driver.send(msg)

    def fetch_wp_dist(self) -> int:
        """Fetch distance to the next waypoint.

        Returns:
            distance to next waypoint in meters.

        Raises:
            `TimeoutError`: if the response time is exceeded.
        """
        return self.wait_message(NavControllerOutput()).wp_dist

    def play_tune(self, tune: str, tune2: str = "") -> bool:
        """Play a tune on the UAV. Tunes have to be in the MML format

        Args:
            tune: The first tune to be played, limited to 30 characters.
            tune2: The second tune to be played, limited to 230 characters. Defaults to an empty string.

        Returns:
            bool: True if the tune was played successfully, False otherwise.
        """
        if len(tune) > 30 or len(tune2) > 230:
            logger.error("Tune too long")
            return False

        msg = MAVLink_play_tune_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            tune=tune.encode("ascii"),
            tune2=tune2.encode("ascii"),
        )
        self.send_raw_mavlink_message(msg)

        self._driver.send(msg)
        logger.debug("Tune played.")
        return True

    def send_heartbeat(
        self,
        type: int = MAV_TYPE_ONBOARD_CONTROLLER,
        autopilot: int = MAV_AUTOPILOT_INVALID,
        base_mode: int = MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        custom_mode: int = 0,
        system_status: int = MAV_STATE_ACTIVE,
        mavlink_version: int = 2,
    ) -> None:
        """Sends a heartbeat message to indicate the system's presence.

        Args:
            type: Type of device. Defaults to `MAV_TYPE_ONBOARD_CONTROLLER`.
            autopilot: Type of autopilot. Defaults to `MAV_AUTOPILOT_INVALID` that means component is not flight controller.
            base_mode: System mode bitmap. Defaults to `MAV_MODE_FLAG_CUSTOM_MODE_ENABLED`.
            custom_mode: A bitfield for use for autopilot-specific flags. Defaults to 0.
            system_status: System status flag. Defaults to `MAV_STATE_ACTIVE`.
            mavlink_version: MAVLink version. Defaults to 2.

        Returns:
            None
        """
        msg = MAVLink_heartbeat_message(
            type, autopilot, base_mode, custom_mode, system_status, mavlink_version
        )

        self.send_raw_mavlink_message(msg)

        self._driver.send(msg)
        logger.debug("Heartbeat sent.")

    def set_home_position(
        self, lat: float, lon: float, alt_m: float = 0, wait_ack: bool = True
    ) -> bool:
        """Sets the home position to either the current position or a specified position.

        The home position is the default position that the system will return to and land on.
        This position is set automatically by the system during takeoff, but it can also be
        set manually using this method.

        Args:
            lat: Latitude of the home position.
            lon: Longitude of the home position.
            alt_m: Altitude of the home position in meters. Defaults to 0.
            wait_ack: Whether to wait for an acknowledgment. Defaults to True.

        Returns:
            bool: True if the command is acknowledged and accepted, False if a TimeoutError occurs or
            the command is not accepted.
        """

        msg = get_command_long_message(
            target_system=self._uav_addr.system_id,
            target_component=self._uav_addr.component_id,
            command=MAV_CMD_DO_SET_HOME,
            param5=lat,
            param6=lon,
            param7=alt_m,
        )

        self._driver.send(msg)
        logger.debug("Set home position command sent.")

        if not wait_ack:
            return True

        try:
            return self.wait_command_ack().result == CommandResult.ACCEPTED
        except TimeoutError:
            return False
