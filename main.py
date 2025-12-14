#!/usr/bin/env python3
"""
优化版本：支持任意传感器类型
"""

from isaacsim import SimulationApp
simulation_app = SimulationApp({"headless": False})

import numpy as np
from isaacsim.core.utils.stage import add_reference_to_stage
from isaacsim.core.api.simulation_context import SimulationContext
import omni.usd
from pxr import UsdGeom, Sdf, Gf
from sensor_config import (
    SENSOR_CONFIG, calculate_sensor_position, get_sensor_config, 
    create_sensor_geometry, SensorFactory
)

simulation_context = SimulationApp({"headless": False})

def setup_scene():
    """加载场景和小车"""
    print("加载公寓场景...")
    add_reference_to_stage(
        usd_path="/home/zsy/Desktop/isaacsim/Lightwheel_kb2Hg5blQp_Apartment/Apartment/scene_04.usd",
        prim_path="/World/Apartment"
    )
    
    print("加载my_carter小车...")
    add_reference_to_stage(
        usd_path="/isaac-sim/isaac-sim-standalone-5.1.0-linux-x86_64/my_carter.usd",
        prim_path="/World/my_carter"
    )

def get_chassis_position():
    """获取底盘位置"""
    stage = omni.usd.get_context().get_stage()
    chassis_path = "/World/my_carter/chassis_link"
    chassis_prim = stage.GetPrimAtPath(chassis_path)
    
    if chassis_prim and chassis_prim.IsValid():
        chassis_xform = UsdGeom.Xformable(chassis_prim)
        for op in chassis_xform.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                pos = op.Get()
                if pos:
                    return chassis_path, pos
    
    return "/World/my_carter", Gf.Vec3d(0, 0, 0.1)

def create_sensor_from_config(stage, chassis_path, base_pos, sensor_type):
    """根据配置创建传感器"""
    config = get_sensor_config(sensor_type)
    mounting_config = SENSOR_CONFIG["mounting"]
    
    # 计算最终位置（包含修正偏移）
    final_pos = calculate_sensor_position(
        base_pos, 
        config["relative_position"], 
        mounting_config["correction_offset"]
    )
    
    print(f"\n创建{sensor_type}传感器:")
    print(f"最终位置: ({final_pos['x']:.3f}, {final_pos['y']:.3f}, {final_pos['z']:.3f})")
    
    # 创建传感器
    sensor_path = f"{chassis_path}/{config['name']}"
    sensor_xform = UsdGeom.Xform.Define(stage, sensor_path)
    translate_op = sensor_xform.AddTranslateOp()
    translate_op.Set(Gf.Vec3d(final_pos['x'], final_pos['y'], final_pos['z']))
    
    # 根据传感器类型创建具体组件
    if sensor_type == "lidar":
        create_lidar_components(stage, sensor_path, config)
    elif sensor_type == "camera_front" or sensor_type == "camera_rear":
        create_camera_components(stage, sensor_path, config)
    elif sensor_type == "ultrasonic":
        create_ultrasonic_components(stage, sensor_path, config)
    elif sensor_type == "imu":
        create_imu_components(stage, sensor_path, config)
    elif sensor_type == "temperature":
        create_temperature_components(stage, sensor_path, config)
    elif sensor_type == "radar_side":
        create_radar_components(stage, sensor_path, config)
    else:
        # 通用传感器创建
        create_sensor_geometry(stage, sensor_path, config["geometry"])
    
    return sensor_path

def create_lidar_components(stage, sensor_path, config):
    """创建激光雷达组件"""
    # 底座
    base = UsdGeom.Cylinder.Define(stage, sensor_path + "/base")
    base.CreateRadiusAttr(config["geometry"]["base_radius"])
    base.CreateHeightAttr(config["geometry"]["base_height"])
    
    # 传感器
    sensor = UsdGeom.Cylinder.Define(stage, sensor_path + "/sensor")
    sensor.CreateRadiusAttr(config["geometry"]["sensor_radius"])
    sensor.CreateHeightAttr(config["geometry"]["sensor_height"])
    
    print(f"  激光雷达组件创建完成")

def create_camera_components(stage, sensor_path, config):
    """创建相机组件"""
    # 外壳
    housing = UsdGeom.Cube.Define(stage, sensor_path + "/housing")
    housing.CreateSizeAttr(config["geometry"]["housing_size"])
    
    # 镜头
    lens = UsdGeom.Cylinder.Define(stage, sensor_path + "/lens")
    lens.CreateRadiusAttr(config["geometry"]["lens_radius"])
    lens.CreateHeightAttr(config["geometry"]["lens_height"])
    
    # USD相机传感器
    camera_sensor = UsdGeom.Camera.Define(stage, sensor_path + "/sensor")
    camera_sensor.CreateFocalLengthAttr(config["specs"]["focal_length"])
    camera_sensor.CreateHorizontalApertureAttr(config["specs"]["aperture"])
    camera_sensor.CreateVerticalApertureAttr(config["specs"]["aperture"])
    
    print(f"  相机组件创建完成")

