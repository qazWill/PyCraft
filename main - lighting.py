import math, random, sys, time

# openggl
from OpenGL.GL import *
from OpenGL.GLU import *

# pygame
import pygame
from pygame.locals import *

# matrix
from gameobjects.matrix44 import *

def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60.0, float(width)/height, .1, 1000.)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
def init():
    
    # OpenGl features
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    
    # fog
    '''glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (0.8, 0.8, 0.8))
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 25)
    glFogf(GL_FOG_END, 30)'''
    
    # light
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)  
    glLight(GL_LIGHT0, GL_POSITION,  (0, 0.8, -1, 1))
    glLight(GL_LIGHT0, GL_AMBIENT,  (0.02, 0.02, 0.02, 1))
    glLight(GL_LIGHT0, GL_DIFFUSE,  (0.7, 0.7, 0.7, 1))
    
def load_texture(texture_location):
    
    # Load the textures
    texture_surface = pygame.image.load(texture_location)
    
    # Retrieve the texture data
    texture_data = pygame.image.tostring(texture_surface, 'RGB', True)
    
    texture_id = glGenTextures(1)
    
    # Tell OpenGL we will be using this texture id for texture operations
    glBindTexture(GL_TEXTURE_2D, texture_id)
    
    # Tell OpenGL how to scale images
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) 
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    
    # Tell OpenGL that data is aligned to byte boundries
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    
    # Get the dimensions of the image
    width, height = texture_surface.get_rect().size
    
    # Upload the image to OpenGL
    glTexImage2D( GL_TEXTURE_2D,
                  0,
                  3,
                  width,
                  height,
                  0,
                  GL_RGB,
                  GL_UNSIGNED_BYTE,
                  texture_data)
    
    # returns id
    return texture_id
    
class SkyBox:
    '''This class is the most basic building block
    for this game.  It has a single texture mapped
    across its six sides.'''
    
    def __init__(self, texture_ids=[1, 1, 1, 1, 1, 1]):
        '''Creates the block class.'''
        
        # remembers its texure id
        self.texture_ids = texture_ids
            
    def render(self, x, y, z):
        '''Renders the block.'''
        
        global block_vertices, block_normals, block_faces
            
        # loops through the faces
        i = 0
        for face in block_faces:
            
            # tells OpenGl to use this texture
            glBindTexture(GL_TEXTURE_2D, self.texture_ids[i])
            
            # normals for shading
            #if self.light == 15:
            #    glNormal(*block_normals[i])
            
            # begin drawing
            glBegin(GL_QUADS)
            
            glTexCoord2f(0, 0)
            glVertex(block_vertices[face[0]][0] + x, block_vertices[face[0]][1] + y, block_vertices[face[0]][2] + z)
                    
            glTexCoord2f(1, 0)
            glVertex(block_vertices[face[1]][0] + x, block_vertices[face[1]][1] + y, block_vertices[face[1]][2] + z) 
            
            glTexCoord2f(1, 1) 
            glVertex(block_vertices[face[2]][0] + x, block_vertices[face[2]][1] + y, block_vertices[face[2]][2] + z) 
            
            glTexCoord2f(0, 1)
            glVertex(block_vertices[face[3]][0] + x, block_vertices[face[3]][1] + y, block_vertices[face[3]][2] + z)   
    
            # stop drawing
            glEnd()
                    
            # increments i
            i = i + 1  
        
class Block:
    '''This class is the most basic building block
    for this game.  It has a single texture mapped
    across its six sides.'''
    
    def __init__(self, texture_ids=[1, 1, 1, 1, 1, 1], light=0):
        '''Creates the block class.'''
        
        self.air = False
        
        # remembers its texure id
        self.texture_ids = texture_ids
                       
        self.blocked = [
            False,
            False,
            False,
            False,
            False,
            False
        ]
        
        # light data
        self.light = light
            
    def render(self, x, y, z):
        '''Renders the block.'''
        
        global block_vertices, block_normals, block_faces
        
        if not self.air:
            
            # loops through the faces
            i = 0
            for face in block_faces:
                    
                if not self.blocked[i]:
                
                    # tells OpenGl to use this texture
                    glBindTexture(GL_TEXTURE_2D, self.texture_ids[i])
                    
                    # normals for shading
                    #if self.light > 10:
                    #   glNormal(*block_normals[i])
                    
                    # begin drawing
                    glBegin(GL_QUADS)
                    
                    # normals for shading
                    #glColor(self.light / 15.0, self.light / 15.0, self.light / 15.0)
                    glColor(*get_color(block_vertices[face[0]][0] + x, block_vertices[face[0]][1] + y, block_vertices[face[0]][2] + z, block_normals[i]))
                    glTexCoord2f(0, 0)
                    glVertex(block_vertices[face[0]][0] + x, block_vertices[face[0]][1] + y, block_vertices[face[0]][2] + z)
                     
                    glColor(*get_color(block_vertices[face[1]][0] + x, block_vertices[face[1]][1] + y, block_vertices[face[1]][2] + z, block_normals[i]))
                    glTexCoord2f(1, 0)
                    glVertex(block_vertices[face[1]][0] + x, block_vertices[face[1]][1] + y, block_vertices[face[1]][2] + z) 
                    
                    glColor(*get_color(block_vertices[face[2]][0] + x, block_vertices[face[2]][1] + y, block_vertices[face[2]][2] + z, block_normals[i]))
                    glTexCoord2f(1, 1) 
                    glVertex(block_vertices[face[2]][0] + x, block_vertices[face[2]][1] + y, block_vertices[face[2]][2] + z) 
                    
                    glColor(*get_color(block_vertices[face[3]][0] + x, block_vertices[face[3]][1] + y, block_vertices[face[3]][2] + z, block_normals[i]))
                    glTexCoord2f(0, 1)
                    glVertex(block_vertices[face[3]][0] + x, block_vertices[face[3]][1] + y, block_vertices[face[3]][2] + z)   
            
                    # stop drawing
                    glEnd()
                        
                # increments i
                i = i + 1           
                
            
    def update_neighbors(self, x, y, z):
        
        global world_size, block_normals
            
        i = 0
        for normal in block_normals:
            blocker = [x, y, z]
            blocker[0] += normal[0]
            blocker[1] += normal[1]
            blocker[2] += normal[2]
            if blocker[0] < 0:
                self.blocked[i] = True
            elif blocker[0] > world_size - 1:
                self.blocked[i] = True
            elif blocker[1] < 0:
                self.blocked[i] = True
            elif blocker[2] < 0:
                self.blocked[i] = True
            elif blocker[2] > world_size - 1:
                self.blocked[i] = True
            else:
                self.blocked[i] = False
                if contains(*blocker):
                    self.blocked[i] = True
            i = i + 1
            
