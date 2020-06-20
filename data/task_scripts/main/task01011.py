# Copyright (c) Facebook, Inc. and its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TableB"""
"""Template task in which you prevent something from falling so ball can roll into container."""
import numpy as np
import phyre.creator as creator_lib
import phyre.virtual_tools as vt

@creator_lib.define_task_template(
    seed=range(1000),
    version="2",
    search_params=dict(
        max_search_tasks=500,
        required_flags=['BALL:GOOD_STABLE'],
        excluded_flags=['BALL:TRIVIAL'],
    ),
)

def build_task(C, seed):
  rng = np.random.RandomState(seed=seed)
  slopeLeft = [200, 400]
  slopeRight = [100, 190]
  slopeWidth = [100, 300]
  goalHeightMin = 60
  goalWidth = [80, 150]
  strutHeightMin = 40 
  strutWid = [15, 40]
  floorH = 7.
  ## Make the slope
  sL = rng.uniform(slopeLeft[0], slopeLeft[1])
  sR = rng.uniform(slopeRight[0], slopeRight[1])
  sW = rng.uniform(slopeWidth[0], slopeWidth[1])
  slopeVerts = [[0,0], [0, sL], [sW, sR], [sW, 0]]

  ## Make the goal
  goalH = rng.uniform(goalHeightMin, sR)
  goalW = rng.uniform(goalWidth[0], goalWidth[1])
  goalL = vt.VT_SCALE - goalW + 5
  goalR = vt.VT_SCALE - 5
  goalVerts = [[goalL, goalH], [goalL, 5], [goalR, 5], [goalR, goalH]]

  ## Find the ball position
  bpos = [30, sL + 15]

  ## Make the falling table
  tabL = sW + 15
  tabR = vt.VT_SCALE - goalW - 8
  tabVerts = [[tabL, sR], [tabL, sR+10], [tabR, sR+10], [tabR, sR]]

  ## Make the strut
  strutH = rng.uniform(strutHeightMin, sR - 10)
  strutW = rng.uniform(strutWid[0], strutWid[1])
  strutL = rng.uniform(sW, (sW + goalL) / 2 -strutW)
  strutVerts = [[strutL, floorH], [strutL, strutH], [strutL+strutW, strutH], [strutL+strutW, floorH]]

  ## Make the world getting into the container
  slopeVerts.reverse()
  tabVerts.reverse()
  strutVerts.reverse()

  slope = C.add_convex_polygon(vt.convert_phyre_tools_vertices(slopeVerts), False)
  container, _ = vt.add_container(C, goalVerts, 10, False, False)
  ball = C.add('dynamic ball', 30./vt.VT_SCALE, center_x=bpos[0]*C.scene.width/vt.VT_SCALE, center_y=bpos[1]*C.scene.height/vt.VT_SCALE)
  table = C.add_convex_polygon(vt.convert_phyre_tools_vertices(tabVerts),True)
  strut = C.add_convex_polygon(vt.convert_phyre_tools_vertices(strutVerts),True)

  floor = vt.add_box(C, [sW, 0, goalR, floorH], False)
  C.update_task(body1=ball,
                body2=floor,
                relationships=[C.SpatialRelationship.TOUCHING])

  C.set_meta(C.SolutionTier.VIRTUAL_TOOLS)