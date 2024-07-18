from __future__ import annotations
import jiminy_py.core
import typing
import Boost.Python
import ctypes
import inspect
import logging
import numpy
import os
import pinocchio.pinocchio_pywrap.serialization
import re
import sys
_Shape = typing.Tuple[int, ...]

__all__ = [
    "AbstractConstraint",
    "AbstractController",
    "AbstractMotor",
    "AbstractSensor",
    "BadControlFlow",
    "BaseConstraint",
    "BaseController",
    "BaseFunctionalController",
    "ConstraintTree",
    "ContactSensor",
    "CouplingForce",
    "CouplingForceVector",
    "DistanceConstraint",
    "EffortSensor",
    "EncoderSensor",
    "Engine",
    "ForceSensor",
    "FrameConstraint",
    "FunctionalController",
    "GJKInitialGuess",
    "HeightmapFunction",
    "HeightmapType",
    "ImpulseForce",
    "ImpulseForceVector",
    "ImuSensor",
    "JointConstraint",
    "JointModelType",
    "LogicError",
    "LookupError",
    "Model",
    "NotImplementedError",
    "OSError",
    "PCG32",
    "PeriodicFourierProcess",
    "PeriodicGaussianProcess",
    "PeriodicPerlinProcess1D",
    "PeriodicPerlinProcess2D",
    "PeriodicPerlinProcess3D",
    "PeriodicTabularProcess",
    "ProfileForce",
    "ProfileForceVector",
    "RandomPerlinProcess1D",
    "RandomPerlinProcess2D",
    "RandomPerlinProcess3D",
    "Robot",
    "RobotState",
    "SensorMeasurementTree",
    "SimpleMotor",
    "SphereConstraint",
    "StepperState",
    "TimeStateBoolFunctor",
    "TimeStateForceFunctor",
    "WheelConstraint",
    "__raw_version__",
    "__version__",
    "aba",
    "array_copyto",
    "build_geom_from_urdf",
    "build_models_from_urdf",
    "computeJMinvJt",
    "computeKineticEnergy",
    "crba",
    "discretize_heightmap",
    "get_cmake_module_path",
    "get_frame_indices",
    "get_include",
    "get_joint_indices",
    "get_joint_position_first_index",
    "get_joint_type",
    "get_libraries",
    "interpolate_positions",
    "is_position_valid",
    "load_from_binary",
    "merge_heightmaps",
    "multi_array_copyto",
    "normal",
    "periodic_perlin_ground",
    "periodic_stairs_ground",
    "query_heightmap",
    "random_perlin_ground",
    "random_tile_ground",
    "rnea",
    "save_to_binary",
    "seed",
    "sharedMemory",
    "solveJMinvJtv",
    "sum_heightmaps",
    "unidirectional_periodic_perlin_ground",
    "unidirectional_random_perlin_ground",
    "uniform"
]