class Chunk:
    def __init__(self, x, z):
        global textures, world_height, world_min_terrain
        self.x = x
        self.z = z
        self.blocks = []
        for x in range(0, 16):
            l = []
            for y in range(0, world_height):
                ol = []
                for z in range(0, 16):
                    if y < world_min_terrain:
                        if y == 0:
                            block = Block(textures["bedrock"])
                        elif y > 0:
                            block = Block(textures["stone"])
                        block.blocked = [True, True, True, True, True, True]
                    else:
                        block = Block(textures["default"])
                        block.air = True
                    ol.append(block)
                l.append(ol)
            self.blocks.append(l)
        self.display_list = None
    def add(self, block):
        self.blocks.append(block)
    def render(self):
        global world_height
        for x in range(0, 16):
            for y in range(0, world_height):
                for z in range(0, 16):
                    self.blocks[x][y][z].render(x + self.x, y, z + self.z)
            
def update_neighbors():
    global chunks, world_height, world_min_terrain, generate_underground
    for chunk in chunks:
        for x in range(0, 16):
            for z in range(0, 16):
                for y in range(0, world_height):
                    if not generate_underground and y < world_min_terrain:
                        continue
                    if not chunk.blocks[x][y][z].air:
                        chunk.blocks[x][y][z].update_neighbors(chunk.x + x, y, chunk.z + z)
            
def contains(x, y, z):
    global chunks, world_height
    for chunk in chunks:
        if x >= chunk.x and x < chunk.x + 16 and z >= chunk.z and z < chunk.z + 16 and y < world_height and y >= 0:
            if not chunk.blocks[int(x - chunk.x)][int(y)][int(z - chunk.z)].air:
                return True
    return False
    
def set(x, y, z, new):
    global chunks, world_height
    for chunk in chunks:
        if x >= chunk.x and x < chunk.x + 16 and z >= chunk.z and z < chunk.z + 16 and y < world_height and y >= 0:
            chunk.blocks[int(x - chunk.x)][int(y)][int(z - chunk.z)] = new
            return 
            
def get(x, y, z):
    global chunks, world_height
    for chunk in chunks:
        if x >= chunk.x and x < chunk.x + 16 and z >= chunk.z and z < chunk.z + 16 and y < world_height and y >= 0:
            return chunk.blocks[int(x - chunk.x)][int(y)][int(z - chunk.z)]
            

def destroy(translate, vector, distance=5, accuracy=8):
    
    global chunks, world_height, textures, time_passed_seconds
    
    xi, yi, zi = vector
    xi = -xi
    yi = -yi
    zi = -zi
    for i in range(0, distance * accuracy):
         translate[0] += xi / accuracy
         translate[1] += yi / accuracy
         translate[2] += zi / accuracy
         for chunk in chunks:
            if int(translate[0]) >= chunk.x and int(translate[0]) < chunk.x + 16 and int(translate[2]) >= chunk.z and int(translate[2]) < chunk.z + 16:
                for x in range(0, 16):
                    for y in range(0, world_height):
                        for z in range(0, 16):
                            if [chunk.x + x, y, chunk.z + z] == [int(translate[0]), int(translate[1]), int(translate[2])] and not chunk.blocks[x][y][z].air:
                                if chunk.blocks[x][y][z].texture_ids == textures["bedrock"]:
                                    return
                                else:
                                    chunk.blocks[x][y][z].air = True
                                    if y != world_height - 1:
                                        chunk.blocks[x][y + 1][z].blocked[5] = False
                                    if y != 0:
                                        chunk.blocks[x][y - 1][z].blocked[4] = False
                                    if x != 15:
                                        chunk.blocks[x + 1][y][z].blocked[3] = False
                                    else:
                                        for other in chunks:
                                            if chunk.x + 16 == other.x and chunk.z == other.z:
                                                other.blocks[0][y][z].blocked[3] = False
                                                other.display_list = None
                                    if x != 0:
                                        chunk.blocks[x - 1][y][z].blocked[2] = False
                                    else:
                                        for other in chunks:
                                            if chunk.x - 16 == other.x and chunk.z == other.z:
                                                other.blocks[15][y][z].blocked[2] = False
                                                other.display_list = None
                                    if z != 15:
                                        chunk.blocks[x][y][z + 1].blocked[1] = False
                                    else:
                                        for other in chunks:
                                            if chunk.x == other.x and chunk.z + 16 == other.z:
                                                other.blocks[x][y][0].blocked[1] = False
                                                other.display_list = None
                                    if z != 0:
                                        chunk.blocks[x][y][z - 1].blocked[0] = False
                                    else:
                                        for other in chunks:
                                            if chunk.x == other.x and chunk.z - 16 == other.z:
                                                other.blocks[x][y][15].blocked[0] = False
                                                other.display_list = None
                                    chunk.display_list = None
                                    generate_light()
                                    return
                                
