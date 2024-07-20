import re
import time

from pydantic import BaseModel

from albatros.enums import (
    CommandResult,
    FixType,
    MissionResult,
    MissionState,
    MissionType,
)


class MavMessage(BaseModel):
    """MAVLink message super class."""

    mavpackettype: str = "UNKNOWN"
    """Message name."""

    timestamp_ms: int = -1
    """Received timestamp (ms)."""

    @classmethod
    def get_object_name(cls) -> str:
        # Use regular expressions to find uppercase letters and add underscores before them
        # Also, convert the string to lowercase
        snake_string = re.sub(r"([A-Z]+)", r"_\1", cls.__name__).lower()

        # Remove leading underscores if any
        snake_string = snake_string.lstrip("_")

        return snake_string

    def less_than(self, time_ms: int) -> bool:
        """Check if the message is newer than the given time."""
        if int(time.time() * 1_000) - self.timestamp_ms < time_ms:
            return True
        return False


class Heartbeat(MavMessage):
    """The heartbeat message shows that a system or component is present and responding.
    The type and autopilot fields (along with the message component id), allow the receiving system
    to treat further messages from this system appropriately (e.g. by laying out the user interface based on the autopilot).
    """

    type: int = 0
    """Vehicle or component type. For a flight controller component the vehicle type (quadrotor, helicopter, etc.).
    For other components the component type (e.g. camera, gimbal, etc.).
    This should be used in preference to component id for identifying the component type.
    """
    autopilot: int = 0
    """Autopilot type / class. Use MAV_AUTOPILOT_INVALID for components that are not flight controllers."""
    base_mode: int = 0
    """System mode bitmap."""
    custom_mode: int = 100
    """A bitfield for use for autopilot-specific flags."""
    system_status: int = 0
    """System status flag."""
    mavlink_version: int = 0
    """MAVLink version, not writable by user, gets added by protocol because of magic data type: uint8_t_mavlink_version."""


class GlobalPositionInt(MavMessage):
    """The filtered global position (e.g. fused GPS and accelerometers).
    The position is in GPS-frame (right-handed, Z-up). It is designed as scaled integer
    message since the resolution of float is not sufficient.
    """

    time_boot_ms: int = 0
    """Time since system boot (ms)."""
    lat: int = 0
    """Latitude, expressed (degE7)."""
    lon: int = 0
    """Longitude, expressed (degE7)."""
    alt: int = 0
    """Altitude (MSL). Note that virtually all GPS modules provide both WGS84 and MSL (mm)."""
    relative_alt: int = 0
    """Altitude above ground (mm)."""
    vx: int = 0
    vy: int = 0
    vz: int = 0
    hdg: int = 0


class SysStatus(MavMessage):
    """The general system state."""

    onboard_control_sensors_present: int = 0
    """Bitmap showing which onboard controllers and sensors are present.
    Value of 0: not present. Value of 1: present.
    """
    onboard_control_sensors_enabled: int = 0
    """Bitmap showing which onboard controllers and sensors are enabled.
    Value of 0: not enabled. Value of 1: enabled.
    """
    onboard_control_sensors_health: int = 0
    """Bitmap showing which onboard controllers and sensors have an error (or are operational).
    Value of 0: error. Value of 1: healthy.
    """
    load: int = 0
    """Maximum usage in percent of the mainloop time. Values: [0-1000]."""
    voltage_battery: int = 0
    """Battery voltage, UINT16_MAX: Voltage not sent by autopilot."""
    current_battery: int = 0
    """Battery current, -1: Current not sent by autopilot."""
    battery_remaining: int = 0
    """Battery energy remaining, -1: Battery remaining energy not sent by autopilot."""
    drop_rate_comm: int = 0
    """Communication drop rate, (UART, I2C, SPI, CAN), dropped packets on all links
    (packets that were corrupted on reception on the MAV).
    """


