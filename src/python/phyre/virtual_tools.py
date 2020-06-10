import pymunk as pm
import phyre.creator as creator_lib
from phyre.creator import constants
import numpy as np

VT_SCALE = 600.
PHYRE_SCALE = constants.SCENE_WIDTH

def _isleft(spt, ept, testpt):
    seg1 = (ept[0]-spt[0], ept[1]-spt[1])
    seg2 = (testpt[0]-spt[0], testpt[1]-spt[1])
    cross = seg1[0]*seg2[1]-seg1[1]*seg2[0]
    return cross > 0

def segs2Poly(seglist, r):
    vlist = [pm.Vec2d(v) for v in seglist]
    # Start by figuring out the initial edge (ensure ccw winding)
    iseg = vlist[1] - vlist[0]
    ipt = vlist[0]
    iang = iseg.angle
    if iang <= (-np.pi / 4.) and iang >= (-np.pi * 3. / 4.):
        # Going downwards
        prev1 = (ipt.x - r, ipt.y)
        prev2 = (ipt.x + r, ipt.y)
    elif iang >= (np.pi / 4.) and iang <= (np.pi * 3. / 4.):
        # Going upwards
        prev1 = (ipt.x + r, ipt.y)
        prev2 = (ipt.x - r, ipt.y)
    elif iang >= (-np.pi / 4.) and iang <= (np.pi / 4.):
        # Going rightwards
        prev1 = (ipt.x, ipt.y - r)
        prev2 = (ipt.x, ipt.y + r)
    else:
        # Going leftwards
        prev1 = (ipt.x, ipt.y + r)
        prev2 = (ipt.x, ipt.y - r)

    polylist = []
    for i in range(1, len(vlist)-1):
        pi = vlist[i]
        pim = vlist[i-1]
        pip = vlist[i+1]
        sm = pim - pi
        sp = pip - pi
        # Get the angle of intersection between two lines
        angm = sm.angle
        angp = sp.angle
        angi = (angm - angp) % (2*np.pi)
        # Find the midpoint of this angle and turn it back into a unit vector
        angn = (angp + (angi / 2.)) % (2*np.pi)
        if angn < 0:
            angn += 2*np.pi
        unitn = pm.Vec2d.unit()
        unitn.angle = angn
        xdiff = r if unitn.x >= 0 else -r
        ydiff = r if unitn.y >= 0 else -r
        next3 = (pi.x + xdiff, pi.y + ydiff)
        next4 = (pi.x - xdiff, pi.y - ydiff)
        # Ensure appropriate winding -- next3 should be on the left of next4
        if _isleft(prev2, next3, next4):
            tmp = next4
            next4 = next3
            next3 = tmp
        curr_poly = [prev1, prev2, next3, next4]
        curr_poly.reverse()
        polylist.append(curr_poly)
        prev1 = next4
        prev2 = next3

    # Finish by figuring out the final edge
    fseg = vlist[-2] - vlist[-1]
    fpt = vlist[-1]
    fang = fseg.angle
    if fang <= (-np.pi / 4.) and fang >= (-np.pi * 3. / 4.):
        # Coming from downwards
        next3 = (fpt.x - r, fpt.y)
        next4 = (fpt.x + r, fpt.y)
    elif fang >= (np.pi / 4.) and fang <= (np.pi * 3. / 4.):
        # Coming from upwards
        next3 = (fpt.x + r, fpt.y)
        next4 = (fpt.x - r, fpt.y)
    elif fang >= (-np.pi / 4.) and fang <= (np.pi / 4.):
        # Coming from rightwards
        next3 = (fpt.x, fpt.y - r)
        next4 = (fpt.x, fpt.y + r)
    else:
        # Coming from leftwards
        next3 = (fpt.x, fpt.y + r)
        next4 = (fpt.x, fpt.y - r)
    curr_poly = [prev1, prev2, next3, next4]
    curr_poly.reverse()
    polylist.append(curr_poly)
    return polylist

def addContainer(pgw, points, width, dynamic, goal_container=False):
    ## Containers are described by sets of segments in Virtual Tools
    ## Convert to set of multipolygons for PHYRE    
    ptlist = points
    r = width/2
    polylist = segs2Poly(ptlist, r)

    ## Since PHYRE does not allow "inside" relations, need to add an extra bar to the bottom
    ## of the container to mimic this behavior
    if goal_container:
        extra_poly = []
        for v in polylist[1]:
            extra_poly.append((v[0], v[1]+width*2))
        bottom_bid = pgw.add_convex_polygon(convert_phyre_tools_vertices(extra_poly), False)
    else:
        bottom_bid = None

    ## Rescale coordinates appropriately
    converted_polylist = [convert_phyre_tools_vertices(poly) for poly in polylist]
    bid = pgw.add_multipolygons(polygons=converted_polylist, dynamic=dynamic)

    return bottom_bid, bid

def convert_phyre_tools_vertices(verts_list):
    ## Rescale vertices to PHYRE coordinates
    all_verts = []
    for verts in verts_list:
        new_verts = tuple([v*PHYRE_SCALE/VT_SCALE for v in verts])
        all_verts.append(new_verts)
    return all_verts

def translateToPhyre(d):

  ## d is assumed to be a dictionary in Virtual Tools level format
  ## please 
  pgw = creator_lib.creator.TaskCreator()
  gcond = d['gcond']
  all_ids = {}
  for nm, o in d['objects'].items():
    if nm[0] != '_':
        density = o['density']
        dynamic = density == 1.0
        if dynamic:
            add_str = "dynamic "
        else:
            add_str = "static "

        if o['type'] == 'Poly':
            vertices = o['vertices']
            vertices.reverse()
            bid = pgw.add_convex_polygon(convert_phyre_tools_vertices(vertices), dynamic)

        elif o['type'] == 'Ball':
            add_str = add_str + 'ball '
            center_x = o['position'][0]*PHYRE_SCALE/VT_SCALE
            center_y = o['position'][1]*PHYRE_SCALE/VT_SCALE
            bid = pgw.add(add_str, scale=o['radius']*2/VT_SCALE, center_x=center_x, center_y=center_y)

        elif o['type'] == 'Container':
            bid, bbid =addContainer(pgw, o['points'], o['width'], dynamic, goal_container=gcond['goal']==nm)

        elif o['type'] == 'Compound':
            polys = o['polys']

            for p in polys:
                p.reverse()

            converted_polylist = [convert_phyre_tools_vertices(poly) for poly in polys]
            bid = pgw.add_multipolygons(polygons=converted_polylist, dynamic=dynamic)

        elif o['type'] == 'Goal':
            vertices = o['vertices']
            vertices.reverse()
            bid = pgw.add_convex_polygon(convert_phyre_tools_vertices(vertices), dynamic)
        else:
            raise Exception("Invalid object type for PHYRE given: ", o['type'])
        all_ids[nm] = bid

  if gcond['type'] == 'SpecificInGoal' and gcond['goal'] != 'Floor' and gcond['goal'] != 'Ground':
    container_id = all_ids[gcond['goal']]
    pgw.update_task(body1=all_ids[gcond['obj']], body2=container_id, relationships=[pgw.SpatialRelationship.TOUCHING])
  
  elif gcond['type'] == 'SpecificTouch' or (gcond['type'] == 'SpecificInGoal' and (gcond['goal'] == 'Floor' or gcond['goal']=='Ground')):
    pgw.update_task(body1=all_ids[gcond['obj']], body2=all_ids[gcond['goal']], relationships=[pgw.SpatialRelationship.TOUCHING])
  else:
    raise Exception("Invalid goal type for PHYRE given: ", gcond['type'])
  return pgw