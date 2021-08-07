import random
import re
import json
import matplotlib.pyplot as plt
from PIL import Image
from adjustText import adjust_text
from collections import deque
from instr_template import *
from ai2thor_docker.x_server import startx
from ai2thor.controller import Controller


SCENES = ["FloorPlan_Train"+str(i)+"_"+str(j) for i in range(1,13) for j in range(1,6)]

BACKGROUND_OBJECT_TYPES = {
    'TVStand',
    'Pillow',
    'AlarmClock',
    'BasketBall',
    'Sofa',
    'ShelvingUnit',
    'Vase',
    'Television',
    'CoffeeTable',
    'Watch',
    'Dresser',
    'DeskLamp',
    'Pen',
    'TennisRacket',
    'Newspaper',
    'Fork',
    'Chair',
    'CellPhone',
    'Box',
    'Laptop',
    'BaseballBat',
    'Drawer',
    'Shelf',
    'RemoteControl',
    'HousePlant',
    'Desk',
    'CD',
    'Mug',
    'Statue',
    'ButterKnife',
    'Bowl',
    'Cup',
    'Pot',
    'SprayBottle',
    'Bed',
    'TeddyBear',
    'Painting',
    'SideTable',
    'Bottle',
    'DiningTable',
    'FloorLamp',
    'PepperShaker',
    'Book',
    'Pencil',
    'ArmChair',
    'SaltShaker',
    'Candle',
    'Apple',
    'Plate',
    'GarbageCan'
}