class GPSRawInt(MavMessage):
    """The global position, as returned by the Global Positioning System (GPS).
    This is NOT the global position estimate of the system, but rather a RAW sensor value.
    """

    time_usec: int = 0
    """Timestamp (UNIX Epoch time or time since system boot)."""
    fix_type: FixType = FixType.NO_GPS
    """GPS fix type."""
    lat: int = 0
    """Latitude (WGS84)"""
    lon: int = 0
    """Longitude (WGS84)"""
    alt: int = 0
    """Altitude (MSL). Positive for up. Note that virtually all GPS modules provide the MSL altitude in addition to the WGS84 altitude."""
    eph: int = 0
    """GPS HDOP horizontal dilution of position (unitless * 100). If unknown, set to: UINT16_MAX."""
    epv: int = 0
    """GPS VDOP vertical dilution of position (unitless * 100). If unknown, set to: UINT16_MAX."""
    vel: int = 0
    """GPS ground speed. If unknown, set to: UINT16_MAX."""
    cog: int = 0
    """Course over ground (NOT heading, but direction of movement) in degrees * 100, 0.0..359.99 degrees.
    If unknown, set to: UINT16_MAX
    """
    satellites_visible: int = 0
    """Number of satellites visible. If unknown, set to UINT8_MAX."""
    alt_ellipsoid: int = 0
    """Altitude (above WGS84, EGM96 ellipsoid). Positive for up."""
    h_acc: int = 0
    """Position uncertainty."""
    v_acc: int = 0
    """Altitude uncertainty."""
    vel_acc: int = 0
    """Speed uncertainty."""
    hdg_acc: int = 0
    """Heading / track uncertainty"""
    yaw: int = 0
    """Yaw in earth frame from north. Use 0 if this GPS does not provide yaw.
    Use UINT16_MAX if this GPS is configured to provide yaw and is currently unable to provide it. Use 36000 for north.
    """


class GPSStatus(MavMessage):
    """The positioning status, as reported by GPS. This message is intended
    to display status information about each satellite visible to the receiver.
    This message can contain information for up to 20 satellites.
    """

    satellites_visible: int = 0
    """Number of satellites visible."""
    satellite_prn: int = 0
    """Global satellite ID."""
    satellite_used: int = 0
    "0: Satellite not used, 1: used for localization."
    satellite_elevation: int = 0
    """Elevation (0: right on top of receiver, 90: on the horizon) of satellite."""
    satellite_azimuth: int = 0
    """Direction of satellite, 0: 0 deg, 255: 360 deg."""
    satellite_snr: int = 0
    """Signal to noise ratio of satellite."""


class Attitude(MavMessage):
    """The attitude in the aeronautical frame (right-handed, Z-down, Y-right, X-front, ZYX, intrinsic)."""

    time_boot_ms: int = 0
    """Time since system boot (ms)."""
    roll: float = 0
    """Roll angle (-pi..+pi)."""
    pitch: float = 0
    """Pitch angle (-pi..+pi)."""
    yaw: float = 0
    """Yaw angle (-pi..+pi)."""
    rollspeed: float = 0
    """Roll angular speed."""
    pitchspeed: float = 0
    """Pitch angular speed."""
    yawspeed: float = 0
    """Yaw angular speed."""


class RcChannelsRaw(MavMessage):
    """The RAW values of the RC channels received. The standard PPM modulation
    is as follows: 1000 microseconds: 0%, 2000 microseconds: 100%.
    """

    time_boot_ms: int = 0
    """Time since system boot (ms)."""
    port: int = 0
    """Servo output port (set of 8 outputs = 1 port).
    Flight stacks running on Pixhawk should use: 0 = MAIN, 1 = AUX.
    """
    chan1_raw: int = 0
    """RC channel 1 value."""
    chan2_raw: int = 0
    """RC channel 2 value."""
    chan3_raw: int = 0
    """RC channel 3 value."""
    chan4_raw: int = 0
    """RC channel 4 value."""
    chan5_raw: int = 0
    """RC channel 5 value."""
    chan6_raw: int = 0
    """RC channel 6 value."""
    chan7_raw: int = 0
    """RC channel 7 value."""
    chan8_raw: int = 0
    """RC channel 8 value."""
    rssi: int = 0
    """Receive signal strength indicator in device-dependent units/scale.
    Values: [0-254], UINT8_MAX: invalid/unknown.
    """