def place(translate, vector, distance=5, accuracy=4):
    
    global chunks, world_height, textures
    
    original = list(translate)
    
    xi, yi, zi = vector
    xi = -xi
    yi = -yi
    zi = -zi
    for i in range(0, distance * accuracy):
         translate[0] += xi / accuracy
         translate[1] += yi / accuracy
         translate[2] += zi / accuracy
         for chunk in chunks:
            if int(translate[0]) >= chunk.x and int(translate[0]) < chunk.x + 16 and int(translate[2]) >= chunk.z and int(translate[2]) < chunk.z + 16:
                for x in range(0, 16):
                    for y in range(0, world_height):
                        for z in range(0, 16):
                            if [chunk.x + x, y, chunk.z + z] == [int(translate[0]), int(translate[1]), int(translate[2])] and not chunk.blocks[x][y][z].air and y != world_height - 1:
                                translate[0] -= xi / accuracy
                                translate[1] -= yi / accuracy
                                translate[2] -= zi / accuracy
                                block = chunk.blocks[x][y][z]
                                closest_normal = None
                                for normal in block_normals:
                                    position = [chunk.x + x + 0.5, y + 0.5, chunk.z + z + 0.5]
                                    for i in [0, 1, 2]:
                                        position[i] += normal[i] / 2
                                    dist = math.sqrt((position[0] - translate[0])**2 + (position[1] - translate[1])**2 + (position[2] - translate[2])**2)
                                    if closest_normal is None:
                                        closest_normal = block_normals.index(normal)
                                        closest_inormal = block_normals.index((-normal[0], -normal[1], -normal[2]))
                                        closest_dist = dist
                                    else:
                                        if dist < closest_dist:
                                            closest_normal = block_normals.index(normal)
                                            closest_inormal = block_normals.index((-normal[0], -normal[1], -normal[2]))
                                            closest_dist = dist
                                new_position = [int(x + block_normals[closest_normal][0]), int(y + block_normals[closest_normal][1]), int(z + block_normals[closest_normal][2])]
                                #if original[0] - 0.3 <= new_position[0] + chunk.x + 1 and original[0] + 0.3 >= chunk.x + new_position[0] and original[1] - 1.2 <= new_position[1] + 1 and original[1] + 0.3 >= new_position[1] and original[2] - 0.3 <= chunk.z + new_position[2] + 1 and original[1] + 0.3 >= chunk.z + new_position[2]:
                                    #return
                                if new_position[0] >= 0 and new_position[0] < 16 and new_position[1] >= 0 and new_position[1] < world_height and new_position[2] >= 0 and new_position[2] < 16:
                                    chunk.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])] = Block(textures["brick"])
                                    chunk.display_list = None
                                    #for normal in chunk.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])].normals:
                                      #  chunk.blocks[int(new_position[0] + normal[0])][int(new_position[1] + normal[1])][int(new_position[2] + normal[2])].update_neighbors(int(new_position[0] + normal[0]), int(new_position[1] + normal[1]), int(new_position[2] + normal[2]))
                                else:
                                    if new_position[0] < 0:
                                        for other in chunks:
                                            if chunk.x == other.x + 16 and chunk.z == other.z:
                                                new_position[0] = 15
                                                other.display_list = None
                                                #for normal in other.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])].normals:
                                                #    other.blocks[int(new_position[0] + normal[0])][int(new_position[1] + normal[1])][int(new_position[2] + normal[2])].update_neighbors(int(new_position[0] + normal[0]), int(new_position[1] + normal[1]), int(new_position[2] + normal[2]))
                                                break
                                    elif new_position[0] >= 16:
                                        for other in chunks:
                                            if chunk.x == other.x - 16 and chunk.z == other.z:
                                                new_position[0] = 0
                                                other.display_list = None
                                                #for normal in other.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])].normals:
                                                #    other.blocks[int(new_position[0] + normal[0])][int(new_position[1] + normal[1])][int(new_position[2] + normal[2])].update_neighbors(int(new_position[0] + normal[0]), int(new_position[1] + normal[1]), int(new_position[2] + normal[2]))
                                                break
                                    elif new_position[1] < 0:
                                        for other in chunks:
                                            if chunk.x == other.x and chunk.z == other.z + 16:
                                                new_position[1] = 15
                                                other.display_list = None
                                                #for normal in other.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])].normals:
                                                 #   other.blocks[int(new_position[0] + normal[0])][int(new_position[1] + normal[1])][int(new_position[2] + normal[2])].update_neighbors(int(new_position[0] + normal[0]), int(new_position[1] + normal[1]), int(new_position[2] + normal[2]))
                                                break
                                    elif new_position[1] >= 16:
                                        for other in chunks:
                                            if chunk.x == other.x and chunk.z == other.z - 16:
                                                new_position[1] = 0
                                                other.display_list = None
                                                #for normal in other.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])].normals:
                                                 #   other.blocks[int(new_position[0] + normal[0])][int(new_position[1] + normal[1])][int(new_position[2] + normal[2])].update_neighbors(int(new_position[0] + normal[0]), int(new_position[1] + normal[1]), int(new_position[2] + normal[2]))                            
                                                break      
                                    else:
                                        return
                                    other.blocks[int(new_position[0])][int(new_position[1])][int(new_position[2])] = Block(textures["brick"], 15)
                                    update_light(*new_position)
                                    
                                generate_light()
                                return
                                
                                    
                                '''chunk.blocks[x][y + 1][z] = Block(textures["brick"])
                                chunk.blocks[x][y + 1][z].blocked[5] = True
                                chunk.blocks[x][y][z].blocked[4] = True
                                if y != world_height - 2:
                                    if not chunk.blocks[x][y + 2][z].air:
                                        chunk.blocks[x][y + 1][z].blocked[4] = True
                                        chunk.blocks[x][y + 2][z].blocked[5] = True
                                if x != 15:
                                    if not chunk.blocks[x + 1][y + 1][z].air:
                                        chunk.blocks[x][y + 1][z].blocked[2] = True
                                        chunk.blocks[x + 1][y + 1][z].blocked[3] = True
                                else:
                                    for other in chunks:
                                        if chunk.x + 16 == other.x and chunk.z == other.z:
                                            if not chunk.blocks[0][y + 1][z].air:
                                                chunk.blocks[x][y + 1][z].blocked[2] = True
                                                other.blocks[0][y + 1][z].blocked[3] = True
                                                other.display_list = None
                                if x != 0:
                                    if not chunk.blocks[x - 1][y + 1][z].air:
                                        chunk.blocks[x][y + 1][z].blocked[3] = True
                                        chunk.blocks[x - 1][y + 1][z].blocked[2] = True
                                else:
                                    for other in chunks:
                                        if chunk.x - 16 == other.x and chunk.z == other.z:
                                            if not chunk.blocks[15][y + 1][z].air:
                                                chunk.blocks[x][y + 1][z].blocked[3] = True
                                                other.blocks[15][y + 1][z].blocked[2] = True
                                                other.display_list = None
                                if z != 15:
                                    if not chunk.blocks[x][y + 1][z + 1].air:
                                        chunk.blocks[x][y + 1][z].blocked[0] = True
                                        chunk.blocks[x][y + 1][z + 1].blocked[1] = True
                                else:
                                    for other in chunks:
                                        if chunk.x == other.x and chunk.z + 16 == other.z:
                                            if not chunk.blocks[x][y + 1][0].air:
                                                chunk.blocks[x][y + 1][z].blocked[0] = True
                                                other.blocks[x][y + 1][0].blocked[1] = True
                                                other.display_list = None
                                if z != 0:
                                    if not chunk.blocks[x][y + 1][z - 1].air:
                                        chunk.blocks[x][y + 1][z].blocked[1] = True
                                        chunk.blocks[x][y + 1][z - 1].blocked[0] = True
                                else:
                                    for other in chunks:
                                        if chunk.x == other.x and chunk.z - 16 == other.z:
                                            if not chunk.blocks[x][y + 1][15].air:
                                                chunk.blocks[x][y + 1][z].blocked[1] = True
                                                other.blocks[x][y + 1][15].blocked[0] = True
                                                other.display_list = None
                                chunk.display_list = None
                                return'''
                                