def find_path(start, end, controller): # start and end are dictionaries
    positions = controller.step("GetReachablePositions").metadata["actionReturn"]
    positions_tuple = [(p["x"], p["y"], p["z"]) for p in positions]

    grid_size = 0.25
    neighbors = dict()

    for position in positions_tuple:
        position_neighbors = set()
        for p in positions_tuple:
            if position != p and (
                (
                    abs(position[0] - p[0]) < 1.5 * grid_size
                    and abs(position[2] - p[2]) < 0.5 * grid_size
                )
                or (
                    abs(position[0] - p[0]) < 0.5 * grid_size
                    and abs(position[2] - p[2]) < 1.5 * grid_size
                )
            ):
                position_neighbors.add(p)
        neighbors[position] = position_neighbors
        
    def closest_grid_point(world_point):
        """
        Return the grid point that is closest to a world coordinate.
        Expects world_point=(x_pos, y_pos, z_pos). Note y_pos is ignored in the calculation.
        """
        def distance(p1, p2):   
            # ignore the y_pos
            # p1 is the tuple certainly
            if isinstance(p2, dict):
                p2 = p2['x'], p2['y'], p2['z']
            return ((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5
        
        min_dist = float("inf")
        closest_point = None
        assert len(positions_tuple) > 0
        for p in positions_tuple:
            dist = distance(p, world_point)
            if dist < min_dist:
                min_dist = dist
                closest_point = p

        return closest_point
        
    def shortest_path(start, end):
        """Expects the start=(x_pos, y_pos, z_pos) and end=(x_pos, y_pos, z_pos).

        Note y_pos is ignored in the calculation.
        """
        start = closest_grid_point(start)
        end = closest_grid_point(end)

        if start == end:
            return [start]

        q = deque()
        q.append([start])

        visited = set()

        while q:
            path = q.popleft()
            pos = path[-1]

            if pos in visited:
                continue

            visited.add(pos)
            for neighbor in neighbors[pos]:
                if neighbor == end:
                    return path + [neighbor]
                q.append(path + [neighbor])

        raise Exception("Invalid state. Must be a bug!")
    
    return shortest_path(start, end)

# first find out the actions taken from the start to end of the path
# one point one set of actions
def get_actions(grid_path):
    actions = []
    cur_rot = 0
    for i in range(len(grid_path)):
        action = dict()
        action['moveahead'] = True
        if i == len(grid_path) - 1:
            action['moveahead'] = False
            action['rotation'] = 'Done'
            actions.append(action)
            continue
        del_x, del_z = grid_path[i+1][0] - grid_path[i][0], grid_path[i+1][2] - grid_path[i][2]
        if del_x > 0:
            if cur_rot == 0:
                action['rotation'] = 'RotateRight'
                cur_rot = (cur_rot + 90) % 360
            elif cur_rot == 90:
                action['rotation'] = 'None'
            elif cur_rot == 180:
                action['rotation'] = 'RotateLeft'
                cur_rot = (cur_rot - 90) % 360
            else:
                action['rotation'] = ('RotateRight', 'RotateRight')
                cur_rot = (cur_rot + 180) % 360
            
        elif del_x < 0:
            if cur_rot == 0:
                action['rotation'] = 'RotateLeft'
                cur_rot = (cur_rot - 90) % 360
            elif cur_rot == 180:
                action['rotation'] = 'RotateRight'
                cur_rot = (cur_rot + 90) % 360
            elif cur_rot == 270:
                action['rotation'] = 'None'
            else:
                action['rotation'] = ('RotateRight', 'RotateRight')
                cur_rot = (cur_rot + 180) % 360
        
        elif del_z > 0:
            if cur_rot == 0:
                action['rotation'] = 'None'
            elif cur_rot == 90:
                action['rotation'] = 'RotateLeft'
                cur_rot = (cur_rot - 90) % 360
            elif cur_rot == 270:
                action['rotation'] = 'RotateRight'
                cur_rot = (cur_rot + 90) % 360
            else:
                action['rotation'] = ('RotateRight', 'RotateRight')
                cur_rot = (cur_rot + 180) % 360
        
        elif del_z < 0:
            if cur_rot == 90:
                action['rotation'] = 'RotateRight'
                cur_rot = (cur_rot + 90) % 360
            elif cur_rot == 180:
                action['rotation'] = 'None'
            elif cur_rot == 270:
                action['rotation'] = 'RotateLeft'
                cur_rot = (cur_rot - 90) % 360
            else:
                action['rotation'] = ('RotateRight', 'RotateRight')
                cur_rot = (cur_rot + 90) % 360  
        
        actions.append(action)
    
    return actions

def visualise(grid_path, controller, filename='path.png'):
    # plotting all accessible points on graph
    plt.figure()
    event = controller.step(action="GetReachablePositions")
    positions = event.metadata["actionReturn"]
    x = [p['x'] for p in positions]
    z = [p['z'] for p in positions]
    plt.scatter(x, z, alpha=0.75)

    xs = [p[0] for p in grid_path]
    zs = [p[2] for p in grid_path]
    plt.scatter(xs, zs, alpha=0.5)

    plt.scatter(xs[0], zs[0], color='green')
    plt.scatter(xs[-1], zs[-1], color='red')

    objs = [(obj['objectType'], obj['position']) for obj in controller.last_event.metadata['objects']]
    obj_pos_x = [obj[1]['x'] for obj in objs]
    obj_pos_z = [obj[1]['z'] for obj in objs]
    obj_name = [re.sub(r'\d+', '', obj[0].replace('_', ' ')) for obj in objs]

    plt.scatter(obj_pos_x, obj_pos_z, alpha=0.25)
    texts = []
    for x, z, name in zip(obj_pos_x, obj_pos_z, obj_name):
        texts.append(plt.text(x, z, name))
    
    adjust_text(texts, only_move={'texts':'xy'}, arrowprops=dict(arrowstyle="->", color='r', lw=0.5))
    print(filename)
    plt.savefig(filename)
    print('figure saved as', filename)

def distance(grid_path):
    return 0.25 * (len(grid_path) - 1)

def L2distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5

def create_path(controller):
    grid_path = []
    visited_objs = []
    positions = controller.step(action='GetReachablePositions').metadata['actionReturn']
    init_pos = random.choice(positions)
    event = controller.step(action='Teleport', position=init_pos, \
                            rotation=dict(x=0, y=0, z=0))
    nearest_pos_obj = {obj['objectType']: find_path(obj['position'], obj['position'], controller)[0] for \
                       obj in event.metadata['objects']}
    obj_pos = {obj['objectType']: (obj['position']['x'], obj['position']['y'], obj['position']['z']) for \
               obj in event.metadata['objects']}

    # 1 single grid path and plot points in between
    while distance(grid_path) < 7.0:
        init_pos = random.choice(positions) 
        event = controller.step(action='Teleport', position=init_pos, \
                            rotation=dict(x=0, y=0, z=0))
        grid_path = find_path(init_pos, nearest_pos_obj[random.sample(nearest_pos_obj.keys(), 1)[0]], controller)

    action_list = get_actions(grid_path)

    for i, point in enumerate(grid_path):
        items = [obj for obj in controller.last_event.class_detections2D.keys() if obj in BACKGROUND_OBJECT_TYPES]
        # print(controller.last_event.metadata['agent']['position'])
        # print(items)
        # img = Image.fromarray(controller.last_event.frame, 'RGB')
        # img.save(str(controller.last_event.metadata['agent']['position'])+'.png')
        # print('---------------------------------------------------')
        if action_list[i]['rotation'] == 'Done':
            controller.step('Done')
        elif action_list[i]['rotation'] == 'None':
            controller.step('MoveAhead')
        else:
            if isinstance(action_list[i]['rotation'], tuple):
                controller.step('RotateRight', degree=180)
            else:
                controller.step(action_list[i]['rotation'])
            controller.step('MoveAhead')

        if i > 5:
            for key, value in obj_pos.items():
                if L2distance(point, value) < 1.2 and key in items:
                    visited_objs.append((point, action_list[i], key))

    # visualise(grid_path, controller)
    rotations = [item for item in visited_objs if item[1]['rotation'] == 'RotateRight' or \
                 item[1]['rotation'] == 'RotateLeft']
    if len(rotations) < 2:
        raise Exception('Number of choices less than minimum')
        
    chosen = [rotations[i] for i in sorted(random.sample(range(len(rotations)), 2))]

    i=0
    while L2distance(chosen[0][0],chosen[1][0]) < 2:
        if i > 50:
            raise Exception('All distances below 2')
        chosen = random.choices(rotations, k=2)
        i+=1
    chosen.append(visited_objs[-1])
    direction = ['right' if item[1]['rotation'] == 'RotateRight' else 'left' for item in chosen]

    sens = sentence_template(len(chosen))
    for i, sen in enumerate(sens):
        sens[i] = sen.replace('<blank>', chosen[i][2]).replace('<dir>', direction[i])
    
    return grid_path, sens, distance(grid_path)

    # 2 find 4 random objescts and construct path from there
    '''
    dist_mtx = [[] for _ in range(len(nearest_pos_obj.keys()))]
    idx_to_obj = dict()
    for i, key1 in enumerate(nearest_pos_obj.keys()):
        idx_to_obj[i] = key1
        for key2 in nearest_pos_obj.keys():
            path = find_path(nearest_pos_obj[key1], nearest_pos_obj[key2], controller)
            dist_mtx[i].append(distance(path))

    path_ids = []

    while len(path_ids) != 4:
        if len(path_ids) == 0:
            candidates = [i for i in range(len(dist_mtx))]
        else:
            candidates = [i for i, candidate in enumerate(dist_mtx[path_ids[-1]]) if 2.5 < candidate < 5 \
                          and i not in path_ids]
    
        if len(candidates) == 0:
            path_ids.pop(-1)
            continue

        candidate = random.choice(candidates)
        path_ids.append(candidate)

    path_1 = find_path(nearest_pos_obj[idx_to_obj[path_ids[0]]], nearest_pos_obj[idx_to_obj[path_ids[1]]], \
             controller)
    path_2 = find_path(nearest_pos_obj[idx_to_obj[path_ids[1]]], nearest_pos_obj[idx_to_obj[path_ids[2]]], \
             controller)
    grid_path = path_1[:-1] + path_2
    '''
    
    # 3 go to each point, see what is visible and find the next one
    '''
    while distance(grid_path) < 7.0:
        objs_dist = {obj['objectType']: distance(find_path(init_pos, nearest_pos_obj[obj['objectType']], controller)) \
                     for obj in event.metadata['objects']}

        objs = [obj for obj in event.class_detections2D.keys() if obj in BACKGROUND_OBJECT_TYPES \
                and obj not in visited_objs and 1.0 <= objs_dist[obj] <= 3.0]

        while len(objs) == 0:
            event = controller.step(action='RotateRight')
            objs = [obj for obj in event.class_detections2D.keys() if obj in BACKGROUND_OBJECT_TYPES \
                    and obj not in visited_objs and 1.0 <= objs_dist[obj] <= 3.0]
     
        target_obj = random.choice(objs)
        for obj in controller.last_event.metadata['objects']:
            if obj['objectType'] == target_obj:
                target_obj_pos = obj['position']
        new_path = find_path(init_pos, target_obj_pos, controller)
        grid_path.extend(new_path)
        action_list = get_actions(new_path)

        while action_list:
            controller.step(action=action_list[0])
            action_list.pop(0)

        randomact = random.choice(['RotateRight', 'RotateLeft'])
        critical_acts.append(randomact)
        event = controller.step(action=randomact)
        init_pos = dict(x=grid_path[-1][0], y=grid_path[-1][1], z=grid_path[-1][2])
        visited_objs.append(target_obj)
    '''  

    # 4 A different approach that I cannot remember 
    '''
    def return_action(cur_pos, positions_tuple):
        forward = cur_pos[0]+0.25, cur_pos[1], cur_pos[2]
        backward = cur_pos[0]-0.25, cur_pos[1], cur_pos[2]
        left = cur_pos[0], cur_pos[1], cur_pos[2]+0.25
        right = cur_pos[0], cur_pos[1], cur_pos[2]-0.25

        result = []
        total = [forward, backward, left, right]
        for item in total:
            if item in positions_tuple:
                result.append(item)

        return result

    def L2distance(p1, p2):
        return ((p1[0] - p2[0]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5

    def check_validity(controller, action, position_tuples):
        event = controller.step(action)
        cur_pos = event.metadata['agent']['position']['x'], event.metadata['agent']['position']['y'], \
                  event.metadata['agent']['position']['z'],
        
        if action == 'RotateRight':
            controller.step('RotateLeft')
        elif action == 'RotateLeft':
            controller.step('RotateRight')
        elif action == 'MoveAhead':
            controller.step('RotateRight', degree=180)
            controller.step('MoveAhead')

        if cur_pos in position_tuples and event.metadata['lastActionSuccess']:
            return True
        else:
            return False

    positions_tuple = [(p["x"], p["y"], p["z"]) for p in positions]
    idx = 0
    # init_pos = random.choice(positions_tuple)
    
    init_pos = random.choice(positions) # a dictionary
    init_pos = init_pos['x'], init_pos['y'], init_pos['z']
    # actions = ['MoveAhead', 'RotateLeft', 'RotateRight']
    
    while distance(grid_path) < 7.0:
        # already have an init_pos in dict format
        grid_path.append(init_pos)
        positions_tuple.remove(init_pos)
        actions = return_action(init_pos, positions_tuple)
        distance_to_obj = {key: L2distance(init_pos, value) for key,value in nearest_pos_obj.items()}
        for key,value in distance_to_obj.items():
            if value < 1.0:
                visited_objs.append((idx, key))
        if len(actions) == 0:
            break
        init_pos = random.choice(actions)
        idx +=1
    '''

startx()
controller = Controller(
    agentMode="locobot",
    visibilityDistance=10,
    scene=SCENES[0],
    gridSize=0.25,
    snapToGrid=True,
    movementGaussianSigma=0.001,
    rotateStepDegrees=90,
    rotateGaussianSigma=0.001,
    renderDepthImage=False,
    renderInstanceSegmentation=True,
    width=640,
    height=480,
    fieldOfView=120
)

i = 0
for scene in SCENES:
    instructions = []
    controller.reset(scene=scene)
    print(f'Beginning instruction creation for {scene}')

    while len(instructions) < 500:
        scene_instr = dict()
        try:
            path, instr, dist = create_path(controller)
            scene_instr['instr_id'] = i
            scene_instr['shortest_path'] = path
            scene_instr['init_pos'] = path[0]
            scene_instr['phrase'] = instr
            scene_instr['dist'] = dist
            scene_instr['scene'] = scene
            instructions.append(scene_instr)
            i += 1
            print(f'{i} instruction(s) created')

        except Exception:
            pass
    
    with open(scene+'.json', 'w') as f:
        json.dump(instructions, f)
        print('File created')