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
parser.add_argument("--headless", action="store_true", default=True, help="Force display off at all times.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to spawn.")
args_cli = parser.parse_args()

# launch omniverse app
app_launcher = AppLauncher(headless=args_cli.headless)
simulation_app = app_launcher.app

"""Rest everything follows."""

from omni.viplanner.collectors.utils.environment3d_reconstruction import (
    EnvironmentReconstruction,
)
from omni.viplanner.collectors.utils.environment3d_reconstruction_cfg import (
    ReconstructionCfg,
)

DATA_DIR = "/home/ubuntu/workspaces/viplanner_ws/viplanner_data/training_dataset/town01"

if __name__ == "__main__":
    cfg = ReconstructionCfg()
    cfg.data_dir = DATA_DIR

    # start depth reconstruction
    depth_constructor = EnvironmentReconstruction(cfg)
    depth_constructor.depth_reconstruction()

    depth_constructor.save_pcd()
    depth_constructor.show_pcd()
