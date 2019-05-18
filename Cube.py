import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Rectangle

color_dict = {0 : 'white',  1 : 'orange', 2 : 'blue',
              3 : 'yellow', 4 : 'red',    5 : 'green',
              'white'  : 0, 'orange' : 1, 'blue' :  2,
              'yellow' : 3, 'red'    : 4, 'green' : 5}
    
face_dict = {0 : 'front', 1 : 'right', 2 : 'back',
             3 : 'left',  4 : 'up',    5 : 'down',
             'front' : 0, 'right' : 1, 'back' : 2,
             'left'  : 3, 'up'    : 4, 'down' : 5} 

face_normals = {'front' : np.array([ 0, -1,  0], dtype=int),
                'back'  : np.array([ 0,  1,  0], dtype=int),
                'left'  : np.array([-1,  0,  0], dtype=int),
                'right' : np.array([ 1,  0,  0], dtype=int),
                'up'    : np.array([ 0,  0,  1], dtype=int),
                'down'  : np.array([ 0,  0, -1], dtype=int)}

color_names = ['white', 'orange', 'blue', 'yellow', 'red', 'green']

idx_edge_pieces = [(f,i_f,j_f) for f in range(6)
                   for i_f in range(3)
                   for j_f in range(3)
                   if (i_f == 1 or j_f == 1) and i_f != j_f]

idx_corner_pieces = [(f, i_f, j_f) for f in range(6)
                     for i_f in range(3)
                     for j_f in range(3)
                     if (i_f != 1 and j_f != 1)]

idx_center_pieces = [(f, 1, 1) for f in range(6)]

