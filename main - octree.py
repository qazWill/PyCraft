# math functions
import math
import random
import sys

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
    glEnable(GL_COLOR_MATERIAL)
    glShadeModel(GL_SMOOTH)
    glClearColor(0.8, 0.8, 0.8, 0)
    
    # fog
    glEnable(GL_FOG)
    glFogfv(GL_FOG_COLOR, (0.8, 0.8, 0.8))
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogf(GL_FOG_START, 30)
    glFogf(GL_FOG_END, 40)
    
    # light
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)  
    glLight(GL_LIGHT0, GL_POSITION,  (0.5, 1, 1, 1)) # in front and above you
    
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
    
def dot_product(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
        
class Block:
    '''This class is the most basic building block
    for this game.  It has a single texture mapped
    across its six sides.'''
    
    def __init__(self, position, texture_ids=[1, 1, 1, 1, 1, 1], size=1, air=False):
        '''Creates the block class.'''
        
        self.size = size
        self.air = air
        self.translate = position
        self.sub_blocks = []
        
        # remembers its texure id
        self.texture_ids = texture_ids
        
        # vertices
        self.vertices = [ [0.0, 0.0, size],
                          [size, 0.0, size],
                          [size, size, size],
                          [0.0, size, size],
                          [0.0, 0.0, 0.0],
                          [size, 0.0, 0.0],
                          [size, size, 0.0],
                          [0.0, size, 0.0] ]
            
        # normals
        self.normals = [ (0.0, 0.0, +1.0),  # front
                (0.0, 0.0, -1.0),  # back
                (+1.0, 0.0, 0.0),  # right
                (-1.0, 0.0, 0.0),  # left 
                (0.0, +1.0, 0.0),  # top
                (0.0, -1.0, 0.0) ] # bottom
           
        # faces
        self.faces = [ (0, 1, 2, 3),  # front
                       (4, 5, 6, 7),  # back
                       (1, 5, 6, 2),  # right
                       (0, 4, 7, 3),  # left
                       (3, 2, 6, 7),  # top
                       (0, 1, 5, 4) ] # bottom  
                       
        self.blocked = [
            False,
            False,
            False,
            False,
            False,
            False
        ]

        # translates the position of the block
        for vertex in self.vertices:
            vertex[0] = vertex[0] + position[0]
            vertex[1] = vertex[1] + position[1]
            vertex[2] = vertex[2] + position[2]
            
    def divide(self, first=False):
        new_size = self.size / 2
        if new_size != 0: # if it can be sub_divided
            if first:
                for x in [self.translate[0], self.translate[0] + self.size / 2]:
                    for z in [self.translate[2], self.translate[2] + self.size / 2]:
                        new_block = Block([x, self.translate[0], z], [1, 1, 1, 1, 1, 1], new_size)
                        new_block.divide()
                        self.sub_blocks.append(new_block)
            else:
                for x in [self.translate[0], self.translate[0] + self.size / 2]:
                    for y in [self.translate[1], self.translate[1] + self.size / 2]:
                        for z in [self.translate[2], self.translate[2] + self.size / 2]:
                            new_block = Block([x, y, z], [1, 1, 1, 1, 1, 1], new_size)
                            new_block.divide()
                            self.sub_blocks.append(new_block)
        else:
            global textures, world_size
            if self.translate[1] == 0:
                self.texture_ids = textures["bedrock"]
            elif self.translate[1] == 1:
                self.texture_ids = textures["stone"]
            else:
                self.air = True
                        
    def search(self, x, y, z):
        if self.size == 1:
            if self.translate == [x, y, z] and not self.air:
                return True
            else:
                return False
        else:
            for block in self.sub_blocks:
                if x >= block.translate[0] and x < block.translate[0] + block.size and y >= block.translate[1] and y < block.translate[1] + block.size and z >= block.translate[2] and z < block.translate[2] + block.size and not block.air:
                    if block.search(x, y, z):
                        return True
                        
    def set(self, x, y, z, new):
        if self.size == 1:
            if self.translate == [x, y, z]:
                self.texture_ids = new.texture_ids
                self.air = new.air
                return True
            else:
                return False
        else:
            for block in self.sub_blocks:
                if x >= self.translate[0] and x < self.translate[0] + self.size and y >= self.translate[1] and y < self.translate[1] + self.size and z >= self.translate[2] and z < self.translate[2] + self.size:
                    if block.set(x, y, z, new):
                        return True
            return False
            
    def get(self, x, y, z):
        if self.size == 1:
            if self.translate == [x, y, z]:
                ret_block = self
                return ret_block
            else:
                return False
        else:
            for block in self.sub_blocks:
                if x >= self.translate[0] and x < self.translate[0] + self.size and y >= self.translate[1] and y < self.translate[1] + self.size and z >= self.translate[2] and z < self.translate[2] + self.size:
                    ret_block = block.get(x, y, z)
                    if ret_block != False:
                        return ret_block
            return False
                          
    def render(self):
        '''Renders the block.'''
        
        if self.size == 1:
            if not self.air:
                global world
            
                # loops through the faces
                i = 0
                for face in self.faces:
                    
                    if not self.blocked[i]:
                    
                        # tells OpenGl to use this texture
                        glBindTexture(GL_TEXTURE_2D, self.texture_ids[i])
                        
                        # normals for shading
                        glNormal3dv(self.normals[i])
                        
                        # begin drawing
                        glBegin(GL_QUADS)
                        
                        # draws each quad
                        glTexCoord2f(0, 0)
                        glVertex(self.vertices[face[0]]) 
                        glTexCoord2f(1, 0)
                        glVertex(self.vertices[face[1]]) 
                        glTexCoord2f(1, 1) 
                        glVertex(self.vertices[face[2]]) 
                        glTexCoord2f(0, 1)
                        glVertex(self.vertices[face[3]])   
                
                        # stop drawing
                        glEnd()
                        
                    # increments i
                    i = i + 1
        
        else:
            for block in self.sub_blocks:
                block.render() 
        
    def collide(self, min_x, min_y, min_z, max_x, max_y, max_z):
        '''This function checks to see if this object collides with anything.'''
        
        if min_x <= self.translate[0] + self.size and max_x >= self.translate[0] and min_y <= self.translate[1] + self.size and max_y >= self.translate[1] and min_z <= self.translate[2] + self.size and max_z >= self.translate[2] and not self.air:
            if self.size == 1:
                if not self.air:
                    return True
                else: 
                    return False
            else:
                for block in self.sub_blocks:
                    if block.collide(min_x, min_y, min_z, max_x, max_y, max_z):
                        return True
                return False
        else:
            return False
            
    def destroy(self, a, b):
        '''This function checks to see if this object collides with anything.'''
        if self.size == 1:
            if self.translate[1] != 0 and not self.air:
                return self.translate
            return False
        else:
            candidate = False
            for block in self.sub_blocks:
                if not block.air:
                    if a[0] > b[0]:
                        minx = b[0]
                        maxx = a[0]
                    else:
                        minx = a[0]
                        maxx = b[0]
                    if a[1] > b[1]:
                        miny = b[1]
                        maxy = a[1]
                    else:
                        miny = a[1]
                        maxy = b[1]
                    if a[2] > b[2]:
                        minz = b[2]
                        maxz = a[2]
                    else:
                        minz = a[2]
                        maxz = b[2]
                    if block.collide(minx, miny, minz, maxx, maxy, maxz):
                        another = block.destroy(a, b)
                        if another != False:
                            if candidate == False:
                                candidate = another
                            else:
                                dc = math.sqrt((a[0] - candidate[0])**2 + (a[2] - candidate[2])**2)
                                dc = math.sqrt(dc + (a[1] - candidate[1])**2)
                                da = math.sqrt((a[0] - another[0])**2 + (a[2] - another[2])**2)
                                da = math.sqrt(da + (a[1] - another[1])**2)
                                if da < dc:
                                    candidate = another
            return candidate
            
    def update_neighbors(self):
        global world, world_size
        
        if self.size == 1:
            if not self.air:
                i = 0
                for normal in self.normals:
                    blocker = list(self.translate)
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
                        if world.search(*blocker):
                            self.blocked[i] = True
                        else:
                            self.blocked[i] = False
                    i = i + 1
        else:
            for block in self.sub_blocks:
                if not block.air:
                    block.update_neighbors()
                    
    def update_air(self):
        if self.size == 1:
            return self.air
        else:
            air = True
            for block in self.sub_blocks:
                if not block.update_air():
                    air = False
            if air:
                self.air = True
            return air
                
def generate_hills():
    global world, world_size
    
    # properties for the generation
    min_hills = world_size / 8
    max_hills = world_size / 4
    min_height = 4
    max_height = (world_size / 2) - 6
    min_gradient = 0.1
    max_gradient = 0.8
    
    trees = []
    for i in range(1, world_size / 2):
        trees.append([random.randint(1, world_size - 2), 2, random.randint(1, world_size - 2)])
    
    # generation
    num_hills = random.randint(min_hills, max_hills)
    hills = []
    for i in range(0, num_hills):
        hills.append([random.randint(0, world_size), random.randint(0, world_size), random.randint(min_height, max_height)])
    ordered = []
    '''while hills != []:
        lowest = hills[0][2]
        lowesti = 0
        for i in range(0, num_hills):
            if hills[i] < lowest:
                lowest = hills[i]
                lowesti = i
        ordered.append(hills[i])
        hills.remove(hills[i])
        num_hills = num_hills - 1'''
    for hill in hills:
        gradient = random.uniform(min_gradient, max_gradient)
        for x in range(0, world_size):
            for z in range(0, world_size):
                dist = math.sqrt((hill[0] - x)**2 + (hill[1] - z)**2)
                height = hill[2] - int(gradient * dist)
                if not world.search(x, height, z):
                    for y in range(1, height):
                        if y == height - 1:
                            texture = textures["grass"]
                        if y < height - 1:
                            texture = textures["dirt"]
                        if y < height - 3:
                            texture = textures["stone"]
                        new = Block([0, 0, 0], texture)
                        world.set(x, y, z, new)
                    for tree in trees:
                        if tree[0] == x and tree[2] == z:
                            if height > tree[1]:
                                tree[1] = height
    for tree in trees:
        generate_tree(*tree)
                    
def generate_tree(x, y, z):
    global world, world_size, textures
    height = random.randint(3, 5)
    for i in range(y, y + height):
        new = Block([0, 0, 0], textures["tree"])
        world.set(x, i, z, new) 
    for i in [x - 1, x, x + 1]:
        for j in [y + height - 1, y + height]:
            for k in [z - 1, z, z + 1]:
                if i != x or k != z or j == y + height:
                    new = Block([0, 0, 0], textures["leaf"])
                    world.set(i, j, k, new) 
                    
    
# sets up everything
pygame.init()
#screen = pygame.display.set_mode((800, 600), HWSURFACE|OPENGL|DOUBLEBUF|FULLSCREEN)
screen = pygame.display.set_mode((1200, 680), HWSURFACE|OPENGL|DOUBLEBUF)
resize(1200, 680)
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

# variables and lists
display_list = None
rotation = [0, 225, 0]
translate = [1, 1, 1]
speed = 5
button = 0
light = [10, 4, 10, 1]
jump = 0
gravity = 1
collision = True


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
textures = {"default":[1, 1, 1, 1, 1, 1],
            "bedrock":[9, 9, 9, 9, 9, 9],
            "stone":[2, 2, 2, 2, 2, 2],
            "grass":[3, 3, 3, 3, 4, 5],
            "dirt":[5, 5, 5, 5, 5, 5],
            "tree":[7, 7, 7, 7, 6, 6],
            "leaf":[8, 8, 8, 8, 8, 8]}
            
world_size = 32
translate[1] = world_size / 2
world = Block([0, 0, 0], [1, 1, 1, 1, 1, 1], world_size)
print "Creating world octree..."
world.divide(True)
print "Generating world terrain..."
generate_hills()
print "Determing which parts of the octree are empty..."
world.update_air()
print "Updating block neighbor flags..."
world.update_neighbors()
print "Compiling display list..."

# starts the main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYUP and event.key == K_ESCAPE:
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                x, y, z, n = camera_matrix.forward
                destroyed = world.destroy(translate, [translate[0] + x * -3, translate[1] + y * -3, translate[2] + z * -3])
                if destroyed != False:
                    new = Block(destroyed, textures["default"], 1, True)
                    world.set(destroyed[0], destroyed[1], destroyed[2], new)
                    for normal in world.normals:
                        neighbor = list(destroyed)
                        neighbor[0] += normal[0]
                        neighbor[1] += normal[1]
                        neighbor[2] += normal[2]
                        new = world.get(*neighbor)
                        if new != False:
                            new.update_neighbors()
                    display_list = None
                    world.update_air()
        if event.type == KEYDOWN:
            if event.key == K_g:
                if collision:
                    collision = False
                else:
                    collision = True
                        
    # time delay
    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0   
        
    # Clear the screen, and z-buffer
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
         
    # gets rotation based on mouse movement
    mouse_rel_x, mouse_rel_y = pygame.mouse.get_rel()
    rotation[1] -= float(mouse_rel_x) / 4
    rotation[0] -= float(mouse_rel_y) / 4
        
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
        change[1] += 0.1 * speed * time_passed_seconds * 10
    if pressed[K_LSHIFT]:
        change[1] -= 0.1 * speed * time_passed_seconds * 10
        
    # collision detection and resolution
    for i in [0, 2, 1]:
        translate[i] = translate[i] + change[i]
        if collision:
            if world.collide(translate[0] - 0.3, translate[1] - 1.2, translate[2] - 0.3, translate[0] + 0.3, translate[1] + 0.3, translate[2] + 0.3) or translate[0] - 0.3 < 0 or translate[0] + 0.3 > world_size or translate[2] - 0.3 < 0 or translate[2] + 0.3 > world_size:
                translate[i] = translate[i] - change[i]        
                
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
    
    # Light must be transformed as well
    #light[0] = light[0] - 0.01
    glLight(GL_LIGHT0, GL_POSITION, (0.5, 1, 1, 0))
    
    #world.render()
    
    if display_list is None:
        
        # Starts display list
        display_list = glGenLists(1) 
        glNewList(display_list, GL_COMPILE)
        
        # renders the world
        world.render()
        
        # Ends display list
        glEndList()
        
    else:
        
        # calls the display list
        glCallList(display_list)
    
    # update the screen
    pygame.display.flip()