def collide(min_x, min_y, min_z, max_x, max_y, max_z):
    '''This function checks to see if this object collides with anything.'''
    
    global chuncks, world_height
        
    for chunk in chunks:
        if max_x >= chunk.x and min_x < chunk.x + 16 and max_z >= chunk.z and min_z < chunk.z + 16:
            for x in range(0, 16):
                for y in range(0, world_height):
                    for z in range(0, 16):
                        if min_x <= chunk.x + x + 1 and max_x >= chunk.x + x and min_y <= y + 1 and max_y >= y and min_z <= chunk.z + z + 1 and max_z >= chunk.z + z and not chunk.blocks[x][y][z].air:
                            return True
    return False
        
def generate_tree(x, y, z):
    global world_size, textures
    height = random.randint(3, 5)
    for i in range(y, y + height):
        new = Block(textures["tree"])
        set(x, i, z, new) 
    for i in [x - 1, x, x + 1]:
        for j in [y + height - 1, y + height]:
            for k in [z - 1, z, z + 1]:
                if i != x or k != z or j == y + height:
                    new = Block(textures["leaf"])
                    set(i, j, k, new) 
                    
def noise(x, y):
    global seeds
    return seeds[9][x][y]
    x += 10000
    y += 10000
    global seed
    return ((int(seed * (x << 7) * x**2) % 100) + (int((seed * 3.728463635) * (y << 9) * y**3) % 100)) / 200.0
    
def smooth_noise(x, y):
    global world_size
    return noise(x, y)
    corners = 0
    sides = 0
    if x > 0 and y > 0:
        corners += noise(x - 1, y - 1)
    if x < world_size and y > 0:
        corners += noise(x + 1, y - 1)
    if x > 0 and y < world_size:
        corners += noise(x - 1, y + 1)
    if x < world_size and y < world_size:
        corners += noise(x + 1, y + 1)
    if x > 0:
        sides += noise(x - 1, y)
    if x < world_size:
        sides += noise(x + 1, y)
    if y > 0:
        sides += noise(x, y - 1)
    if y < world_size:
        sides += noise(x, y + 1)
    corners /= 16
    sides /= 8
    center = noise(x, y) / 4
    return corners + sides + center
    
def interpolate(a, b, x):
    ft = x * 3.1415927
    f = (1.0 - math.cos(ft)) * 0.5
    return float(a * (1.0 - f) + b * f)
    
def interpolated_noise(x, y):
    global world_size

    integer_x    = int(x)
    fractional_x = x - integer_x
    
    integer_y    = int(y)
    fractional_y = y - integer_y
    
    v1 = smooth_noise(integer_x, integer_y)
    v2 = smooth_noise(integer_x + 1, integer_y)
    v3 = smooth_noise(integer_x, integer_y + 1)
    v4 = smooth_noise(integer_x + 1, integer_y + 1)
    
    i1 = interpolate(v1, v2, fractional_x)
    i2 = interpolate(v3, v4, fractional_x)
    
    return interpolate(i1 , i2 , fractional_y)
                    