class Cube:
    pts = np.zeros((54, 3), dtype='int')
    squares = np.zeros((6, 3, 3), dtype='int')
    cs  = []
    
    def __init__(self):
        idx = 0    
        for x in [-2, 0, 2]:
            for y in [-2, 0, 2]:
                for s, c in enumerate(color_names):
                    z = (-1)**s * 3

                    # Fill point array
                    self.pts[idx, (idx+0) % 3] = x
                    self.pts[idx, (idx+1) % 3] = y
                    self.pts[idx, (idx+2) % 3] = z
                    self.cs.append(c)

                    # Fill face array
                    f, i_f, j_f = self.point_to_square_idx(self.pts[idx,:])
                    self.squares[f, i_f, j_f] = color_dict[c]
                    
                    # Advance index
                    idx += 1
                    
    def point_to_square_idx(self, pt):
        x,y,z = pt
        if   z ==  3:
            return face_dict['up'], int((2+x) / 2), int((2+y) / 2)
        elif z == -3:
            return face_dict['down'], int((2+x) / 2), 2 - int((2+y) / 2)
        elif x ==  3:
            return face_dict['right'], int((2+y) / 2), int((2+z) / 2)
        elif x == -3:
            return face_dict['left'], 2 - int((2+y) / 2), int((2+z) / 2)
        elif y ==  3:
            return face_dict['back'], 2 - int((2+x) / 2), int((2+z) / 2)
        elif y == -3:
            return face_dict['front'], int((2+x) / 2), int((2+z) / 2)

    def square_idx_to_point(self, idx):
        f,i,j = idx        
        if   face_dict[f] == 'up':
            return np.array([2*i-2,  2*j-2, 3], dtype='int')
        elif face_dict[f] == 'down':
            return np.array([2*i-2,  2-2*j, -3], dtype='int')
        elif face_dict[f] == 'right':
            return np.array([3, 2*i-2, 2*j-2], dtype='int')            
        elif face_dict[f] == 'left':
            return np.array([-3, 2-2*i, 2*j-2], dtype='int')
        elif face_dict[f] == 'back':
            return np.array([2-2*i,  3, 2*j-2], dtype='int')
        elif face_dict[f] == 'front':
            return np.array([2*i-2, -3, 2*j-2], dtype='int')                    

    def face_of_idx(self, idx):
        return idx[0]

    def edge_of_idx(self, idx):
        pass
        
    def update_squares(self, idx_rot):
        for idx in idx_rot:
            f, i_f, j_f = self.point_to_square_idx(self.pts[idx, :])
            self.squares[f, i_f, j_f] = color_dict[self.cs[idx]]

    def rotate_face_to_face(self, f1, f2):
        # same faces, so nohting to do:
        if f1 == f2:
            pass

        # faces to switch:
        else :
            n1 = face_normals[f1]
            n2 = face_normals[f2]
            rot_ax = np.cross(n1, n2)

            # Zero rot_ax implies n1 and n2 are opposite faces
            # and means we need to determine the rotation axis
            if int(np.linalg.norm(rot_ax)) == 0:

                # If n1 is parallel to x or y, we rotate 180 about z
                if abs(n1[0]) == 1 or abs(n1[1]) == 1:
                    rot_ax = face_normals['up']
                    n_rot  = 2

                # If n1 is parallel to z, we rotate 180 about x
                if abs(n1[2]) == 1:
                    rot_ax = face_normals['right']
                    n_rot  = 2

            # they're distinct faces, and we just need a single rotation
            else:
                if min(rot_ax) < 0:
                    n_rot = 1
                else:
                    n_rot = -1
        
            # perform rotation
            if   abs(rot_ax[2]) == 1:
                self.rotate_z(n_rot)
            elif abs(rot_ax[0]) == 1:
                self.rotate_x(n_rot)
            elif abs(rot_ax[1]) == 1:
                self.rotate_y(-n_rot)


    def rotate_face_edge_to_edge(self, f, e1, e2):
        # same faces, so nohting to do:
        if e1 == e2:
            pass

        # faces to switch:
        else :
            n1 = face_normals[e1]
            n2 = face_normals[e2]
            rot_ax = np.cross(n1, n2)

            # Zero rot_ax implies n1 and n2 are opposite faces
            # and means we need to determine the rotation axis
            if int(np.linalg.norm(rot_ax)) == 0:

                # If n1 is parallel to x or y, we rotate 180 about z
                if abs(n1[0]) == 1 or abs(n1[1]) == 1:
                    rot_ax = face_normals['up']
                    n_rot  = 2

                # If n1 is parallel to z, we rotate 180 about x
                if abs(n1[2]) == 1:
                    rot_ax = face_normals['right']
                    n_rot  = 2

            # they're distinct faces, and we just need a single rotation
            else:
                if min(rot_ax) < 0:
                    n_rot = 1
                else:
                    n_rot = -1
        
            # perform rotation
            if   abs(rot_ax[2]) == 1:
                self.rotate_z(n_rot, edge=f)
            elif abs(rot_ax[0]) == 1:
                self.rotate_x(n_rot, edge=f)
            elif abs(rot_ax[1]) == 1:
                self.rotate_y(-n_rot, edge=f)
                
            
    def rotate_up(self, n):
        self.rotate_z(n, 'up')
    
    def rotate_down(self, n):
        self.rotate_z(n, 'down')
        
    def rotate_left(self, n):
        self.rotate_x(n, 'left')
    
    def rotate_right(self, n):
        self.rotate_x(n, 'right')      
    
    def rotate_front(self, n):
        self.rotate_y(n, 'front')
    
    def rotate_back(self, n):
        self.rotate_y(n, 'back')              
        
    def rotate_x(self, n, edge = None):
        if edge in ['right', face_dict['right']]:
            idx_rot, = np.where(self.pts[:, 0] >=  2)
        elif edge in ['left', face_dict['left']]:
            idx_rot, = np.where(self.pts[:, 0] <= -2)
        else:
            idx_rot = np.arange(0, 54)
            
        theta = n * (np.pi / 2)
        M = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta),  np.cos(theta)]],
                     dtype='int')
        fs_rot = np.dot(self.pts[idx_rot, 1:], M)
        self.pts[idx_rot, 1:] = fs_rot
        self.update_squares(idx_rot)

    
    def rotate_y(self, n, edge = None):
        if edge in ['front', face_dict['front']]:
            idx_rot, = np.where(self.pts[:, 1] <= -2)
        elif edge in ['back', face_dict['back']]:
            idx_rot, = np.where(self.pts[:, 1] >= 2)
        else:
            idx_rot = np.arange(0, 54)
            
        theta = n * (np.pi / 2)
        M = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta),  np.cos(theta)]],
                     dtype='int')
        fs_rot = np.dot(self.pts[idx_rot, 0::2], M)
        self.pts[idx_rot, 0::2] = fs_rot
        self.update_squares(idx_rot)
    
    def rotate_z(self, n, edge=None):
        if edge in ['up', face_dict['up']]:
            idx_rot, = np.where(self.pts[:, 2] >=  2)
        elif edge in ['down', face_dict['down']]:
            idx_rot, = np.where(self.pts[:, 2] <= -2)
        else:
            idx_rot = np.arange(0, 54)            
            
        theta = n * (np.pi / 2)
        M = np.array([[np.cos(theta), -np.sin(theta)],
                      [np.sin(theta),  np.cos(theta)]],
                     dtype='int')
        fs_rot = np.dot(self.pts[idx_rot, 0:2], M)
        self.pts[idx_rot, 0:2] = fs_rot
        self.update_squares(idx_rot)

    def center_piece_idx(self, c):
        idx_list = [idx for idx in idx_center_pieces if color_dict[self.squares[idx]] == c]
        return idx_list[0]        
        
    def edge_piece_idx(self, c):
        return [idx for idx in idx_edge_pieces if color_dict[self.squares[idx]] == c]
    
    def corner_piece_idx(self, c):
        return [idx for idx in idx_corner_pieces if color_dict[self.squares[idx]] == c]

    
    def edge_piece_adj_idx(self, idx):
        f, i_f, j_f = idx

        if face_dict[f] == 'up':
            if   i_f == 1 and j_f == 0:
                return (face_dict['front'],  1, 2)
            elif i_f == 1 and j_f == 2:
                return (face_dict['back'], 1, 2)                
            elif i_f == 0 and j_f == 1:
                return (face_dict['left'],  1, 2)
            elif i_f == 2 and j_f == 1:
                return (face_dict['right'], 1, 2)
            
        elif face_dict[f] == 'down':
            if   i_f == 1 and j_f == 0:
                return (face_dict['back'], 1, 0)
            elif i_f == 1 and j_f == 2:
                return (face_dict['front'],  1, 0)                
            elif i_f == 0 and j_f == 1:
                return (face_dict['left'],  1, 0)
            elif i_f == 2 and j_f == 1:
                return (face_dict['right'], 1, 0)             

        elif face_dict[f] == 'left':
            if   i_f == 1 and j_f == 0:
                return (face_dict['down'], 0, 1)
            elif i_f == 1 and j_f == 2:
                return (face_dict['up'],  0, 1)                
            elif i_f == 0 and j_f == 1:
                return (face_dict['back'],  2, 1)
            elif i_f == 2 and j_f == 1:
                return (face_dict['front'], 0, 1)             

        elif face_dict[f] == 'right':
            if   i_f == 1 and j_f == 0:
                return (face_dict['down'], 2, 1)
            elif i_f == 1 and j_f == 2:
                return (face_dict['up'],  2, 1)                
            elif i_f == 0 and j_f == 1:
                return (face_dict['front'], 2, 1)
            elif i_f == 2 and j_f == 1:
                return (face_dict['back'], 0, 1)

        elif face_dict[f] == 'front':
            if   i_f == 1 and j_f == 0:
                return (face_dict['down'], 1, 2)
            elif i_f == 1 and j_f == 2:
                return (face_dict['up'],  1, 0)                
            elif i_f == 0 and j_f == 1:
                return (face_dict['left'],  2, 1)
            elif i_f == 2 and j_f == 1:
                return (face_dict['right'], 0, 1)
            
        elif face_dict[f] == 'back':
            if i_f == 0 and j_f == 1:
                return (face_dict['right'],  2, 1)
            elif i_f == 2 and j_f == 1:
                return (face_dict['left'], 0, 1)            
            elif i_f == 1 and j_f == 0:
                return (face_dict['down'], 1, 0)
            elif i_f == 1 and j_f == 2:
                return (face_dict['up'],  1, 2)                
            
    def edge_piece_solved(self, idx):
        ctr_pc = (idx[0], 1, 1)
        
        idx_adj = self.edge_piece_adj_idx(idx)
        ctr_pc_adj = (idx_adj[0], 1, 1)
        
        return self.squares[idx] == self.squares[ctr_pc] and self.squares[idx_adj] == self.squares[ctr_pc_adj]

    def edge_pieces_matching_color(self, c):
        return [ep for ep in idx_edge_pieces if color_dict[self.squares[ep]] == c or self.squares[ep] == c]

    def cloud_plot(self, ax=None):
        if ax is None:
            fig = plt.figure(figsize=(8,8))
            ax = fig.add_subplot(111, projection='3d')
        ax.scatter(self.pts[:,0], self.pts[:,1], self.pts[:,2], c = self.cs,
                   edgecolors='k', s =100)
        ax.set_xlim([-3.01,3.01])
        ax.set_ylim([-3.01,3.01])
        ax.set_zlim([-3.01,3.01])
        ax.axis('off')
        plt.axis('equal')
        return ax

    def cube_plot(self, ax=None):
        if ax is None:
            fig = plt.figure(figsize=(8,8))
            ax = fig.add_subplot(111, projection='3d')
        
        for idx, p in enumerate(self.pts):
            if abs(p[2]) > 2.5:
                xs = np.linspace(p[0]-1, p[0]+1, 2)
                ys = np.linspace(p[1]-1, p[1]+1, 2)                
                xs,ys = np.meshgrid(xs,ys)
                zs = p[2] * np.ones(np.shape(xs))

            if abs(p[0]) > 2.5:
                ys = np.linspace(p[1]-1, p[1]+1, 2)
                zs = np.linspace(p[2]-1, p[2]+1, 2)                
                ys,zs = np.meshgrid(ys,zs)
                xs = p[0] * np.ones(np.shape(zs))

            if abs(p[1]) > 2.5:
                xs = np.linspace(p[0]-1, p[0]+1, 2)
                zs = np.linspace(p[2]-1, p[2]+1, 2)                
                xs,zs = np.meshgrid(xs,zs)
                ys = p[1] * np.ones(np.shape(xs))
                                
            ax.plot_surface(xs,ys,zs, color = self.cs[idx],
                            edgecolor='k', shade=False, linewidth=3)
                
        ax.set_xlim([-3.01,3.01])
        ax.set_ylim([-3.01,3.01])
        ax.set_zlim([-3.01,3.01])
        ax.axis('off')
        plt.axis('equal')
        return ax

    def square_plot(self):
        fig, axs = plt.subplots(2,3)        
        
        for f in range(6):
            i = f % 3
            j = int(f / 3)
            ax = axs[j][i]
            
            for s in range(9):
                i_f = s % 3
                j_f = int(s / 3)
                x = i_f
                y = j_f
                c = color_dict[self.squares[f, i_f, j_f]]
                ax.add_patch(Rectangle((x, y), width = 1, height = 1,
                                       facecolor = c, linewidth=2,
                                       edgecolor='k'))
                ax.set_title(face_dict[f] + " " + str(f))
                ax.set_xlim(0, 3)
                ax.set_ylim(0, 3)                
                ax.axis('equal')
                ax.axis('off')
                
        plt.tight_layout()
        return axs
    
if __name__ == "__main__":
    c = Cube()
    # c.cube_plot()
    # c.rotate_face_to_face('back', 'up')
    # # # c.cube_plot()
    # c.rotate_face_to_face('up', 'back')    
    # # c.rotate_y(1)
    # c.cube_plot()

    # c.square_plot()
    # plt.show()
    pass