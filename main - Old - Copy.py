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
    glFogf(GL_FOG_START, 15)
    glFogf(GL_FOG_END, 20)
    
    # light
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)  
    glLight(GL_LIGHT0, GL_POSITION,  (1, 1, 1, 1)) # in front and above you
    
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
        
class NewBlock:
    '''This class is the most basic building block
    for this game.  It has a single texture mapped
    across its six sides.'''
    
    def __init__(self, position, texture_ids=[1, 1, 1, 1, 1, 1]):
        '''Creates the block class.'''
        
        # remembers its texure id
        self.texture_ids = texture_ids
        
        # vertices
        self.vertices = [ [0.0, 0.0, 1.0],
                          [1.0, 0.0, 1.0],
                          [1.0, 1.0, 1.0],
                          [0.0, 1.0, 1.0],
                          [0.0, 0.0, 0.0],
                          [1.0, 0.0, 0.0],
                          [1.0, 1.0, 0.0],
                          [0.0, 1.0, 0.0] ]
            
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

        # translates the position of the block
        for vertex in self.vertices:
            vertex[0] = vertex[0] + position[0]
            vertex[1] = vertex[1] + position[1]
            vertex[2] = vertex[2] + position[2]
                          
    def render(self):
        '''Renders the block.'''
        
        # loops through the faces
        i = 0
        for face in self.faces:
            
             # tells OpenGl to use this texture
            glBindTexture(GL_TEXTURE_2D, self.texture_ids[i])
            
            # normals for shading
            glNormal3dv(self.normals[i])
            
            # increments i
            i = i + 1
            
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
        
    def collide(self, o_minX, o_minY, o_minZ, o_maxX, o_maxY, o_maxZ):
        '''This function checks to see if this object collides with anything.'''
        
        # finds the bounding box of this object
        minX, minY, minZ = self.vertices[0]
        maxX, maxY, maxZ = self.vertices[0]
        
        # checks for a collision
        for vertex in self.vertices:
            if minX > vertex[0]:
                minX = vertex[0]
            elif maxX < vertex[0]:
                maxX = vertex[0]
            if minY > vertex[1]:
                minY = vertex[1]
            elif maxY < vertex[1]:
                maxY = vertex[1]
            if minZ > vertex[2]:
                minZ = vertex[2]
            elif maxZ < vertex[2]:
                maxZ = vertex[2]
                
        # returns the results
        if o_minX >= minX and o_maxX <= maxX and o_minY >= minY and o_maxY <= maxY and o_minZ >= minZ and o_maxZ <= maxZ:
            return True
        else:
            return False
            
def Create_World(type):
    '''This creates all the blocks and returns a list containing them.'''
    
    global textures
    
    # will store all the objects
    objects = []
    
    # creates a flat world
    if type == "test":
        for x in range(0, 10):
            for z in range(0, 10):
                for y in [0, -1, -2, -3, -4, -5]:
                    height = 0
                    if x > 1 and z > 4 or x > 3 and z > 3:
                        height = 1
                    if y == 0:
                        objects.append(NewBlock([x, y + height, z], textures["grass"]))
                    elif y <= -3:
                        objects.append(NewBlock([x, y + height, z], textures["stone"]))
                    else:
                        objects.append(NewBlock([x, y + height, z], textures["dirt"]))
        for y in range(1, 6):
            objects.append(NewBlock([6, y, 8], textures["tree"]))
        for x in range(5, 8):
            for y in range(5, 7):
                for z in range(7, 10):
                    if x != 6 or z != 8:
                        objects.append(NewBlock([x, y, z], textures["leaf"]))

    if type == "woods":
        for x in range(0, 10):
            for z in range(0, 10):
                for y in [0, -1, -2, -3, -4, -5]:
                    if y == 0:
                        objects.append(NewBlock([x, y, z], textures["grass"]))
                    elif y <= -3:
                        objects.append(NewBlock([x, y, z], textures["stone"]))
                    else:
                        objects.append(NewBlock([x, y, z], textures["dirt"]))
        for i in range(0, random.randint(3, 6)):
            height = random.randint(4, 8)
            x = random.randint(0, 9)
            z = random.randint(0, 9)
            for y in range(1, height):
                objects.append(NewBlock([x, y, z], textures["tree"]))
            for tx in [x - 1, x, x + 1]:
                for ty in [height - 1, height]:
                    for tz in [z - 1, z, z + 1]:
                        if tx != x or tz != z or ty != height - 1:
                                objects.append(NewBlock([tx, ty, tz], textures["leaf"]))
        
    return objects
    
# sets up everything
pygame.init()
screen = pygame.display.set_mode((800, 600), HWSURFACE|OPENGL|DOUBLEBUF|FULLSCREEN)
#screen = pygame.display.set_mode((800, 600), HWSURFACE|OPENGL|DOUBLEBUF)
resize(800, 600)
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
translate = [0, 10, 0]
jump = 0
jumped = False
speed = 3
button = 0
light = [10, 4, 10, 1]