def perlin_noise(x, y):
    global world_size
    return interpolated_noise(x / 32.0, y / 32.0)
    average = 0
    octaves = 2
    amplitude = 0.5
    frequency = 0.02
    for i in range(0, octaves):
        average += amplitude * interpolated_noise(x * frequency, y * frequency)
        frequency *= 2
        amplitude /= 2
    return average
                    
def generate_terrain():
    global world_size, textures, world_height, world_min_terrain, world_max_terrain, generate_underground
    trees = []
    for i in range(1, (world_size / 16)**2):
        trees.append([random.randint(2, world_size - 3), 0, random.randint(2, world_size - 3)])
    for x in range(0, world_size):
        for z in range(0, world_size):
            height = world_min_terrain + (int(perlin_noise(x, z) * (world_max_terrain - world_min_terrain)))
            for y in range(world_min_terrain, height + 1):
                if y == height:
                    texture = textures["grass"]
                if y < height:
                    texture = textures["dirt"]
                if y < height - 2:
                    texture = textures["stone"]
                new = Block(texture)
                set(x, y, z, new)  
            for tree in trees:
                if tree[0] == x and tree[2] == z:
                    tree[1] = height + 1
    for chunkx in range(0, world_size, 16):
        for chunkz in range(0, world_size, 16):
            amount = random.randint(5, 8)
            for i in range(0, amount):
                x = random.randint(chunkx, chunkx + 16)
                y = random.randint(1, world_min_terrain - 1)
                z = random.randint(chunkz, chunkz + 16)
                if x == 0:
                    x += 1
                if x == world_size - 1:
                    x -= 1
                if z == 0:
                    z += 1
                if z == world_size - 1:
                    z -= 1
                if y == 0:
                    y += 1
                new = Block(textures["iron"])
                new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                set(x, y, z, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]   
                    set(x - 1, y, z, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x + 1, y, z, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x, y - 1, z, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x, y + 1, z, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x, y, z - 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x, y, z + 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x - 1, y - 1, z - 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x + 1, y - 1, z - 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x - 1, y - 1, z + 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x + 1, y - 1, z + 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x - 1, y + 1, z - 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x + 1, y + 1, z - 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x - 1, y + 1, z + 1, new)
                if random.choice([True, False]):
                    new = Block(textures["iron"])
                    new.blocked = [
                    True,
                    True,
                    True,
                    True,
                    True,
                    True
                    ]  
                    set(x + 1, y + 1, z + 1, new)
                
    if generate_underground:
        threshold = 0.53
        for x in range(1, world_size - 1):
            for y in range(2, world_height):
                for z in range(1, world_size - 1):
                    if not get(x, y, z).air:
                        value = perlin_noise_3d(x, y, z)
                        if value > threshold:
                            new = Block()
                            new.air = True
                            set(x, y, z, new)
    
    for tree in trees:
        if contains(tree[0], tree[1] - 1, tree[2]):
            make = True
            others = list(trees)
            others.remove(tree)
            for other in others:
                if other[0] > tree[0] - 3 and other[0] < tree[0] + 3 and other[2] > tree[2] - 3 and other[2] < tree[2] + 3:
                    make = False
            if make:
                generate_tree(*tree)
            
def noise_3d(x, y, z):
    global seeds
    return seeds[x][y][z]
    x += 10000
    y += 10000
    z += 10000
    global seed
    return ((int(seed * (x << 7) * x**2) + int((seed * 3.728463635) * (y << 9) * y**3) + int((seed * 5.61368952) * (z << 5) * z**(3/2))) % 100) / 100.0
    
def smooth_noise_3d(x, y, z):
    global world_size, world_height
    corners = 0
    sides = 0
    if x > 0 and y > 0 and z > 0:
        corners += noise_3d(x - 1, y - 1, z - 1)
    if x > 0 and y > 0 and z < world_size:
        corners += noise_3d(x - 1, y - 1, z + 1)
    if x < world_size and y > 0 and z > 0:
        corners += noise_3d(x + 1, y - 1, z - 1)
    if x < world_size and y > 0 and z < world_size:
        corners += noise_3d(x + 1, y - 1, z + 1)
    if x > 0 and y < world_size and z > 0:
        corners += noise_3d(x - 1, y + 1, z - 1)
    if x > 0 and y < world_size and z < world_size:
        corners += noise_3d(x - 1, y + 1, z + 1)
    if x < world_size and y < world_size and z > 0:
        corners += noise_3d(x + 1, y + 1, z - 1)
    if x < world_size and y < world_size and z < world_size:
        corners += noise_3d(x + 1, y + 1, z + 1)
    if x > 0:
        sides += noise_3d(x - 1, y, z)
    if x < world_size:
        sides += noise_3d(x + 1, y, z)
    if y > 0:
        sides += noise_3d(x, y - 1, z)
    if y < world_size:
        sides += noise_3d(x, y + 1, z)
    if z > 0:
        sides += noise_3d(x, y, z - 1) 
    if z < world_size:
        sides += noise_3d(x, y, z + 1)
    corners *= (10.0 / 8.0) / 16.0
    sides *= (2.0 / 6.0) / 16.0
    center = noise_3d(x, y, z) / 4
    return corners + sides + center
    
def interpolated_noise_3d(x, y, z):

    integer_x    = int(x)
    fractional_x = x - integer_x
    
    integer_y    = int(y)
    fractional_y = y - integer_y
    
    integer_z    = int(z)
    fractional_z = z - integer_z

    v1 = smooth_noise_3d(integer_x, integer_y, integer_z)
    v2 = smooth_noise_3d(integer_x + 1, integer_y, integer_z)
    v3 = smooth_noise_3d(integer_x, integer_y + 1, integer_z)
    v4 = smooth_noise_3d(integer_x + 1, integer_y + 1, integer_z)
    i1 = interpolate(v1, v2, fractional_x)
    i2 = interpolate(v3, v4, fractional_x)
    left = interpolate(i1, i2, fractional_y)
    
    v1 = smooth_noise_3d(integer_x, integer_y, integer_z + 1)
    v2 = smooth_noise_3d(integer_x + 1, integer_y, integer_z + 1)
    v3 = smooth_noise_3d(integer_x, integer_y + 1, integer_z + 1)
    v4 = smooth_noise_3d(integer_x + 1, integer_y + 1, integer_z + 1)
    i1 = interpolate(v1, v2, fractional_x)
    i2 = interpolate(v3, v4, fractional_x)
    right = interpolate(i1, i2, fractional_y)
    
    return interpolate(left, right, fractional_z)
            