class ServoOutputRaw(MavMessage):
    """The RAW values of the servo outputs. The standard PPM
    modulation is as follows: 1000 microseconds: 0%, 2000 microseconds: 100%.
    """

    time_usec: int = 0
    """Timestamp (UNIX Epoch time or time since system boot)."""
    servo1_raw: int = 0
    """Servo output 1 value"""
    servo2_raw: int = 0
    """Servo output 2 value"""
    servo3_raw: int = 0
    """Servo output 3 value"""
    servo4_raw: int = 0
    """Servo output 4 value"""
    servo5_raw: int = 0
    """Servo output 5 value"""
    servo6_raw: int = 0
    """Servo output 6 value"""
    servo7_raw: int = 0
    """Servo output 7 value"""
    servo8_raw: int = 0
    """Servo output 8 value"""
    servo9_raw: int = 0
    """Servo output 9 value"""
    servo10_raw: int = 0
    """Servo output 10 value"""
    servo11_raw: int = 0
    """Servo output 11 value"""
    servo12_raw: int = 0
    """Servo output 12 value"""
    servo13_raw: int = 0
    """Servo output 13 value"""
    servo14_raw: int = 0
    """Servo output 14 value"""
    servo15_raw: int = 0
    """Servo output 15 value"""
    servo16_raw: int = 0
    """Servo output 16 value"""


class RadioStatus(MavMessage):
    """Status generated by radio and injected into MAVLink stream."""

    rssi: int = 0
    """Local (message sender) received signal strength indication in device-dependent units/scale.
    Values: [0-254], UINT8_MAX: invalid/unknown.
    """
    remrssi: int = 0
    """Remote (message receiver) signal strength indication in device-dependent units/scale.
    Values: [0-254], UINT8_MAX: invalid/unknown.
    """
    txbuf: int = 0
    """Remaining free transmitter buffer space."""
    noise: int = 0
    """Local background noise level. These are device dependent RSSI values (scale as approx 2x dB on SiK radios).
    Values: [0-254], UINT8_MAX: invalid/unknown.
    """
    remnoise: int = 0
    """Remote background noise level. These are device dependent RSSI values (scale as approx 2x dB on SiK radios).
    Values: [0-254], UINT8_MAX: invalid/unknown.
    """
    rxerrors: int = 0
    """Count of radio packet receive errors (since boot)."""
    fixed: int = 0
    """Count of error corrected radio packets (since boot)."""


class MissionRequest(MavMessage):
    """Request the information of the mission item with the sequence number seq.
    The response of the system to this message should be a MISSION_ITEM_INT message.
    https://mavlink.io/en/services/mission.html
    """

    target_system: int = 0
    target_component: int = 0
    seq: int = 0
    mission_type: MissionType = MissionType.MISSION


class MissionACK(MavMessage):
    """Acknowledgment message during waypoint handling. The type field states
    if this message is a positive ack (type=0) or if an error happened (type=non-zero).
    """

    target_system: int = 0
    target_component: int = 0
    type: MissionResult = MissionResult.NOT_RECEIVED
    mission_type: MissionType = MissionType.MISSION


class CommandACK(MavMessage):
    """Report status of a command. Includes feedback whether the command was executed.
    The command microservice is documented at https://mavlink.io/en/services/command.html
    """

    command: int = 0
    """Command ID."""
    result: CommandResult = CommandResult.NOT_RECEIVED
    """Command result."""


class ParamValue(MavMessage):
    """Emit the value of a onboard parameter. The parameter microservice is documented at
    https://mavlink.io/en/services/parameter.html
    """

    param_id: str = ""
    param_value: float = 0.0
    param_type: int = 0
    param_count: int = 0
    """"Total number of onboard parameters"""
    param_index: int = 0
    """Index of this onboard parameter"""


