# Copyright (c) 2024 ETH Zurich (Robotic Systems Lab)
# Author: Pascal Roth, Ziqi Fan
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""
This script demonstrates how to use the rigid objects class.
"""

"""Launch Isaac Sim Simulator first."""

import argparse

# omni-isaac-orbit
from omni.isaac.lab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(description="This script demonstrates how to use the camera sensor.")
parser.add_argument("--headless", action="store_true", default=False, help="Force display off at all times.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to spawn.")
args_cli = parser.parse_args()
args_cli.enable_cameras = True

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""

import os

import omni.isaac.lab.sim as sim_utils
from omni.isaac.lab.assets import ArticulationCfg, AssetBaseCfg
from omni.isaac.lab.scene import InteractiveScene, InteractiveSceneCfg
from omni.isaac.lab.sensors import CameraCfg
from omni.isaac.lab.sim import SimulationContext
from omni.isaac.lab.utils import configclass
from omni.viplanner.importer.importer import UnRealImporterCfg
from omni.viplanner.importer.sensors import DATA_DIR

##
# Pre-defined configs
##
from omni.isaac.lab_assets.anymal import ANYMAL_C_CFG  # isort: skip

"""
Environment Configuration
"""

USD_PATH = ""


@configclass
class TestTerrainCfg(InteractiveSceneCfg):
    """Configuration for a matterport terrain scene with a camera."""

    # ground terrain
    terrain = UnRealImporterCfg(
        prim_path="/World/Carla",
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
        ),
        usd_path=USD_PATH,
        duplicate_cfg_file=[
            os.path.join(DATA_DIR, "unreal", "town01", "cw_multiply_cfg.yml"),
            os.path.join(DATA_DIR, "unreal", "town01", "vehicle_cfg.yml"),
        ],
        sem_mesh_to_class_map=os.path.join(DATA_DIR, "unreal", "town01", "keyword_mapping.yml"),
        people_config_file=os.path.join(DATA_DIR, "unreal", "town01", "people_cfg.yml"),
    )
    # articulation
    robot: ArticulationCfg = ANYMAL_C_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    # camera
    semantic_camera = CameraCfg(
        prim_path="{ENV_REGEX_NS}/Robot/base/front_sem_cam",
        update_period=0,
        data_types=["semantic_segmentation"],
        debug_vis=True,
        offset=CameraCfg.OffsetCfg(pos=(0.419, -0.025, -0.020), rot=(0.992, 0.008, 0.127, 0.001), convention="world"),
        height=720,
        width=1280,
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24,
            horizontal_aperture=20.955,
        ),
    )
    depth_camera = CameraCfg(
        prim_path="{ENV_REGEX_NS}/Robot/base/front_depth_cam",
        update_period=0,
        data_types=["distance_to_image_plane"],
        debug_vis=False,
        offset=CameraCfg.OffsetCfg(pos=(0.419, -0.025, -0.020), rot=(0.992, 0.008, 0.127, 0.001), convention="world"),
        height=480,
        width=848,
        spawn=sim_utils.PinholeCameraCfg(
            focal_length=24,
            horizontal_aperture=20.955,
        ),
    )
    # extras - light
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DistantLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, 500.0)),
    )

    def __post_init__(self):
        """Post initialization."""
        # Set the initial robot position
        self.robot.init_state.pos = [110.0, 0.0, 0.6]


"""
Main
"""


def main():
    """Main function."""
    # Load kit helper
    sim_cfg = sim_utils.SimulationCfg()
    sim = SimulationContext(sim_cfg)
    # Set main camera
    sim.set_camera_view([130, -125, 10], [100, -130, 0.5])
    # Design scene
    scene_cfg = TestTerrainCfg(num_envs=args_cli.num_envs, env_spacing=2.0)
    scene = InteractiveScene(scene_cfg)
    # Play the simulator
    sim.reset()
    # Now we are ready!
    print("[INFO]: Setup complete...")

    # Define simulation stepping
    sim_dt = sim.get_physics_dt()
    # Simulation loop
    while simulation_app.is_running():
        # set joint targets
        scene.articulations["robot"].set_joint_position_target(
            scene.articulations["robot"].data.default_joint_pos.clone()
        )
        # write data to sim
        scene.write_data_to_sim()
        # Perform step
        sim.step()
        # Update buffers
        scene.update(sim_dt)


if __name__ == "__main__":
    # Run the main function
    main()
    # Close the simulator
    simulation_app.close()
