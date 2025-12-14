# sensor_config.py
"""
扩展的传感器配置文件 - 支持任意传感器类型
"""

SENSOR_CONFIG = {
    # 激光雷达
    "lidar": {
        "type": "lidar",
        "name": "lidar_2d",
        "relative_position": {"x": 0.0, "y": 0.0, "z": -0.10},
        "geometry": {
            "type": "cylinder",
            "base_radius": 0.04,
            "base_height": 0.005,
            "sensor_radius": 0.035,
            "sensor_height": 0.04
        },
        "specs": {
            "range_min": 0.1,
            "range_max": 30.0,
            "horizontal_fov": 360.0,
            "vertical_fov": 1.0,
            "rotation_rate": 10.0
        }
    },
    
    # 前向相机
    "camera_front": {
        "type": "camera",
        "name": "camera_front",
        "relative_position": {"x": 0.12, "y": 0.0, "z": -0.05},
        "geometry": {
            "type": "cube+cylinder",
            "housing_size": 0.025,
            "lens_radius": 0.012,
            "lens_height": 0.015
        },
        "specs": {
            "resolution": [640, 480],
            "fov": 60.0,
            "focal_length": 24.0,
            "aperture": 20.955
        }
    },
    
    # 后向相机
    "camera_rear": {
        "type": "camera",
        "name": "camera_rear",
        "relative_position": {"x": -0.12, "y": 0.0, "z": -0.05},
        "geometry": {
            "type": "cube+cylinder",
            "housing_size": 0.020,
            "lens_radius": 0.010,
            "lens_height": 0.012
        },
        "specs": {
            "resolution": [640, 480],
            "fov": 120.0,
            "focal_length": 24.0,
            "aperture": 20.955
        }
    },
    
    # 超声波传感器
    "ultrasonic_front": {
        "type": "ultrasonic",
        "name": "ultrasonic_front",
        "relative_position": {"x": 0.15, "y": 0.0, "z": -0.08},
        "geometry": {
            "type": "cylinder",
            "radius": 0.02,
            "height": 0.01
        },
        "specs": {
            "frequency": 40,  # kHz
            "range_min": 0.02,  # 2cm
            "range_max": 4.0,   # 4m
            "beam_angle": 15.0  # degrees
        }
    },
    
    # IMU传感器
    "imu": {
        "type": "imu",
        "name": "imu_center",
        "relative_position": {"x": 0.0, "y": 0.0, "z": 0.0},
        "geometry": {
            "type": "cube",
            "size": 0.015
        },
        "specs": {
            "accelerometer_range": [±16, "g"],
            "gyroscope_range": [±2000, "dps"],
            "update_rate": 100  # Hz
        }
    },
    
    # 温度传感器
    "temperature": {
        "type": "temperature",
        "name": "temperature_sensor",
        "relative_position": {"x": 0.0, "y": 0.0, "z": -0.05},
        "geometry": {
            "type": "sphere",
            "radius": 0.005
        },
        "specs": {
            "range": [-40, 125],  # °C
            "accuracy": 0.5,      # °C
            "response_time": 1.0  # seconds
        }
    },
    
    # 新增传感器示例
    "radar_side": {
        "type": "radar",
        "name": "radar_side_left",
        "relative_position": {"x": 0.0, "y": 0.15, "z": -0.05},
        "geometry": {
            "type": "rectangle",
            "width": 0.06,
            "height": 0.04,
            "depth": 0.01
        },
        "specs": {
            "frequency": 77,    # GHz
            "range": [0.5, 100], # m
            "resolution": 0.1   # m
        }
    },
    
    # 安装配置
    "mounting": {
        "chassis_reference": "chassis_link",
        "correction_offset": -0.15,  # 整体向下15cm修正
        "sensor_thickness": 0.005
    }
}

# 新增传感器类型支持
def create_sensor_geometry(stage, sensor_path, geometry_config):
    """根据几何配置创建传感器几何体"""
    if geometry_config["type"] == "cylinder":
        geom = UsdGeom.Cylinder.Define(stage, sensor_path)
        geom.CreateRadiusAttr(geometry_config["radius"])
        geom.CreateHeightAttr(geometry_config["height"])
        
    elif geometry_config["type"] == "cube":
        geom = UsdGeom.Cube.Define(stage, sensor_path)
        geom.CreateSizeAttr(geometry_config["size"])
        
    elif geometry_config["type"] == "sphere":
        geom = UsdGeom.Sphere.Define(stage, sensor_path)
        geom.CreateRadiusAttr(geometry_config["radius"])
        
    elif geometry_config["type"] == "cube+cylinder":
        # 复合几何体
        housing = UsdGeom.Cube.Define(stage, sensor_path + "/housing")
        housing.CreateSizeAttr(geometry_config["housing_size"])
        
        lens = UsdGeom.Cylinder.Define(stage, sensor_path + "/lens")
        lens.CreateRadiusAttr(geometry_config["lens_radius"])
        lens.CreateHeightAttr(geometry_config["lens_height"])
        
    elif geometry_config["type"] == "rectangle":
        # 长方体
        box = UsdGeom.Cube.Define(stage, sensor_path)
        box.CreateSizeAttr([geometry_config["width"], 
                           geometry_config["height"], 
                           geometry_config["depth"]])

# 批量创建传感器
def create_multiple_sensors(stage, chassis_path, base_pos, sensor_types):
    """批量创建多个传感器"""
    created_sensors = {}
    
    for sensor_type in sensor_types:
        config = SENSOR_CONFIG.get(sensor_type)
        if config:
            created_sensors[sensor_type] = create_sensor_from_config(
                stage, chassis_path, base_pos, sensor_type
            )
    
    return created_sensors

# 传感器工厂模式
class SensorFactory:
    """传感器工厂 - 动态创建任意类型传感器"""
    
    @staticmethod
    def create_sensor(sensor_type, base_position, **custom_config):
        """动态创建传感器"""
        config = SENSOR_CONFIG.get(sensor_type, {}).copy()
        if custom_config:
            config.update(custom_config)
        
        return create_sensor_from_config(base_position, sensor_type, config)
    
    @staticmethod
    def add_new_sensor_type(sensor_name, sensor_config):
        """动态添加新的传感器类型"""
        SENSOR_CONFIG[sensor_name] = sensor_config
    
    @staticmethod
    def get_all_sensor_types():
        """获取所有传感器类型"""
        return [key for key in SENSOR_CONFIG.keys() if key != "mounting"]