def create_ultrasonic_components(stage, sensor_path, config):
    """创建超声波传感器组件"""
    # 超声波传感器 - 简单的圆柱体
    sensor = UsdGeom.Cylinder.Define(stage, sensor_path + "/sensor")
    sensor.CreateRadiusAttr(config["geometry"]["radius"])
    sensor.CreateHeightAttr(config["geometry"]["height"])
    
    print(f"  超声波传感器组件创建完成")

def create_imu_components(stage, sensor_path, config):
    """创建IMU传感器组件"""
    # IMU - 小立方体
    sensor = UsdGeom.Cube.Define(stage, sensor_path + "/sensor")
    sensor.CreateSizeAttr(config["geometry"]["size"])
    
    print(f"  IMU传感器组件创建完成")

def create_temperature_components(stage, sensor_path, config):
    """创建温度传感器组件"""
    # 温度传感器 - 小球体
    sensor = UsdGeom.Sphere.Define(stage, sensor_path + "/sensor")
    sensor.CreateRadiusAttr(config["geometry"]["radius"])
    
    print(f"  温度传感器组件创建完成")

def create_radar_components(stage, sensor_path, config):
    """创建雷达组件"""
    # 雷达 - 长方体
    sensor = UsdGeom.Cube.Define(stage, sensor_path + "/sensor")
    sensor.CreateSizeAttr([config["geometry"]["width"], 
                          config["geometry"]["height"], 
                          config["geometry"]["depth"]])
    
    print(f"  雷达组件创建完成")

def create_multiple_sensors_demo():
    """演示：创建多个传感器"""
    print("\n=== 创建多个传感器演示 ===")
    
    # 定义要创建的传感器列表
    sensor_list = [
        "lidar",           # 主激光雷达
        "camera_front",    # 前向相机
        "camera_rear",     # 后向相机
        "ultrasonic_front", # 前向超声波
        "imu",             # IMU传感器
        "temperature",     # 温度传感器
        "radar_side"       # 侧向雷达
    ]
    
    print("将要创建的传感器:")
    for sensor in sensor_list:
        config = get_sensor_config(sensor)
        if config:
            print(f"  - {sensor}: {config['type']}")
    
    return sensor_list

def test_config_system():
    """测试配置系统"""
    print("\n=== 测试配置系统 ===")
    print("现在可以通过修改 sensor_config.py 来：")
    print("1. 调整现有传感器的位置和参数")
    print("2. 添加全新的传感器类型")
    print("3. 批量创建多个传感器")
    print("4. 动态调整传感器配置")
    
    print(f"\n可用的传感器类型:")
    all_types = SENSOR_FACTORY.get_all_sensor_types()
    for sensor_type in all_types:
        config = get_sensor_config(sensor_type)
        print(f"  - {sensor_type}: {config['type']}")

def main():
    """主函数"""
    print("=== 优化版本：使用配置文件管理任意传感器 ===")
    print("现在可以通过修改 sensor_config.py 来管理任意传感器！")
    
    # 设置场景
    setup_scene()
    simulation_context.reset()
    
    # 获取底盘位置
    chassis_path, chassis_pos = get_chassis_position()
    
    # 演示：创建多个传感器
    sensor_list = create_multiple_sensors_demo()
    
    # 批量创建传感器
    created_sensors = {}
    for sensor_type in sensor_list:
        try:
            sensor_path = create_sensor_from_config(
                simulation_context.get_stage(), chassis_path, chassis_pos, sensor_type
            )
            created_sensors[sensor_type] = sensor_path
            print(f"✓ {sensor_type} 创建成功: {sensor_path}")
        except Exception as e:
            print(f"✗ {sensor_type} 创建失败: {e}")
    
    print(f"\n=== 多传感器系统创建完成 ===")
    print(f"成功创建了 {len(created_sensors)} 个传感器！")
    
    # 测试配置系统
    test_config_system()
    
    print(f"\n传感器路径:")
    for sensor_type, path in created_sensors.items():
        print(f"  {sensor_type}: {path}")
    
    # 运行仿真
    while simulation_app.is_running():
        simulation_app.step(render=True)

if __name__ == "__main__":
    main()