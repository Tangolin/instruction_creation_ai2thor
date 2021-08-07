import numpy as np
from ai2thor_docker.x_server import startx
from ai2thor.controller import Controller
from ai2thor.util.metrics import get_shortest_path_to_object_type

# def find_shortest_path(cur_pos, target, con):
#     # both cur_pos and target are arrays as well
#     xround = lambda x: round(x*4)/4
#     rel_dir = target - cur_pos
#     del_x, del_z = rel_dir[0], rel_dir[2]
#     del_x, del_z = xround(del_x), xround(del_z)
#     x_mov, z_mov = int(abs(del_x / 0.25)), int(abs(del_z / 0.25))

#     move1 = [] # follow x then z
#     move2 = [] # follow z then x

#     if del_x < 0:
#         move1.append('RotateLeft')
#     elif del_x > 0:
#         move1.append('RotateRight')
    
#     move1.extend(['MoveAhead'] * x_mov)
    
#     if len(move1) != 0:
#         if del_x < 0:
#             if del_z > 0:
#                 move1.append('RotateRight')
#             elif del_z < 0:
#                 move1.append('RotateLeft')
        
#         elif del_x > 0:
#             if del_z > 0:
#                 move1.append('RotateLeft')
#             elif del_z < 0:
#                 move1.append('RotateRight')
    
#     else:
#         if del_z < 0:
#             move1.extend(['RotateLeft'] * 2)
        
#     move1.extend(['MoveAhead'] * z_mov)

#     if del_z < 0:
#         move2.extend(['RotateLeft'] * 2)
    
#     move2.extend(['MoveAhead'] * z_mov)

#     if 'RotateLeft' in move2:
#         if del_x > 0:
#             move2.append('RotateLeft')
        
#         elif del_x < 0:
#             move2.append('RotateRight')
    
#     else:
#         if del_x > 0:
#             move2.append('RotateRight')
        
#         elif del_x < 0:
#             move2.append('RotateLeft')
    
#     move2.extend(['MoveAhead'] * x_mov)

#     move1.append('Done')
#     move2.append('Done')

#     con.step(action='Teleport', rotation=dict(x=0, y=0, z=0))
#     init_pos = con.last_event.metadata['agent']['position']

#     def minifunc(move):
#         movesucc = True

#         for step in move:
#             if step == 'RotateRight':
#                 con.step(action='RotateRight', degrees=90)
#             elif step == 'RotateLeft':
#                 con.step(action='RotateLeft', degrees=90)
#             elif step == 'MoveAhead':
#                 con.step(action='MoveAhead', moveMagnitude=0.25)
            
#             if not con.last_event.metadata['lastActionSuccess']:
#                 movesucc = False
#                 break
        
#         con.step(action='Teleport', position=init_pos, rotation=dict(x=0, y=0, z=0))
#         return movesucc
    
#     move1succ = minifunc(move1)
#     move2succ = minifunc(move2)

#     if move1succ:
#         return move1
    
#     elif move2succ:
#         return move2
    
#     else:
#         return None


# vectors = []
# for i in range(len(x)):
#     if i == len(x)-1:
#         continue
#     vectors.append([x[i+1]-x[i], z[i+1]-z[i]])

# angles = []
# for vector in vectors:
#     angle = np.arctan(vector[0]/(vector[1]+0.00001)) * (180/np.pi)
#     if angle < 0:
#         angle = 360 + angle
#     angles.append(angle)

# print('angles:\t', angles)

# done = False
# i = 4

# controller.step(action='Teleport', position=path[i], \
#                 rotation=dict(x=0, y=0, z=0))
# cur_pos = controller.last_event.metadata['agent']['position']
# print('rotation', controller.last_event.metadata['agent']['rotation'])
# cur_pos = np.array(list(path[i].values()))
# target = np.array(list(path[i+1].values()))

# print(find_shortest_path(cur_pos, target, controller))
# while not done:
#     print('Next point:')
#     target = np.array(list(path[i+1].values()))
#     controller.step(action='Teleport', position=path[i], rotation=dict(x=0, y=angles[i], z=0))
#     # print(angles[i])
#     cur_pos = controller.last_event.metadata['agent']['position']
#     # print('rotation', controller.last_event.metadata['agent']['rotation'])
#     cur_pos = np.array(list(cur_pos.values()))
#     distance = np.linalg.norm(cur_pos - target, ord=2, axis=0)

#     while distance > 0.15:
#         print('target', target)

#         print('last action', controller.last_event.metadata['lastAction'])
#         print(controller.last_event.metadata['lastActionSuccess'])
#         controller.step(action='MoveAhead')
#         cur_pos = controller.last_event.metadata['agent']['position']
#         if controller.last_event.metadata['lastActionSuccess'] == True:
#             print('no error')
#         else:
#             print(controller.last_event.metadata['errorMessage'])
#         print('current position', cur_pos)
#         print('current rotation', controller.last_event.metadata['agent']['rotation'])
#         cur_pos = np.array(list(cur_pos.values()))
#         distance = np.linalg.norm(cur_pos - target, ord=2, axis=0)
#         print(distance)
#         input()
#         print('-----------------------------------------------')
#         if i == len(path) - 1:
#             done = True
    
#     i += 1