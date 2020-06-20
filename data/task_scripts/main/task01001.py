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

"""Bridge"""
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
  leftWall = [80, 180]
  breakPoint = [0.1, 0.9]
  bridgeLength = [150, 300]
  slopeL = [60, 200]
  slopeR = [250, 400]

  ## Make the goal container
  height = rng.uniform(slopeL[0], slopeL[1])
  lW = rng.uniform(leftWall[0], leftWall[1])
  container, _ = vt.add_container(C, [[5, height], [5, 5], [lW-5, 5], [lW-5, height]], 10, False, True)#'green', 0)

  ## Make the left wall
  lw1 = vt.add_box(C, [lW, 0, lW+70, height-10], False)
  lw2 = vt.add_box(C, [lW, height-10, lW+20, height], False)

  ## Make the bridge
  bL = rng.uniform(bridgeLength[0], bridgeLength[1])
  bP = rng.uniform(breakPoint[0], breakPoint[1])
  bridgeL = vt.add_box(C, [lW+20+2, height+10, lW+20+2+bL*bP, height+20], True)
  bridgeR = vt.add_box(C, [lW+20+2+bL*bP+2, height+10, lW+20+2+bL+2, height+20], True)

  ## Make the right wall
  sW = rng.uniform(min([lW+20+2+bL+2+50, vt.VT_SCALE-30]), max([vt.VT_SCALE - 30, lW+20+2+bL+2+50]))
  rw1 = vt.add_box(C, [sW-50, 0, vt.VT_SCALE, height - 10], False)

  ## Make the slope
  sR = rng.uniform(slopeR[0], slopeR[1])
  slopeVerts = [(sW, height-10), (sW, height), (vt.VT_SCALE, sR), (vt.VT_SCALE, height-10)]
  slopeVerts.reverse()

  rw2 = C.add_convex_polygon(vt.convert_phyre_tools_vertices(slopeVerts), False)

  ball = C.add('dynamic ball', 15*2./vt.VT_SCALE, center_x=550*C.scene.width/vt.VT_SCALE, center_y=450*C.scene.width/vt.VT_SCALE)

  C.update_task(
        body1=ball,
        body2=container,
        relationships=[C.SpatialRelationship.TOUCHING])
  C.set_meta(C.SolutionTier.VIRTUAL_TOOLS)