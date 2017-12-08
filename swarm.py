import entities
import random
import turtle
import math


# ----------------------- Arena Configuration ---------------------- #
class CreatureConfiguration:
  def __init__(self, count, attract=True, space=10, speed=3):
    self.count = count
    self.attract = attract
    self.speed = speed
    self.space = space

class LightConfiguration:
  def __init__(self, count, speed=5, random=True):
    self.count = count
    self.speed = speed
    self.random = random


example = [0,0]
example[0] = ( CreatureConfiguration( 10, True, 20 ),
             CreatureConfiguration( 10, False, 10 ),
             LightConfiguration( 2 ) )

example[1] = ( CreatureConfiguration( 5, True, 10, 5 ),
             CreatureConfiguration( 10, False, 10, 5),
             LightConfiguration( 5, 5 ))



# -------------------------------- Global / Environment Variables -------------------------- #

# Dimeonsion of the window
WINDOW_XDIM = 900
WINDOW_YDIM = 600


# Dimeonsions of the area in which the creatures moves
SCREEN_XDIM = WINDOW_XDIM - 100
SCREEN_YDIM = WINDOW_YDIM - 100

RADIUS = 6
MAX_XPOS = SCREEN_XDIM / 2 - RADIUS
MAX_YPOS = SCREEN_YDIM / 2 - RADIUS


# ------------------------- Helper functions and useful data structures --------------- #
def Velocity(angle, length):
  '''
  Helper function to assist in creatures bouncing off the arena wall
  '''

  x = length*math.cos(angle)
  y = length*math.sin(angle)

  return Vector(x,y)


class Vector:

  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.angle = math.atan2(y,x)


def drawRectangle(inTurtle, width, height):
    '''
    Helper function to assist in drawing the arena
    '''
    inTurtle.begin_fill()
    inTurtle.begin_poly()
    for el in [width, height, width, height]:
        inTurtle.fd(el)
        inTurtle.lt(90)
    inTurtle.end_poly()
    inTurtle.end_fill()



def DetermineNewHeading( creature, stationary_pos ):
  creature_vel = Velocity(creature[1],creature[2])

  # Determine the point of collision, which also defines the angle
  collision = Vector(stationary_pos.x-creature[0].x, \
                      stationary_pos.y-creature[0].y )

  # Define the tangent to the point of collision
  collision_tangent = Vector( stationary_pos.y-creature[0].y, \
                              -(stationary_pos.x-creature[0].x))

  # Normalize the tangent making it length 1
  tangent_length = (collision_tangent.x**2 + collision_tangent.y**2)**0.5
  normal_tangent = Vector( collision_tangent.x/max(tangent_length,1), \
                           collision_tangent.y/max(tangent_length,1))

  rel_velocity = creature_vel

  length = rel_velocity.x*normal_tangent.x + rel_velocity.y*normal_tangent.y
  tangent_velocity = Vector( normal_tangent.x*length, normal_tangent.y*length)


  perpendicular = Vector(rel_velocity.x-tangent_velocity.x, \
                         rel_velocity.y-tangent_velocity.y )

  new_heading = Vector( (creature_vel.x-2*perpendicular.x), \
                        (creature_vel.y-2*perpendicular.y))

  return new_heading.angle