class PositionTargetLocalNED(MavMessage):
    """MAVLink message for local NED position target."""

    time_boot_ms: int = 0
    """Timestamp (milliseconds since system boot)."""

    target_system: int = 0
    """System ID of the target system."""

    target_component: int = 0
    """Component ID of the target system."""

    coordinate_frame: int = 0
    """Coordinate frame in which the position is represented.
    0: FRAME_BODY_NED, 1: FRAME_LOCAL_NED, 2: FRAME_GLOBAL_INT, 3: FRAME_GLOBAL_RELATIVE_ALT.
    """

    type_mask: int = 0
    """Bitmask to indicate which dimensions are being used for control.
    Bit 0: X, Bit 1: Y, Bit 2: Z, Bit 3: Vx, Bit 4: Vy, Bit 5: Vz, Bit 6: Afx, Bit 7: Afy, Bit 8: Afz,
    Bit 9: Yaw, Bit 10: Yaw Rate.
    """

    x: float = 0.0
    """X-position in the local NED frame (meters)."""

    y: float = 0.0
    """Y-position in the local NED frame (meters)."""

    z: float = 0.0
    """Z-position in the local NED frame (meters)."""

    vx: float = 0.0
    """X-velocity in the local NED frame (m/s)."""

    vy: float = 0.0
    """Y-velocity in the local NED frame (m/s)."""

    vz: float = 0.0
    """Z-velocity in the local NED frame (m/s)."""

    afx: float = 0.0
    """X-acceleration or force in the local NED frame (m/s^2 or N)."""

    afy: float = 0.0
    """Y-acceleration or force in the local NED frame (m/s^2 or N)."""

    afz: float = 0.0
    """Z-acceleration or force in the local NED frame (m/s^2 or N)."""

    yaw: float = 0.0
    """Yaw setpoint (radians)."""

    yaw_rate: float = 0.0
    """Yaw rate setpoint (radians/second)."""


class HomePosition(MavMessage):
    """MAVLink message for home position information."""

    latitude: int = 0
    """Latitude of the home position (WGS84) in degrees * 1e7."""

    longitude: int = 0
    """Longitude of the home position (WGS84) in degrees * 1e7."""

    altitude: int = 0
    """Altitude of the home position (MSL) in millimeters (positive for up)."""

    x: float = 0.0
    """X position in NED frame (meters)."""

    y: float = 0.0
    """Y position in NED frame (meters)."""

    z: float = 0.0
    """Z position in NED frame (meters)."""

    q: list[float] = [0.0, 0.0, 0.0, 0.0]
    """Quaternion representation of the home position orientation (w, x, y, z)."""

    approach_x: float = 0.0
    """Local X position of the home position in the body frame (meters)."""

    approach_y: float = 0.0
    """Local Y position of the home position in the body frame (meters)."""

    approach_z: float = 0.0
    """Local Z position of the home position in the body frame (meters)."""


class LocalPositionNED(MavMessage):
    """MAVLink message for local position in NED (North-East-Down) frame."""

    time_boot_ms: int = 0
    """Timestamp (milliseconds since system boot)."""

    x: float = 0.0
    """X position in local NED frame (meters)."""

    y: float = 0.0
    """Y position in local NED frame (meters)."""

    z: float = 0.0
    """Z position in local NED frame (meters)."""

    vx: float = 0.0
    """X velocity in local NED frame (m/s)."""

    vy: float = 0.0
    """Y velocity in local NED frame (m/s)."""

    vz: float = 0.0
    """Z velocity in local NED frame (m/s)."""

    ax: float = 0.0
    """X acceleration in local NED frame (m/s^2)."""

    ay: float = 0.0
    """Y acceleration in local NED frame (m/s^2)."""

    az: float = 0.0
    """Z acceleration in local NED frame (m/s^2)."""


class NavControllerOutput(MavMessage):
    """MAVLink message for navigation controller output."""

    nav_roll: float = 0.0
    """Current desired roll angle (degrees)."""

    nav_pitch: float = 0.0
    """Current desired pitch angle (degrees)."""

    nav_bearing: int = 0
    """Current desired heading/bearing (degrees) toward the active waypoint."""

    target_bearing: int = 0
    """Current bearing to the active waypoint (degrees)."""

    wp_dist: int = 0
    """Distance to the active waypoint (meters)."""

    alt_error: int = 0
    """Current altitude error (meters)."""

    aspd_error: int = 0
    """Current airspeed error (m/s)."""

    xtrack_error: int = 0
    """Current crosstrack error (meters)."""