class AbstractConstraint():
    def compute_jacobian_and_drift(self, q: numpy.ndarray, v: numpy.ndarray) -> None: ...
    def reset(self, q: numpy.ndarray, v: numpy.ndarray) -> None: ...
    @property
    def baumgarte_freq(self) -> float:
        """
        :type: float
        """
    @baumgarte_freq.setter
    def baumgarte_freq(self: AbstractConstraint) -> None:
        pass
    @property
    def drift(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def is_enabled(self) -> bool:
        """
        :type: bool
        """
    @is_enabled.setter
    def is_enabled(self: AbstractConstraint) -> None:
        pass
    @property
    def jacobian(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def kd(self) -> float:
        """
        :type: float
        """
    @kd.setter
    def kd(self: AbstractConstraint) -> None:
        pass
    @property
    def kp(self) -> float:
        """
        :type: float
        """
    @kp.setter
    def kp(self: AbstractConstraint) -> None:
        pass
    @property
    def lambda_c(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def size(self) -> int:
        """
        :type: int
        """
    @property
    def type(self) -> str:
        """
        :type: str
        """
    pass
class AbstractController():
    def compute_command(self, t: float, q: numpy.ndarray, v: numpy.ndarray, command: numpy.ndarray) -> None: ...
    def get_options(self) -> dict: ...
    def initialize(self, robot: Robot) -> None: ...
    def internal_dynamics(self, t: float, q: numpy.ndarray, v: numpy.ndarray, u_custom: numpy.ndarray) -> None: ...
    def register_constant(self, name: str, value: typing.Any) -> None: ...
    def register_variable(self, name: str, value: typing.Any) -> None: 
        """
        @copydoc AbstractController::registerVariable
        """
    def register_variables(self, fieldnames: list, values: typing.Any) -> None: ...
    def remove_entries(self) -> None: ...
    def reset(self, reset_dynamic_telemetry: bool = False) -> None: ...
    def set_options(self, options: dict) -> None: ...
    @property
    def is_initialized(self) -> bool:
        """
        :type: bool
        """
    @property
    def robot(self) -> Robot:
        """
        :type: Robot
        """
    @property
    def sensor_measurements(self) -> SensorMeasurementTree:
        """
        :type: SensorMeasurementTree
        """
    pass
class AbstractMotor():
    def get_options(self) -> dict: ...
    def set_options(self, arg2: dict) -> None: ...
    @property
    def armature(self) -> float:
        """
        :type: float
        """
    @property
    def backlash(self) -> float:
        """
        :type: float
        """
    @property
    def effort_limit(self) -> float:
        """
        :type: float
        """
    @property
    def index(self) -> int:
        """
        :type: int
        """
    @property
    def is_attached(self) -> bool:
        """
        :type: bool
        """
    @property
    def is_initialized(self) -> bool:
        """
        :type: bool
        """
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    @property
    def joint_name(self) -> str:
        """
        :type: str
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def position_limit_lower(self) -> float:
        """
        :type: float
        """
    @property
    def position_limit_upper(self) -> float:
        """
        :type: float
        """
    @property
    def velocity_limit(self) -> float:
        """
        :type: float
        """
    pass
class AbstractSensor():
    def __repr__(self) -> str: ...
    def get_options(self) -> dict: ...
    def set_options(self, arg2: dict) -> None: ...
    @property
    def data(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @data.setter
    def data(self: AbstractSensor) -> None:
        pass
    @property
    def fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def index(self) -> int:
        """
        :type: int
        """
    @property
    def is_attached(self) -> bool:
        """
        :type: bool
        """
    @property
    def is_initialized(self) -> bool:
        """
        :type: bool
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def type(self) -> str:
        """
        :type: str
        """
    pass
class LogicError(Exception, BaseException):
    pass
class BaseConstraint(AbstractConstraint):
    def __init__(self) -> None: ...
    def compute_jacobian_and_drift(self, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: ...
    def reset(self, arg2: numpy.ndarray, arg3: numpy.ndarray) -> None: ...
    __instance_size__ = 32
    type = 'UserConstraint'
    pass
class BaseController(AbstractController):
    def __init__(self) -> None: ...
    @typing.overload
    def compute_command(self, t: float, q: numpy.ndarray, v: numpy.ndarray, command: numpy.ndarray) -> None: ...
    @typing.overload
    def compute_command(self, arg2: float, arg3: numpy.ndarray, arg4: numpy.ndarray, arg5: numpy.ndarray) -> None: ...
    @typing.overload
    def internal_dynamics(self, t: float, q: numpy.ndarray, v: numpy.ndarray, u_custom: numpy.ndarray) -> None: ...
    @typing.overload
    def internal_dynamics(self, arg2: float, arg3: numpy.ndarray, arg4: numpy.ndarray, arg5: numpy.ndarray) -> None: ...
    def reset(self, reset_dynamic_telemetry: bool = False) -> None: ...
    __instance_size__ = 32
    pass
class BaseFunctionalController(AbstractController):
    pass
class ConstraintTree():
    @property
    def bounds_joints(self) -> dict:
        """
        :type: dict
        """
    @property
    def collision_bodies(self) -> list:
        """
        :type: list
        """
    @property
    def contact_frames(self) -> dict:
        """
        :type: dict
        """
    @property
    def user(self) -> dict:
        """
        :type: dict
        """
    pass
class ContactSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, frame_name: str) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 32
    fieldnames = ['FX', 'FY', 'FZ']
    type = 'ContactSensor'
    pass
class CouplingForce():
    @property
    def func(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def robot_index_1(self) -> int:
        """
        :type: int
        """
    @property
    def robot_index_2(self) -> int:
        """
        :type: int
        """
    @property
    def robot_name_1(self) -> str:
        """
        :type: str
        """
    @property
    def robot_name_2(self) -> str:
        """
        :type: str
        """
    pass
class CouplingForceVector():
    def __contains__(self, arg2: typing.Any) -> bool: ...
    def __delitem__(self, arg2: typing.Any) -> None: ...
    def __getitem__(self, arg2: typing.Any) -> typing.Any: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg2: typing.Any, arg3: typing.Any) -> None: ...
    def append(self, arg2: typing.Any) -> None: ...
    def extend(self, arg2: typing.Any) -> None: ...
    pass
class DistanceConstraint(AbstractConstraint):
    def __init__(self, first_frame_name: str, second_frame_name: str) -> None: ...
    @property
    def frame_indices(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def frame_names(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def reference_distance(self) -> float:
        """
        :type: float
        """
    @reference_distance.setter
    def reference_distance(self: DistanceConstraint) -> None:
        pass
    __instance_size__ = 32
    type = 'DistanceConstraint'
    pass
class EffortSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, motor_name: str) -> None: ...
    @property
    def motor_index(self) -> int:
        """
        :type: int
        """
    @property
    def motor_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 32
    fieldnames = ['U']
    type = 'EffortSensor'
    pass
class EncoderSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, motor_name: typing.Any = None, joint_name: typing.Any = None) -> None: ...
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    @property
    def joint_name(self) -> str:
        """
        :type: str
        """
    @property
    def motor_index(self) -> int:
        """
        :type: int
        """
    @property
    def motor_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 32
    fieldnames = ['Q', 'V']
    type = 'EncoderSensor'
    pass
class Engine():
    def __init__(self) -> None: ...
    def add_robot(self, robot: Robot) -> None: ...
    @staticmethod
    def compute_forward_kinematics(robot: Robot, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray) -> None: ...
    def compute_robots_dynamics(self, t_end: float, q_list: typing.Any, v_list: typing.Any) -> list: ...
    def get_options(self) -> dict: ...
    def get_robot(self, robot_name: str) -> Robot: ...
    def get_robot_index(self, robot_name: str) -> int: ...
    def get_robot_state(self, robot_name: str) -> RobotState: ...
    def get_simulation_options(self) -> dict: ...
    @staticmethod
    def read_log(fullpath: str, format: typing.Any = None) -> dict: 
        """
        Read a logfile from jiminy.

        .. note::
            This function supports both binary and hdf5 log.

        :param fullpath: Name of the file to load.
        :param format: Name of the file to load.

        :returns: Dictionary containing the logged constants and variables.
        """
    def register_coupling_force(self, robot_name_1: str, robot_name_2: str, frame_name_1: str, frame_name_2: str, force_func: typing.Any) -> None: ...
    def register_impulse_force(self, robot_name: str, frame_name: str, t: float, dt: float, force: numpy.ndarray) -> None: ...
    def register_profile_force(self, robot_name: str, frame_name: str, force_func: typing.Any, update_period: float = 0.0) -> None: ...
    @typing.overload
    def register_viscoelastic_coupling_force(self, robot_name_1: str, robot_name_2: str, frame_name_1: str, frame_name_2: str, stiffness: numpy.ndarray, damping: numpy.ndarray, alpha: float = 0.5) -> None: ...
    @typing.overload
    def register_viscoelastic_coupling_force(self, robot_name: str, frame_name_1: str, frame_name_2: str, stiffness: numpy.ndarray, damping: numpy.ndarray, alpha: float = 0.5) -> None: ...
    @typing.overload
    def register_viscoelastic_directional_coupling_force(self, robot_name_1: str, robot_name_2: str, frame_name_1: str, frame_name_2: str, stiffness: float, damping: float, rest_length: float = 0.0) -> None: ...
    @typing.overload
    def register_viscoelastic_directional_coupling_force(self, robot_name: str, frame_name_1: str, frame_name_2: str, stiffness: float, damping: float, rest_length: float = 0.0) -> None: ...
    def remove_all_forces(self) -> None: ...
    @typing.overload
    def remove_coupling_forces(self, robot_name_1: str, robot_name_2: str) -> None: ...
    @typing.overload
    def remove_coupling_forces(self, robot_name: str) -> None: ...
    def remove_impulse_forces(self, robot_name: str) -> None: ...
    def remove_profile_forces(self, robot_name: str) -> None: ...
    def remove_robot(self, robot_name: str) -> None: ...
    def reset(self, reset_random_generator: bool = False, remove_all_forces: bool = False) -> None: ...
    def set_options(self, arg2: dict) -> None: ...
    def set_simulation_options(self, arg2: dict) -> None: ...
    @typing.overload
    def simulate(self, t_end: float, q_init_dict: dict, v_init_dict: dict, a_init_dict: typing.Any = None, callback: typing.Any = None) -> None: ...
    @typing.overload
    def simulate(self, t_end: float, q_init: numpy.ndarray, v_init: numpy.ndarray, a_init: typing.Any = None, is_state_theoretical: bool = False, callback: typing.Any = None) -> None: ...
    @typing.overload
    def start(self, q_init_dict: dict, v_init_dict: dict, a_init_dict: typing.Any = None) -> None: ...
    @typing.overload
    def start(self, q_init: numpy.ndarray, v_init: numpy.ndarray, a_init: typing.Any = None, is_state_theoretical: bool = False) -> None: ...
    def step(self, step_dt: float = -1) -> None: ...
    def stop(self) -> None: ...
    def write_log(self, fullpath: str, format: str) -> None: ...
    @property
    def coupling_forces(self) -> CouplingForceVector:
        """
        :type: CouplingForceVector
        """
    @property
    def impulse_forces(self) -> dict:
        """
        :type: dict
        """
    @property
    def is_simulation_running(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_data(self) -> dict:
        """
        :type: dict
        """
    @property
    def profile_forces(self) -> dict:
        """
        :type: dict
        """
    @property
    def robot_states(self) -> list:
        """
        :type: list
        """
    @property
    def robots(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def stepper_state(self) -> StepperState:
        """
        :type: StepperState
        """
    __instance_size__ = 32
    simulation_duration_max = 922337203.6854776
    telemetry_time_unit = 1e-10
    pass
class ForceSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, frame_name: str) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    __instance_size__ = 32
    fieldnames = ['FX', 'FY', 'FZ', 'MX', 'MY', 'MZ']
    type = 'ForceSensor'
    pass
class FrameConstraint(AbstractConstraint):
    def __init__(self, frame_name: str, mask_fixed: typing.Any = None) -> None: ...
    def set_normal(self, arg2: numpy.ndarray) -> None: ...
    @property
    def dofs_fixed(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def local_rotation(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def reference_transform(self) -> SE3:
        """
        :type: SE3
        """
    @reference_transform.setter
    def reference_transform(self: FrameConstraint) -> None:
        pass
    type = 'FrameConstraint'
    pass
class FunctionalController(BaseFunctionalController, AbstractController):
    def __init__(self, compute_command: typing.Any = None, internal_dynamics: typing.Any = None) -> None: ...
    def reset(self, reset_dynamic_telemetry: bool = False) -> None: ...
    pass
class GJKInitialGuess(Boost.Python.enum, int):
    BoundingVolumeGuess = jiminy_py.core.GJKInitialGuess.BoundingVolumeGuess
    CachedGuess = jiminy_py.core.GJKInitialGuess.CachedGuess
    DefaultGuess = jiminy_py.core.GJKInitialGuess.DefaultGuess
    __slots__ = ()
    names = {'DefaultGuess': jiminy_py.core.GJKInitialGuess.DefaultGuess, 'CachedGuess': jiminy_py.core.GJKInitialGuess.CachedGuess, 'BoundingVolumeGuess': jiminy_py.core.GJKInitialGuess.BoundingVolumeGuess}
    values = {0: jiminy_py.core.GJKInitialGuess.DefaultGuess, 1: jiminy_py.core.GJKInitialGuess.CachedGuess, 2: jiminy_py.core.GJKInitialGuess.BoundingVolumeGuess}
    pass
class HeightmapFunction():
    def __call__(self, position: numpy.ndarray) -> tuple: ...
    def __init__(self, heightmap_function: typing.Any, heightmap_type: HeightmapType = HeightmapType.GENERIC) -> None: ...
    @property
    def py_function(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class HeightmapType(Boost.Python.enum, int):
    CONSTANT = jiminy_py.core.HeightmapType.CONSTANT
    GENERIC = jiminy_py.core.HeightmapType.GENERIC
    STAIRS = jiminy_py.core.HeightmapType.STAIRS
    __slots__ = ()
    names = {'CONSTANT': jiminy_py.core.HeightmapType.CONSTANT, 'STAIRS': jiminy_py.core.HeightmapType.STAIRS, 'GENERIC': jiminy_py.core.HeightmapType.GENERIC}
    values = {1: jiminy_py.core.HeightmapType.CONSTANT, 2: jiminy_py.core.HeightmapType.STAIRS, 3: jiminy_py.core.HeightmapType.GENERIC}
    pass
class ImpulseForce():
    @property
    def dt(self) -> float:
        """
        :type: float
        """
    @property
    def force(self) -> Force:
        """
        :type: Force
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def t(self) -> float:
        """
        :type: float
        """
    pass
class ImpulseForceVector():
    def __contains__(self, arg2: typing.Any) -> bool: ...
    def __delitem__(self, arg2: typing.Any) -> None: ...
    def __getitem__(self, arg2: typing.Any) -> typing.Any: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg2: typing.Any, arg3: typing.Any) -> None: ...
    def append(self, arg2: typing.Any) -> None: ...
    def extend(self, arg2: typing.Any) -> None: ...
    pass
class ImuSensor(AbstractSensor):
    def __init__(self, name: str) -> None: ...
    def initialize(self, frame_name: str) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    __instance_size__ = 32
    fieldnames = ['GyroX', 'GyroY', 'GyroZ', 'AccelX', 'AccelY', 'AccelZ']
    type = 'ImuSensor'
    pass
class JointConstraint(AbstractConstraint):
    def __init__(self, joint_name: str) -> None: ...
    @property
    def joint_index(self) -> int:
        """
        :type: int
        """
    @property
    def joint_name(self) -> str:
        """
        :type: str
        """
    @property
    def reference_configuration(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @reference_configuration.setter
    def reference_configuration(self: JointConstraint) -> None:
        pass
    @property
    def rotation_dir(self) -> bool:
        """
        :type: bool
        """
    @rotation_dir.setter
    def rotation_dir(self: JointConstraint) -> None:
        pass
    __instance_size__ = 32
    type = 'JointConstraint'
    pass
class JointModelType(Boost.Python.enum, int):
    FREE = jiminy_py.core.JointModelType.FREE
    LINEAR = jiminy_py.core.JointModelType.LINEAR
    NONE = jiminy_py.core.JointModelType.NONE
    PLANAR = jiminy_py.core.JointModelType.PLANAR
    ROTARY = jiminy_py.core.JointModelType.ROTARY
    ROTARY_UNBOUNDED = jiminy_py.core.JointModelType.ROTARY_UNBOUNDED
    SPHERICAL = jiminy_py.core.JointModelType.SPHERICAL
    __slots__ = ()
    names = {'NONE': jiminy_py.core.JointModelType.NONE, 'LINEAR': jiminy_py.core.JointModelType.LINEAR, 'ROTARY': jiminy_py.core.JointModelType.ROTARY, 'ROTARY_UNBOUNDED': jiminy_py.core.JointModelType.ROTARY_UNBOUNDED, 'PLANAR': jiminy_py.core.JointModelType.PLANAR, 'SPHERICAL': jiminy_py.core.JointModelType.SPHERICAL, 'FREE': jiminy_py.core.JointModelType.FREE}
    values = {0: jiminy_py.core.JointModelType.NONE, 1: jiminy_py.core.JointModelType.LINEAR, 2: jiminy_py.core.JointModelType.ROTARY, 3: jiminy_py.core.JointModelType.ROTARY_UNBOUNDED, 4: jiminy_py.core.JointModelType.PLANAR, 6: jiminy_py.core.JointModelType.SPHERICAL, 7: jiminy_py.core.JointModelType.FREE}
    pass
class BadControlFlow(LogicError, Exception, BaseException):
    pass
class LookupError(Exception, BaseException):
    pass
class Model():
    def __init__(self) -> None: ...
    def add_collision_bodies(self, body_names: typing.Any = [], ignore_meshes: bool = False) -> None: ...
    def add_constraint(self, name: str, constraint: AbstractConstraint) -> None: ...
    def add_contact_points(self, frame_names: typing.Any = []) -> None: ...
    def add_frame(self, frame_name: str, parent_body_name: str, frame_placement: SE3) -> None: ...
    def compute_constraints(self, q: numpy.ndarray, v: numpy.ndarray) -> None: ...
    def copy(self) -> Model: ...
    def get_constraints_jacobian_and_drift(self) -> tuple: ...
    def get_extended_position_from_theoretical(self, mechanical_position: numpy.ndarray) -> numpy.ndarray: ...
    def get_extended_velocity_from_theoretical(self, mechanical_velocity: numpy.ndarray) -> numpy.ndarray: ...
    def get_options(self) -> dict: ...
    def get_theoretical_position_from_extended(self, flexibility_position: numpy.ndarray) -> numpy.ndarray: ...
    def get_theoretical_velocity_from_extended(self, flexibility_velocity: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def initialize(self, urdf_path: str, has_freeflyer: bool = False, mesh_package_dirs: typing.Any = [], load_visual_meshes: bool = False) -> None: ...
    @typing.overload
    def initialize(self, pinocchio_model: Model, collision_model: typing.Any = None, visual_model: typing.Any = None) -> None: ...
    def remove_collision_bodies(self, body_names: typing.Any) -> None: ...
    def remove_constraint(self, name: str) -> None: ...
    def remove_contact_points(self, frame_names: typing.Any) -> None: ...
    def remove_frames(self, frame_names: typing.Any) -> None: ...
    def reset(self, generator: typing.Any) -> None: ...
    def set_options(self, options: dict) -> None: ...
    @property
    def backlash_joint_indices(self) -> StdVec_Index:
        """
        :type: StdVec_Index
        """
    @property
    def backlash_joint_names(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def collision_body_indices(self) -> StdVec_Index:
        """
        :type: StdVec_Index
        """
    @property
    def collision_body_names(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def collision_data(self) -> GeometryData:
        """
        :type: GeometryData
        """
    @property
    def collision_model(self) -> GeometryModel:
        """
        :type: GeometryModel
        """
    @property
    def collision_model_th(self) -> GeometryModel:
        """
        :type: GeometryModel
        """
    @property
    def collision_pair_indices(self) -> StdVec_IndexVector:
        """
        :type: StdVec_IndexVector
        """
    @property
    def constraints(self) -> ConstraintTree:
        """
        :type: ConstraintTree
        """
    @property
    def contact_forces(self) -> StdVec_Force:
        """
        :type: StdVec_Force
        """
    @property
    def contact_frame_indices(self) -> StdVec_Index:
        """
        :type: StdVec_Index
        """
    @property
    def contact_frame_names(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def flexibility_joint_indices(self) -> StdVec_Index:
        """
        :type: StdVec_Index
        """
    @property
    def flexibility_joint_names(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def has_constraints(self) -> bool:
        """
        :type: bool
        """
    @property
    def has_freeflyer(self) -> bool:
        """
        :type: bool
        """
    @property
    def is_flexibility_enabled(self) -> bool:
        """
        :type: bool
        """
    @property
    def is_initialized(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_acceleration_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def log_constraint_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def log_effort_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def log_f_external_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def log_position_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def log_velocity_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def mechanical_joint_indices(self) -> StdVec_Index:
        """
        :type: StdVec_Index
        """
    @property
    def mechanical_joint_names(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def mechanical_joint_position_indices(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def mechanical_joint_velocity_indices(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def mesh_package_dirs(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def nq(self) -> int:
        """
        :type: int
        """
    @property
    def nv(self) -> int:
        """
        :type: int
        """
    @property
    def nx(self) -> int:
        """
        :type: int
        """
    @property
    def pinocchio_data(self) -> Data:
        """
        :type: Data
        """
    @property
    def pinocchio_data_th(self) -> Data:
        """
        :type: Data
        """
    @property
    def pinocchio_model(self) -> pinocchio.Model:
        """
        :type: pinocchio.Model
        """
    @property
    def pinocchio_model_th(self) -> pinocchio.Model:
        """
        :type: pinocchio.Model
        """
    @property
    def urdf_path(self) -> str:
        """
        :type: str
        """
    @property
    def visual_data(self) -> GeometryData:
        """
        :type: GeometryData
        """
    @property
    def visual_model(self) -> GeometryModel:
        """
        :type: GeometryModel
        """
    @property
    def visual_model_th(self) -> GeometryModel:
        """
        :type: GeometryModel
        """
    __instance_size__ = 32
    pass
class NotImplementedError(LogicError, Exception, BaseException):
    pass
class OSError(Exception, BaseException):
    pass
class PCG32():
    def __call__(self) -> int: ...
    @typing.overload
    def __init__(self, state: int) -> None: ...
    @typing.overload
    def __init__(self, seed_seq: list) -> None: ...
    def seed(self, seed_seq: list) -> None: ...
    __instance_size__ = 32
    max = 4294967295
    min = 0
    pass
class PeriodicTabularProcess():
    def __call__(self, time: float) -> float: ...
    def grad(self, time: float) -> float: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    pass
class PeriodicGaussianProcess(PeriodicTabularProcess):
    def __init__(self, wavelength: float, period: float) -> None: ...
    __instance_size__ = 32
    pass
class PeriodicPerlinProcess1D():
    @typing.overload
    def __call__(self, arg2: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, period: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 32
    pass
class PeriodicPerlinProcess2D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, period: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 32
    pass
class PeriodicPerlinProcess3D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float, arg4: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, period: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float, arg4: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def period(self) -> float:
        """
        :type: float
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 32
    pass
class PeriodicFourierProcess(PeriodicTabularProcess):
    def __init__(self, wavelength: float, period: float) -> None: ...
    __instance_size__ = 32
    pass
class ProfileForce():
    @property
    def force(self) -> Force:
        """
        :type: Force
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def func(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def update_period(self) -> float:
        """
        :type: float
        """
    pass
class ProfileForceVector():
    def __contains__(self, arg2: typing.Any) -> bool: ...
    def __delitem__(self, arg2: typing.Any) -> None: ...
    def __getitem__(self, arg2: typing.Any) -> typing.Any: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __setitem__(self, arg2: typing.Any, arg3: typing.Any) -> None: ...
    def append(self, arg2: typing.Any) -> None: ...
    def extend(self, arg2: typing.Any) -> None: ...
    pass
class RandomPerlinProcess1D():
    @typing.overload
    def __call__(self, arg2: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 32
    pass
class RandomPerlinProcess2D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 32
    pass
class RandomPerlinProcess3D():
    @typing.overload
    def __call__(self, arg2: float, arg3: float, arg4: float) -> float: ...
    @typing.overload
    def __call__(self, vec: numpy.ndarray) -> float: ...
    def __init__(self, wavelength: float, num_octaves: int = 6) -> None: ...
    @typing.overload
    def grad(self, arg2: float, arg3: float, arg4: float) -> numpy.ndarray: ...
    @typing.overload
    def grad(self, vec: numpy.ndarray) -> numpy.ndarray: ...
    def reset(self, generator: typing.Any) -> None: ...
    @property
    def num_octaves(self) -> int:
        """
        :type: int
        """
    @property
    def wavelength(self) -> float:
        """
        :type: float
        """
    __instance_size__ = 32
    pass
class Robot(Model):
    def __init__(self, name: str = '') -> None: ...
    def attach_motor(self, motor: AbstractMotor) -> None: ...
    def attach_sensor(self, sensor: AbstractSensor) -> None: ...
    def compute_sensor_measurements(self, t: float, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray, u_motor: numpy.ndarray, f_external: StdVec_Force) -> None: ...
    def copy(self) -> Robot: ...
    def detach_motor(self, joint_name: str) -> None: ...
    def detach_motors(self, joints_names: typing.Any = []) -> None: ...
    def detach_sensor(self, sensor_type: str, sensor_name: str) -> None: ...
    def detach_sensors(self, sensor_type: str = '') -> None: ...
    def get_model_options(self) -> dict: ...
    def get_motor(self, motor_name: str) -> AbstractMotor: ...
    def get_options(self) -> dict: ...
    def get_sensor(self, sensor_type: str, sensor_name: str) -> AbstractSensor: ...
    @typing.overload
    def initialize(self, urdf_path: str, has_freeflyer: bool = False, mesh_package_dirs: typing.Any = [], load_visual_meshes: bool = False) -> None: ...
    @typing.overload
    def initialize(self, pinocchio_model: Model, collision_model: typing.Any = None, visual_model: typing.Any = None) -> None: ...
    def set_model_options(self, model_options: dict) -> None: ...
    def set_options(self, robot_options: dict) -> None: ...
    @property
    def controller(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @controller.setter
    def controller(self: Robot) -> None:
        pass
    @property
    def is_locked(self) -> bool:
        """
        :type: bool
        """
    @property
    def log_command_fieldnames(self) -> StdVec_StdString:
        """
        :type: StdVec_StdString
        """
    @property
    def motors(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def name(self) -> str:
        """
        :type: str
        """
    @property
    def nmotors(self) -> int:
        """
        :type: int
        """
    @property
    def sensor_measurements(self) -> SensorMeasurementTree:
        """
        :type: SensorMeasurementTree
        """
    @property
    def sensors(self) -> typing.Any:
        """
        :type: typing.Any
        """
    __instance_size__ = 32
    pass
class RobotState():
    def __repr__(self) -> str: ...
    @property
    def a(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def command(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def f_external(self) -> StdVec_Force:
        """
        :type: StdVec_Force
        """
    @property
    def q(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_custom(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_internal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_motor(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def u_transmission(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def v(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    pass
class SensorMeasurementTree():
    def __contains__(self, key: tuple) -> bool: ...
    @typing.overload
    def __getitem__(self, sensor_info: tuple) -> numpy.ndarray: ...
    @typing.overload
    def __getitem__(self, sensor_type: str, sensor_name: str) -> numpy.ndarray: ...
    @typing.overload
    def __getitem__(self, sensor_type: str) -> numpy.ndarray: ...
    def __init__(self, sensor_measurements: dict) -> None: ...
    def __iter__(self) -> typing.Any: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def items(self) -> list: ...
    @typing.overload
    def keys(self) -> list: ...
    @typing.overload
    def keys(self, sensor_type: str) -> list: ...
    def values(self) -> list: ...
    pass
class SimpleMotor(AbstractMotor):
    def __init__(self, motor_name: str) -> None: ...
    def initialize(self, arg2: str) -> None: ...
    __instance_size__ = 32
    pass
class SphereConstraint(AbstractConstraint):
    def __init__(self, frame_name: str, radius: float) -> None: ...
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def normal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def radius(self) -> float:
        """
        :type: float
        """
    @property
    def reference_transform(self) -> SE3:
        """
        :type: SE3
        """
    @reference_transform.setter
    def reference_transform(self: SphereConstraint) -> None:
        pass
    __instance_size__ = 32
    type = 'SphereConstraint'
    pass
class StepperState():
    def __repr__(self) -> str: ...
    @property
    def a(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def dt(self) -> float:
        """
        :type: float
        """
    @property
    def iter(self) -> int:
        """
        :type: int
        """
    @property
    def iter_failed(self) -> int:
        """
        :type: int
        """
    @property
    def q(self) -> typing.Any:
        """
        :type: typing.Any
        """
    @property
    def t(self) -> float:
        """
        :type: float
        """
    @property
    def v(self) -> typing.Any:
        """
        :type: typing.Any
        """
    pass
class TimeStateBoolFunctor():
    def __call__(self, t: float, q: numpy.ndarray, v: numpy.ndarray) -> bool: ...
    pass
class TimeStateForceFunctor():
    def __call__(self, t: float, q: numpy.ndarray, v: numpy.ndarray) -> Force: ...
    pass
class WheelConstraint(AbstractConstraint):
    def __init__(self, frame_name: str, radius: float, ground_normal: numpy.ndarray, wheel_axis: numpy.ndarray) -> None: ...
    @property
    def axis(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def frame_index(self) -> int:
        """
        :type: int
        """
    @property
    def frame_name(self) -> str:
        """
        :type: str
        """
    @property
    def normal(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def radius(self) -> float:
        """
        :type: float
        """
    @property
    def reference_transform(self) -> SE3:
        """
        :type: SE3
        """
    @reference_transform.setter
    def reference_transform(self: WheelConstraint) -> None:
        pass
    __instance_size__ = 32
    type = 'WheelConstraint'
    pass
def aba(pinocchio_model: Model, pinocchio_data: Data, q: numpy.ndarray, v: numpy.ndarray, u: numpy.ndarray, fext: StdVec_Force) -> numpy.ndarray:
    """
    Compute ABA with external forces, store the result in Data::ddq and return it.
    """
def array_copyto(dst: typing.Any, src: typing.Any) -> None:
    pass
def build_geom_from_urdf(pinocchio_model: Model, urdf_filename: str, geom_type: int, mesh_package_dirs: typing.Any = [], load_meshes: bool = True, make_meshes_convex: bool = False) -> GeometryModel:
    pass
def build_models_from_urdf(urdf_path: str, has_freeflyer: bool, mesh_package_dirs: typing.Any = [], build_visual_model: bool = False, load_visual_meshes: bool = False) -> tuple:
    pass
def computeJMinvJt(pinocchio_model: Model, pinocchio_data: Data, J: numpy.ndarray, update_decomposition: bool = True) -> numpy.ndarray:
    pass
def computeKineticEnergy(pinocchio_model: Model, pinocchio_data: Data, q: numpy.ndarray, v: numpy.ndarray, update_kinematics: bool = True) -> float:
    """
    Computes the forward kinematics and the kinematic energy of the model for the given joint configuration and velocity given as input. The result is accessible through data.kinetic_energy.
    """
def crba(pinocchio_model: Model, pinocchio_data: Data, q: numpy.ndarray, fastmath: bool = False) -> numpy.ndarray:
    """
    Computes CRBA, store the result in Data and return it.
    """
def discretize_heightmap(heightmap: HeightmapFunction, x_min: float, x_max: float, x_unit: float, y_min: float, y_max: float, y_unit: float, must_simplify: bool = False) -> CollisionGeometry:
    pass
def get_frame_indices(pinocchio_model: Model, frame_names: StdVec_StdString) -> list:
    pass
@typing.overload
def get_joint_indices(pinocchio_model: Model, joint_names: StdVec_StdString) -> StdVec_Index:
    pass
@typing.overload
def get_joint_indices(pinocchio_model: Model, joint_names: StdVec_StdString) -> list:
    pass
def get_joint_position_first_index(pinocchio_model: Model, joint_name: str) -> int:
    pass
@typing.overload
def get_joint_type(joint_model: JointModel) -> JointModelType:
    pass
@typing.overload
def get_joint_type(pinocchio_model: Model, joint_index: int) -> JointModelType:
    pass
def interpolate_positions(pinocchio_model: Model, times_in: numpy.ndarray, positions_in: numpy.ndarray, times_out: numpy.ndarray) -> numpy.ndarray:
    pass
def is_position_valid(pinocchio_model: Model, position: numpy.ndarray, tol_abs: float = 1.1920928955078125e-07) -> bool:
    pass
def load_from_binary(data: str, mesh_path_dir: typing.Any = None, mesh_package_dirs: typing.Any = []) -> Robot:
    pass
def merge_heightmaps(heightmaps: typing.Any) -> HeightmapFunction:
    pass
def multi_array_copyto(dst: typing.Any, src: typing.Any) -> None:
    pass
@typing.overload
def normal(generator: typing.Any, mean: numpy.ndarray, stddev: numpy.ndarray) -> numpy.ndarray:
    pass
@typing.overload
def normal(generator: typing.Any, mean: float = 0.0, stddev: float = 1.0, size: typing.Any = None) -> typing.Any:
    pass
def periodic_perlin_ground(wavelength: float, period: float, num_octaves: int, seed: int) -> HeightmapFunction:
    pass
def periodic_stairs_ground(step_width: float, step_height: float, step_number: int, orientation: float) -> HeightmapFunction:
    pass
@typing.overload
def query_heightmap(heightmap: HeightmapFunction, positions: numpy.ndarray, heights: numpy.ndarray) -> None:
    pass
@typing.overload
def query_heightmap(heightmap: HeightmapFunction, positions: numpy.ndarray, heights: numpy.ndarray, normals: numpy.ndarray) -> None:
    pass
def random_perlin_ground(wavelength: float, num_octaves: int, seed: int) -> HeightmapFunction:
    pass
def random_tile_ground(size: numpy.ndarray, height_max: float, interp_delta: numpy.ndarray, sparsity: int, orientation: float, seed: int) -> HeightmapFunction:
    pass
@typing.overload
def rnea(pinocchio_model: Model, pinocchio_data: Data, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray) -> numpy.ndarray:
    """
    Compute the RNEA without external forces, store the result in Data and return it.

    Compute the RNEA with external forces, store the result in Data and return it.
    """
@typing.overload
def rnea(pinocchio_model: Model, pinocchio_data: Data, q: numpy.ndarray, v: numpy.ndarray, a: numpy.ndarray, fext: StdVec_Force) -> numpy.ndarray:
    pass
def save_to_binary(robot: Robot) -> typing.Any:
    pass
def seed(seed_value: int) -> None:
    """
    Initialize the pseudo-random number generator with the argument seed_value.

    C++ signature :
        void seed(unsigned int)
    """
@typing.overload
def sharedMemory(value: bool) -> None:
    """
    Share the memory when converting from Eigen to Numpy.

    C++ signature :
        void sharedMemory(bool)

    Status of the shared memory when converting from Eigen to Numpy.
    If True, the memory is shared when converting an Eigen::Matrix to a numpy.array.
    Otherwise, a deep copy of the Eigen::Matrix is performed.

    C++ signature :
        bool sharedMemory()
    """
@typing.overload
def sharedMemory() -> bool:
    pass
def solveJMinvJtv(pinocchio_data: Data, v: numpy.ndarray, update_decomposition: bool = True) -> numpy.ndarray:
    pass
def sum_heightmaps(heightmaps: typing.Any) -> HeightmapFunction:
    pass
def unidirectional_periodic_perlin_ground(wavelength: float, period: float, num_octaves: int, orientation: float, seed: int) -> HeightmapFunction:
    pass
def unidirectional_random_perlin_ground(wavelength: float, num_octaves: int, orientation: float, seed: int) -> HeightmapFunction:
    pass
@typing.overload
def uniform(generator: typing.Any, lo: numpy.ndarray, hi: numpy.ndarray) -> numpy.ndarray:
    pass
@typing.overload
def uniform(generator: typing.Any, lo: float = 0.0, hi: float = 1.0, size: typing.Any = None) -> typing.Any:
    pass
@typing.overload
def uniform(generator: typing.Any) -> float:
    pass
_JIMINY_REQUIRED_MODULES = ('eigenpy', 'hppfcl', 'pinocchio')
__all__ = ['AbstractConstraint', 'AbstractController', 'AbstractMotor', 'AbstractSensor', 'BadControlFlow', 'BaseConstraint', 'BaseController', 'BaseFunctionalController', 'ConstraintTree', 'ContactSensor', 'CouplingForce', 'CouplingForceVector', 'DistanceConstraint', 'EffortSensor', 'EncoderSensor', 'Engine', 'ForceSensor', 'FrameConstraint', 'FunctionalController', 'GJKInitialGuess', 'HeightmapFunction', 'HeightmapType', 'ImpulseForce', 'ImpulseForceVector', 'ImuSensor', 'JointConstraint', 'JointModelType', 'LogicError', 'LookupError', 'Model', 'NotImplementedError', 'OSError', 'PCG32', 'PeriodicFourierProcess', 'PeriodicGaussianProcess', 'PeriodicPerlinProcess1D', 'PeriodicPerlinProcess2D', 'PeriodicPerlinProcess3D', 'PeriodicTabularProcess', 'ProfileForce', 'ProfileForceVector', 'RandomPerlinProcess1D', 'RandomPerlinProcess2D', 'RandomPerlinProcess3D', 'Robot', 'RobotState', 'SensorMeasurementTree', 'SimpleMotor', 'SphereConstraint', 'StepperState', 'TimeStateBoolFunctor', 'TimeStateForceFunctor', 'WheelConstraint', 'aba', 'array_copyto', 'build_geom_from_urdf', 'build_models_from_urdf', 'computeJMinvJt', 'computeKineticEnergy', 'crba', 'discretize_heightmap', 'get_frame_indices', 'get_joint_indices', 'get_joint_position_first_index', 'get_joint_type', 'interpolate_positions', 'is_position_valid', 'load_from_binary', 'merge_heightmaps', 'multi_array_copyto', 'normal', 'periodic_perlin_ground', 'periodic_stairs_ground', 'query_heightmap', 'random_perlin_ground', 'random_tile_ground', 'rnea', 'save_to_binary', 'seed', 'sharedMemory', 'solveJMinvJtv', 'sum_heightmaps', 'unidirectional_periodic_perlin_ground', 'unidirectional_random_perlin_ground', 'uniform', 'get_cmake_module_path', 'get_include', 'get_libraries', '__version__', '__raw_version__']
__raw_version__ = '1.8.8'
__version__ = '1.8.8'
_are_all_dependencies_available = True
_boost_python_lib = 'libboost_python39.so'
_is_boost_shared = True
_lib_prefix = 'lib'
_lib_suffix = '.so'
_module_name = 'serialization'
_module_real_path = 'pinocchio.pinocchio_pywrap.serialization'
_module_sym_path = 'pinocchio.serialization'
_pyver_suffix = '39'
_submodules: list # value = [('cholesky', <module 'pinocchio.pinocchio_pywrap.cholesky'>), ('liegroups', <module 'pinocchio.pinocchio_pywrap.liegroups'>), ('rpy', <module 'pinocchio.pinocchio_pywrap.rpy'>), ('serialization', <module 'pinocchio.pinocchio_pywrap.serialization'>)]
name = 'uniform'
_find_spec = importlib.util.find_spec
_get_config_var = sysconfig.get_config_var
_import_module = importlib.import_module