# --------------------------- Arena Class ------------------------------------- #
class Arena:

    # Initialize with the number of creatures you want to be attracted and not attracted (test_config file)
    def __init__(self, test_config):
        self.attract_crea = test_config[0]
        self.repel_crea = test_config[1]
        self.lights = test_config[2]
        self.light_list = [] # Maintaining a separate data structure for the lights
        self.creature_dict = {} # Storing our creatures in a dictionary and using keys "attract" and "not_attract"
        self.creature_dict['attract'] = [] # Within our dictionary, the values are lists
        self.creature_dict['not_attract'] = []

        for creature in range(0, self.attract_crea.count): # Attracted creatures are green
            self.creature_dict['attract'].append(entities.Attractive(RADIUS,self.attract_crea.count, self.attract_crea.attract, 300,self.attract_crea.speed))
        for creature in range(0, self.repel_crea.count): # Repelled creatures are red
            self.creature_dict['not_attract'].append(entities.Ugly(RADIUS, self.repel_crea.count, self.repel_crea.attract, 500, self.repel_crea.speed))
        for light in range(0, self.lights.count): # Lights are yellow
            self.light_list.append(entities.Light(RADIUS, self.lights.count, self.lights.speed, self.lights.random))

        self.creature_dict['all_creatures'] = self.creature_dict['attract'] + self.creature_dict['not_attract']
        self.creature_dict['all_objects'] = self.creature_dict['all_creatures'] + self.light_list # Did this, in order to not repeat code
                                                                                                # since I am going to make sure that ALL objects don't collide with walls
                                                                                                # collide with each other.

    def DrawArena(self):
        drawingWindow = turtle.Turtle()
        drawingWindow.speed(0)
        drawingWindow.hideturtle()
        drawingWindow.pu()
        drawingWindow.goto(-SCREEN_XDIM//2,-SCREEN_YDIM//2)
        drawingWindow.color('black', 'light blue')
        drawingWindow.pd()
        drawRectangle(drawingWindow, SCREEN_XDIM, SCREEN_YDIM)


    def InitializeGraphics(self):
        self.DrawArena()
        for obj in self.creature_dict['all_objects']:
            obj.Draw()



    def WallHit(self, creature, max_x, max_y,spacing = 0):
        # Main use of this function is to check if a light is ABOUT to hit the wall, so the creature can turn around #
        '''
        Takes in creature, max x and y coordinates and spacing
        Returns creature heading
        '''

        if creature.position.x + spacing > max_x:
            creature.heading = DetermineNewHeading( \
                                [creature.position,creature.heading, creature.speed],
                                entities.Position(max_x, creature.position.y))
            creature.position = entities.Position(MAX_XPOS,creature.position.y)
            return creature.heading

        # Left Wall
        elif creature.position.x - spacing < -max_x:
            creature.heading = DetermineNewHeading( \
                                [creature.position,creature.heading, creature.speed],
                                entities.Position(-max_x, creature.position.y))
            creature.position = entities.Position(-MAX_XPOS,creature.position.y)
            return creature.heading

        # Top Wall
        elif creature.position.y + spacing > max_y:
            creature.heading = DetermineNewHeading( \
                                [creature.position,creature.heading, creature.speed],
                                entities.Position(creature.position.x, max_y))
            creature.position = entities.Position(creature.position.x, MAX_YPOS)
            return creature.heading

        # Bottom Wall
        elif creature.position.y - spacing < -max_y:
            creature.heading = DetermineNewHeading( \
                                [creature.position,creature.heading, creature.speed],
                                entities.Position(creature.position.x, -max_y))
            creature.position = entities.Position(creature.position.x, -MAX_YPOS)
            return creature.heading

        else:
            return creature.heading


    def Update(self):
        '''
        Draws Creatures at their new locations
        '''
        #--- Collision with wall detection (All objects should bounce of walls) -- #
        for c1 in self.creature_dict['all_objects']:
            c1.old_pos = c1.position
            c1.Move(5)
            self.WallHit(c1, MAX_XPOS, MAX_YPOS)
            c1.Draw()
            turtle.update()

            for c2 in self.creature_dict['all_objects']:
                if c1 == c2: continue
                if (entities.Position(-MAX_XPOS, -MAX_YPOS) < c1.position < entities.Position(MAX_XPOS, MAX_YPOS)) \
                and (entities.Position(-MAX_XPOS, -MAX_YPOS) < c2.position < entities.Position(MAX_XPOS, MAX_YPOS)):

                # --- If creature is attracted to the light ---- #
                    if c1.__str__() == 'Attracted' and c2.__str__() == 'Light':
                        c1.heading = c1.maintain_space(self.light_list)

                # --- If creature not attracted and we come across a light ---- #
                    if c1.__str__() == 'Not Attracted' and c2.__str__() == 'Light':
                        c1.heading = c1.maintain_space(self.light_list)

        # ----- Collision Detection with other creatures (All creatures and lights bounce off each other. ---- #
        #----- It doesn't "look" like they are colliding but when I tested with one kind of creature they were bouncing off each other -- #
                dist = math.sqrt((c2.position.y - c1.position.y)**2 + (c2.position.x - c1.position.x)**2)
                if dist < c1.radius + c2.radius:
                    c1.heading = DetermineNewHeading([c1.position, c1.heading, c1.speed], c2.position)



# --------------------------------------------- Main Function ------------------------------------------------------------- #
def main():
    test_case = 0
    turtle.tracer(0,0)
    arena = Arena(example[test_case])
    arena.InitializeGraphics()


    try:
        while True:
            arena.Update()
            turtle.update()
    except KeyboardInterrupt:
        print('Done swarming.')



if __name__=='__main__' :
  main()