class RCChannels(MavMessage):
    """MAVLink message for RC channels information."""

    time_boot_ms: int = 0
    """Timestamp (milliseconds since system boot)."""

    chancount: int = 0
    """Number of RC channels being received."""

    chan1_raw: int = 0
    """Raw value of RC channel 1."""

    chan2_raw: int = 0
    """Raw value of RC channel 2."""

    chan3_raw: int = 0
    """Raw value of RC channel 3."""

    chan4_raw: int = 0
    """Raw value of RC channel 4."""

    chan5_raw: int = 0
    """Raw value of RC channel 5."""

    chan6_raw: int = 0
    """Raw value of RC channel 6."""

    chan7_raw: int = 0
    """Raw value of RC channel 7."""

    chan8_raw: int = 0
    """Raw value of RC channel 8."""

    chan9_raw: int = 0
    """Raw value of RC channel 9."""

    chan10_raw: int = 0
    """Raw value of RC channel 10."""

    chan11_raw: int = 0
    """Raw value of RC channel 11."""

    chan12_raw: int = 0
    """Raw value of RC channel 12."""

    chan13_raw: int = 0
    """Raw value of RC channel 13."""

    chan14_raw: int = 0
    """Raw value of RC channel 14."""

    chan15_raw: int = 0
    """Raw value of RC channel 15."""

    chan16_raw: int = 0
    """Raw value of RC channel 16."""

    chan17_raw: int = 0
    """Raw value of RC channel 17."""

    chan18_raw: int = 0
    """Raw value of RC channel 18."""

    rssi: int = 0
    """Received signal strength indicator in device-dependent units/scale (0-254)."""


class WindCov(MavMessage):
    """MAVLink message for wind covariance."""

    time_usec: int = 0
    """Timestamp (microseconds since system boot or since epoch)."""

    wind_x: float = 0.0
    """Wind in X (NED) direction, m/s."""

    wind_y: float = 0.0
    """Wind in Y (NED) direction, m/s."""

    wind_z: float = 0.0
    """Wind in Z (NED) direction, m/s."""

    var_horiz: float = 0.0
    """Horizontal wind variance, m^2/s^2."""

    var_vert: float = 0.0
    """Vertical wind variance, m^2/s^2."""

    wind_alt: float = 0.0
    """Altitude (above MSL), m."""

    horiz_accuracy: float = 0.0
    """Horizontal speed 1-STD accuracy."""

    vert_accuracy: float = 0.0
    """Vertical speed 1-STD accuracy."""


class EncapsulatedData(MavMessage):
    """Data packet."""

    seqnr: int = 0
    """Sequence number (starting with 0 on every transmission)."""

    data: bytes = bytes()
    """Data bytes."""


class MissionCurrent(MavMessage):
    """Message that announces the sequence number of the current
    target mission item (that the system will fly towards/execute when
    the mission is running).
    """

    seq: int = 0
    """Sequence number."""

    total: int = 0
    """Total number of mission items on vehicle (on last item, sequence == total).
    If the autopilot stores its home location as part of the mission this will be
    excluded from the total. 0: Not supported, UINT16_MAX if no mission is present
    on the vehicle.
    """

    mission_state: MissionState = MissionState.MISSION_STATE_UNKNOWN
    """Mission state machine state."""

    mission_mode: int = 0
    """Vehicle is in a mode that can execute mission items or suspended.
    0: Unknown, 1: In mission mode, 2: Suspended (not in mission mode).
    """

    mission_id: int = 0
    """Id of current on-vehicle mission plan, or 0 if IDs are not supported
    or there is no mission loaded.
    """

    fence_id: int = 0
    """Id of current on-vehicle fence plan, or 0 if IDs are not supported or
    there is no fence loaded.
    """

    rally_points_id: int = 0
    """Id of current on-vehicle rally point plan, or 0 if IDs are not supported
    or there are no rally points loaded.
    """


class MissionItemReached(MavMessage):
    """A certain mission item has been reached. The system will either hold this
    position (or circle on the orbit) or (if the autocontinue on the WP was set)
    continue to the next waypoint.
    """

    seq: int = 0
    """Sequence number."""


class MissionCount(MavMessage):
    """This message is emitted as response to `MISSION_REQUEST_LIST`
    by the MAV and to initiate a write transaction.
    """

    target_system: int = 0
    target_component: int = 0
    count: int = 0
    mission_type: MissionType = MissionType.ALL
    opaque_id: int = 0