# loads all textures
load_texture("textures\\default.png")
load_texture("textures\\stone.png")
load_texture("textures\\grass_side.png")
load_texture("textures\\grass_top.png")
load_texture("textures\\dirt.png")
load_texture("textures\\tree_middle.png")
load_texture("textures\\tree_side.png")
load_texture("textures\\grass_top.png")
textures = {"default":[1, 1, 1, 1, 1, 1],
            "stone":[2, 2, 2, 2, 2, 2],
            "grass":[3, 3, 3, 3, 4, 5],
            "dirt":[5, 5, 5, 5, 5, 5],
            "tree":[7, 7, 7, 7, 6, 6],
            "leaf":[8, 8, 8, 8, 8, 8]}

# creates the world
objects = Create_World("woods")

# starts the main loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYUP and event.key == K_ESCAPE:
            sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            button = event.button
            
    # Clear the screen, and z-buffer
    glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
       
    # time delay
    time_passed = clock.tick()
    time_passed_seconds = time_passed / 1000.0
    
    # allows user to destroy blocks
    if button == 1:
        button = 0
        x, y, z = translate
        xi, yi, zi, n = camera_matrix.forward
        x = x + xi * 2
        y = y + yi * 2
        z = z + zi * 2
        i = 0
        while i < 7:
            i = i + 1
            x = x - xi
            y = y - yi
            z = z - zi
            for object in objects:
                if object.collide(x, y, z, x, y, z):
                    objects.remove(object)
                    
                    # deletes old display list
                    display_list = None
                    
                    # breaks from the loop
                    i = 10
                    break
    elif button == 3:
        button = 0
        x, y, z = translate
        xi, yi, zi, n = camera_matrix.forward
        i = 0
        while i < 5:
            i = i + 1
            x = x - xi
            y = y - yi
            z = z - zi
            for object in objects:
                if object.collide(x, y, z, x, y, z):
                            
                    objects.append(NewBlock([int(x), int(y + 1), int(z)], textures["stone"]))
                            
                    # deletes old display list
                    display_list = None
                            
                    # breaks from the loop
                    i = 10
                    break
                            
    elif button == 2:
        button = 0
        for block in blocks:
            if block[0] == current:
                if blocks.index(block) + 1 >= len(blocks):
                    current = blocks[0][0]
                else:
                    current = blocks[blocks.index(block) + 1][0]
                break
            
            
        
    
    # gets rotation based on mouse movement
    mouse_rel_x, mouse_rel_y = pygame.mouse.get_rel()
    rotation[1] -= float(mouse_rel_x) / 4
    rotation[0] -= float(mouse_rel_y) / 4
    
    # gets list of pressed keys
    pressed = pygame.key.get_pressed()
    
    # adjusts translate based on the keys pressed
    old_x, old_y, old_z = translate
    if pressed[K_w]:
        x = math.sin(math.radians(rotation[1]))
        z = math.cos(math.radians(rotation[1]))
        translate[0] += x * -speed * time_passed_seconds
        translate[2] += z * -speed * time_passed_seconds
    elif pressed[K_s]:
        x = math.sin(math.radians(rotation[1]))
        z = math.cos(math.radians(rotation[1]))
        translate[0] += x * speed * time_passed_seconds
        translate[2] += z * speed * time_passed_seconds
    if pressed[K_a]:
        x = math.sin(math.radians(rotation[1] + 90))
        z = math.cos(math.radians(rotation[1] + 90))
        translate[0] += x * -speed * time_passed_seconds
        translate[2] += z * -speed * time_passed_seconds
    elif pressed[K_d]:
        x = math.sin(math.radians(rotation[1] + 90))
        z = math.cos(math.radians(rotation[1] + 90))
        translate[0] += x * speed * time_passed_seconds
        translate[2] += z * speed * time_passed_seconds
        
    # jumping
    if time_passed_seconds < 0.3:
        if pressed[K_SPACE] and not jumped:
            jump = 15
            jumped = True
        if jump > 0:
            jump = jump - 10 * time_passed_seconds
            translate[1] = translate[1] + jump * time_passed_seconds
        
    # gravity
    if time_passed_seconds < 0.3:
        translate[1] -= 10 * time_passed_seconds
    
    # checks for a collision with user
    for object in objects:
        if object.collide(translate[0] + 0.3, translate[1] + 0.3, translate[2] + 0.3, translate[0] - 0.3, translate[1] - 1.5, translate[2] - 0.3) or display_list is None:
            max = object.vertices[0][1]
            for vertex in object.vertices:
                if vertex[1] > max:
                    max = vertex[1]
            if old_y - 1.5 > max:
                translate[1] = old_y
                jumped = False
                break
    for object in objects:
        if object.collide(translate[0] + 0.31, translate[1] + 0.3, translate[2] + 0.31, translate[0] - 0.31, translate[1] - 1.5, translate[2] - 0.31) or display_list is None:
            translate[0] = old_x
            translate[2] = old_z
            break
                
    # resets camera matrix
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
    glLight(GL_LIGHT0, GL_POSITION, (1, 1, 1, 0))
    
    if display_list is None:
        
        # Starts display list
        display_list = glGenLists(1) 
        glNewList(display_list, GL_COMPILE)
        
        # renders objects
        for object in objects:
            object.render()
        
        # Ends display list
        glEndList()
        
    else:
        
        # calls the display list
        glCallList(display_list)
    
    # update the screen
    pygame.display.flip()