def perlin_noise_3d(x, y, z):
    return interpolated_noise_3d(x / 8.0, y / 8.0, z / 8.0)
    global world_size
    average = 0
    octaves = [16, 8]
    for i in octaves:
        average += interpolated_noise_3d(x / float(i), y / float(i), z / float(i)) / float(len(octaves))
    # print average
    return average
                    
def dot_product(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def runtime(function, args=[]):
    start = time.time()
    function(*args)
    return time.time() - start
    
def generate_chunks():
    global chunks, world_size
    for x in range(0, world_size, 16):
        for z in range(0, world_size, 16):
            chunks.append(Chunk(x, z))
            
def get_color(x, y, z, normal):
    global minimum_light, maximum_light
    l = 0
    n = 0
    for xi in [x, x - 1]:
        if normal[0] == 1 and xi == x or normal[0] == -1 and xi == x - 1 or normal[0] == 0:
            for yi in [y, y - 1]:
                if normal[1] == 1 and yi == y or normal[1] == -1 and yi == y - 1 or normal[1] == 0:
                    for zi in [z, z - 1]:
                        if normal[2] == 1 and zi == z or normal[2] == -1 and zi == z - 1 or normal[2] == 0:
                            block = get(xi, yi, zi)
                            if block != None:
                                l += block.light
                                n += 1
    if l != 0:
        l /= float(n)
    return (l / float(maximum_light), l / float(maximum_light), l / float(maximum_light))
            
def generate_light(x=0, y=0, z=0):
    global minimum_light, maximum_light
    '''chunkx = x / 16
    chunkz = z / 16
    x = x % 16
    z = z % 16
    b = chunk.blocks[x][y][z]
    for chunk in chunks:
        if chunk.x == chunkx and chunk.z == chunkz:
            b = chunk.blocks[x][y][z]
            if not b.air:
                continue'''
            

    for chunk in chunks:
        for y in range(world_height - 1, -1, -1):
            for x in range(0, 16):
                for z in range(0, 16):
                    b = chunk.blocks[x][y][z]
                    if not b.air:
                        continue
                    exposed = True
                    for i in range(y + 1, world_height):
                        if contains(x + chunk.x, i, z + chunk.z):
                            exposed = False
                            break;
                    if exposed:
                        chunk.blocks[x][y][z].light = maximum_light
                    else:
                        global world_size, block_normals
            
                        best = 0
                        for normal in block_normals:
                            blocker = [x + chunk.x, y, z + chunk.z]
                            blocker[0] += normal[0]
                            blocker[1] += normal[1]
                            blocker[2] += normal[2]
                            b = get(*blocker)
                            if b != None:
                                l = b.light
                                if l > best:
                                    best = l
                        if best == minimum_light:
                            best = minimum_light + 1
                        chunk.blocks[x][y][z].light = best - 1
    for chunk in chunks:
        for y in range(0, world_height):
            for x in range(15, 0, -1):
                for z in range(15, 0, -1):
                    b = chunk.blocks[x][y][z]
                    if not b.air:
                        continue
                    if b.light != maximum_light:
            
                        best = 0
                        for normal in block_normals:
                            blocker = [x + chunk.x, y, z + chunk.z]
                            blocker[0] += normal[0]
                            blocker[1] += normal[1]
                            blocker[2] += normal[2]
                            b = get(*blocker)
                            if b != None:
                                l = b.light
                                if l > best:
                                    best = l
                        if best == minimum_light:
                            best = minimum_light + 1
                        chunk.blocks[x][y][z].light = best - 1
    for chunk in chunks:
        for y in range(world_height - 1, -1, -1):
            for x in range(0, 16):
                for z in range(0, 16):
                    b = chunk.blocks[x][y][z]
                    if b.air:
                        if b.light < minimum_light:
                            b.light = minimum_light
    
                        
# world properties
world_size = input("World's Size? >>> ")
world_height = input("World's Height? >>> ")
world_min_terrain = input("World's Minimum Terrain Height? >>> ")
world_max_terrain = world_height - 8
generate_underground = raw_input("Generate Underground Caves? (y/n) >>> ")
print
if generate_underground != "n":
    generate_underground = True
else:
    generate_underground = False
    
# sets up everything
pygame.init()
width = 800
height = 600
screen = pygame.display.set_mode((width, height), HWSURFACE|OPENGL|DOUBLEBUF|FULLSCREEN)
#screen = pygame.display.set_mode((width, height), HWSURFACE|OPENGL|DOUBLEBUF)
pygame.display.set_caption("PyCraft")
resize(width, height)
init()

# creates a timer
clock = pygame.time.Clock()

# Camera transform matrix
camera_matrix = Matrix44()
camera_matrix.translate = (0, 0, 0)
rotation_matrix = Matrix44.xyz_rotation(0, 0, 0)        
camera_matrix *= rotation_matrix

# makes the mouse invisible
pygame.mouse.set_visible(False)
        
# Upload the inverse camera matrix to OpenGL
glLoadMatrixd(camera_matrix.get_inverse().to_opengl())

# block information
block_vertices = [ 
    [0.0, 0.0, 1.0],
    [1.0, 0.0, 1.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0],
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [1.0, 1.0, 0.0],
    [0.0, 1.0, 0.0] 
]
block_normals = [ 
    (0.0, 0.0, +1.0),  # front
    (0.0, 0.0, -1.0),  # back
    (+1.0, 0.0, 0.0),  # right
    (-1.0, 0.0, 0.0),  # left 
    (0.0, +1.0, 0.0),  # top
    (0.0, -1.0, 0.0) ] # bottom
block_faces = [ (0, 1, 2, 3),
    (4, 5, 6, 7),  # back
    (1, 5, 6, 2),  # right
    (0, 4, 7, 3),  # left
    (3, 2, 6, 7),  # top
    (0, 1, 5, 4) ] # bottom  
    
sun = [0, 0, 1]
minimum_light = 2
maximum_light = 15

# variables and lists
speed = 5
display_chunks = False
rotation = [0, 225, 0]
translate = [world_size / 2, world_height + 2, world_size / 2]
translate[0] = 2
translate[2] = 2
flying = False
y_vel = 0
grounded = False
collision = True
time_passed_seconds = 0
space = 0
focus = False
view_distance = 40
chunks = []

seeds = []
for x in range(0, world_size):
    i = []
    for y in range(0, world_height):
        j = []
        for z in range(0, world_size):
            j.append(random.uniform(0, 1))
        i.append(j)
    seeds.append(i)

# loads all textures
load_texture("textures\\default.png")
load_texture("textures\\stone.png")
load_texture("textures\\grass_side.png")
load_texture("textures\\grass_top.png")
load_texture("textures\\dirt.png")
load_texture("textures\\tree_middle.png")
load_texture("textures\\tree_side.png")
load_texture("textures\\leaves.png")
load_texture("textures\\bedrock.png")
load_texture("textures\\brick.png")
load_texture("textures\\sky box\\side.png")
load_texture("textures\\sky box\\top.png")
load_texture("textures\\sky box\\bottom.png")
load_texture("textures\\sky box\\sun.png")
load_texture("textures\\iron.png")
textures = {"default":[1, 1, 1, 1, 1, 1],
            "bedrock":[9, 9, 9, 9, 9, 9],
            "stone":[2, 2, 2, 2, 2, 2],
            "grass":[3, 3, 3, 3, 4, 5],
            "dirt":[5, 5, 5, 5, 5, 5],
            "tree":[7, 7, 7, 7, 6, 6],
            "leaf":[8, 8, 8, 8, 8, 8],
            "brick":[10, 10, 10, 10, 10, 10],
            "skybox":[14, 11, 11, 11, 12, 13],
            "iron":[15, 15, 15, 15, 15, 15]}
            
# creates a skybox
skybox = SkyBox(textures["skybox"])
        
# creates world
total = 0
print "Creating world chunks..."
run = runtime(generate_chunks)
total += run
print("Completed in %.2f seconds.\n" % run)
print "Generating world terrain..."
run = runtime(generate_terrain)
total += run
print ("Completed in %.2f seconds.\n" % run)
print "Updating block neighbor flags..."
run = runtime(update_neighbors)
total += run
print ("Completed in %.2f seconds.\n" % run)
print "Generating lighting..."
run = runtime(generate_light)
total += run
print ("Completed in %.2f seconds.\n" % run)
print ("All world generation completed in %.2f seconds." % total)
print "Starting game...\n"


# starts the main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYUP and event.key == K_ESCAPE:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y, z, n = camera_matrix.forward
                destroy(list(translate), [x, y, z])  
            if event.button == 3:
                x, y, z, n = camera_matrix.forward
                place(list(translate), [x, y, z])
        if event.type == KEYDOWN:
            if event.key == K_c:
                if display_chunks:
                    display_chunks = False
                else:
                    display_chunks = True
            if event.key == K_f:
                if focus:
                    focus = False
                else:
                    focus = True
            if event.key == K_u:
                if collision:
                    collision = False
                else:
                    collision = True
            if event.key == K_SPACE:
                if space < 0.2:
                    if flying:
                        flying = False
                        speed = 5
                    else:
                        flying = True
                        speed = 7
                space = 0
            if event.key == K_DOWN:
                if view_distance > 0:
                    view_distance -= 5
            if event.key == K_UP:
                view_distance += 5
            if event.key == K_p:
                fps = 1.0 / time_passed_seconds
                print("Running at %.2f fps." % fps)
      
    # time since last space bar press
    space += time_passed_seconds
    
    # Clear the screen, and z-buffer
    #glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)
         
    # gets rotation based on mouse movement
    if focus:
        x, y = pygame.mouse.get_pos()
        x = (screen.get_width() / 2) - x
        y = (screen.get_height() / 2) - y
        pygame.mouse.set_pos([screen.get_width() / 2, screen.get_height() / 2])
        rotation[0] += float(y) * time_passed_seconds * 4
        rotation[1] += float(x) * time_passed_seconds * 4
        
    # gets list of pressed keys
    pressed = pygame.key.get_pressed()
        
    # adjusts translate based on the keys pressed
    old_x, old_y, old_z = translate
    change = [0, 0, 0]
    if pressed[K_w]:
        x = math.sin(math.radians(rotation[1]))
        z = math.cos(math.radians(rotation[1]))
        change[0] += x * -speed * time_passed_seconds
        change[2] += z * -speed * time_passed_seconds
    elif pressed[K_s]:
        x = math.sin(math.radians(rotation[1]))
        z = math.cos(math.radians(rotation[1]))
        change[0] += x * speed * time_passed_seconds
        change[2] += z * speed * time_passed_seconds
    if pressed[K_a]:
        x = math.sin(math.radians(rotation[1] + 90))
        z = math.cos(math.radians(rotation[1] + 90))
        change[0] += x * -speed * time_passed_seconds
        change[2] += z * -speed * time_passed_seconds
    elif pressed[K_d]:
        x = math.sin(math.radians(rotation[1] + 90))
        z = math.cos(math.radians(rotation[1] + 90))
        change[0] += x * speed * time_passed_seconds
        change[2] += z * speed * time_passed_seconds
    if pressed[K_SPACE]:
        if flying:
            change[1] += 0.1 * speed * time_passed_seconds * 10
        else:
            if grounded:
                y_vel = 12
        
    if pressed[K_LSHIFT] and flying:
        change[1] -= 0.1 * speed * time_passed_seconds * 10
        
    if not flying and not grounded and time_passed_seconds < 0.1:
        if y_vel > -10:
            y_vel -= 40 * time_passed_seconds
        change[1] += time_passed_seconds * y_vel
        
    # collision detection and resolution
    grounded = False
    for i in [0, 2, 1]:
        translate[i] = translate[i] + change[i]
        if collision:
            if collide(translate[0] - 0.3, translate[1] - 1.5, translate[2] - 0.3, translate[0] + 0.3, translate[1] + 0.3, translate[2] + 0.3) or translate[0] - 0.3 < 0 or translate[0] + 0.3 > world_size or translate[2] - 0.3 < 0 or translate[2] + 0.3 > world_size:
                translate[i] = translate[i] - change[i] 
                if i == 1:
                    grounded = True
                    translate[1] = int(translate[1] - 1.5) + 1.501
                    y_vel = 0
                
    # reset camera matrix
    camera_matrix = Matrix44()
    camera_matrix.translate = translate
    rotation_matrix = Matrix44.xyz_rotation(0, 0, 0)        
    camera_matrix *= rotation_matrix
        
    # calculate rotation matrix and multiply by camera matrix
    rotation_matrix = Matrix44.xyz_rotation(0, math.radians(rotation[1]), 0)  
    camera_matrix *= rotation_matrix
    rotation_matrix = Matrix44.xyz_rotation(math.radians(rotation[0]), 0, 0)  
    camera_matrix *= rotation_matrix
        
    # upload the inverse camera matrix to OpenGL
    glLoadMatrixd(camera_matrix.get_inverse().to_opengl())
    
    '''# Light must be transformed as well
    #light[0] = light[0] - 0.01
    sun = [0, 0.8, 1]
    rotation_matrix = Matrix44.xyz_rotation(math.radians(0.1), 0, 0) 
    #sun = rotation_matrix.transform(sun)
    if sun[1] >= 0:
        glLight(GL_LIGHT0, GL_DIFFUSE,  (0.7, 0.7, 0.7, 1))
        glLight(GL_LIGHT0, GL_POSITION, (sun[0], sun[1], sun[2], 0))
    else:
        glLight(GL_LIGHT0, GL_DIFFUSE,  (0.1, 0.1, 0.1, 1))
        glLight(GL_LIGHT0, GL_POSITION, (-sun[0], -sun[1], -sun[2], 0))'''
        
    glLight(GL_LIGHT0, GL_POSITION, (0, 0.8, 1, 0))
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    skybox.render(translate[0] - 0.5, translate[1] - 0.5, translate[2] - 0.5)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    for chunk in chunks:
        if chunk.display_list is None:
            
            # Starts display list
            chunk.display_list = glGenLists(1) 
            glNewList(chunk.display_list, GL_COMPILE)
            
            # renders the chunk
            chunk.render()
            
            # Ends display list
            glEndList()
            
        else:
            distance = math.sqrt((translate[0] - (chunk.x + 8))**2 + (translate[2] - (chunk.z + 8))**2)
            if distance < view_distance:
                display = False
                x, y, z, n = camera_matrix.forward
                if translate[0] > chunk.x and translate[0] < chunk.x + 16 and translate[1] > 0 and translate[1] < world_height and translate[2] > chunk.z and translate[2] < chunk.z + 16:
                    display = True
                if not display:
                    for pointx in [chunk.x, chunk.x + 16 , chunk.x + 8]:
                        for pointy in range(0, world_height + 4, 4):
                            for pointz in [chunk.z, chunk.z + 16, chunk.z + 8]:
                                chunk_vector = [pointx - translate[0], pointy - translate[1], pointz - translate[2]]
                                distance = math.sqrt(chunk_vector[0]**2 + chunk_vector[1]**2 + chunk_vector[2]**2)
                                chunk_vector[0] /= distance
                                chunk_vector[1] /= distance
                                chunk_vector[2] /= distance
                                if dot_product(chunk_vector, [x, y, z]) < -0.67: # if any point is in view, display that chunk
                                    display = True
                if display:
                    
                    # calls the display list
                    glCallList(chunk.display_list)
                
    if display_chunks:
        glDisable(GL_TEXTURE_2D)
        for x in range(0, world_size + 16, 16):
            for z in range(0, world_size + 16, 16):
                a = [x, -8, z]
                b = [x, world_height + 8, z]
                glColor(1.0, 0.0, 0.0)
                glBegin(GL_LINES)
                glVertex3f(*a)
                glVertex3f(*b)
                glEnd()
        glColor(1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0.0, 800, 600, 0.0, -1.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glClear(GL_DEPTH_BUFFER_BIT)

    glBegin(GL_LINES)
    glColor3f(0.0, 0.0, 0.0)
    glVertex2f(390.0, 300.0)
    glVertex2f(410.0, 300.0)
    glVertex2f(400.0, 290.0)
    glVertex2f(400.0, 310.0)
    glEnd()
    glColor3f(1.0, 1.0, 1.0)
        
    # Making sure we can render 3d again
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # time delay
    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0
    
    # update the screen
    pygame.display.flip()
