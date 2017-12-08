import turtle
import math
import random
import swarm


class Position :
  # A data structure to conveniently hold an x,y position
  def __init__(self, x, y):
    self.x = x
    self.y = y

  # Made use of operator overlading for the purposes of determining if an object is in bounds
  def __gt__(self, other):
      return (self.x > other.x and self.y > other.y)

  def __lt__(self, other):
      return (self.x < other.x and self.y < other.y)


class Creature:

    def __init__(self, radius, count, attract, spacing, speed):
        self.radius = radius
        self.creature = turtle.Turtle()
        self.creature.hideturtle()
        self.count = count
        self.position = Position(random.randint(-100,100), random.randint(-100,100)) # Randomly set the starting position
        self.attact = attract
        self.speed = speed
        self.spacing = spacing
        self.heading = math.pi / random.randint(1,5) # Randomly set the heading
        self.old_pos = self.position    # A variable to keep old position, so we can revert back to it if it goes out of bounds

    def Draw(self):
        if self.attract == True:
            self.creature.pencolor("green") # Attracted creatures are green
        else:
            self.creature.pencolor("red")  # Repelled (or ugly) are red
        self.creature.clear()
        self.creature.hideturtle()
        self.creature.pu()
        self.creature.goto(self.position.x, self.position.y)
        self.creature.dot(self.radius*2)
        deltaX = self.radius*math.cos(self.heading)
        deltaY = self.radius*math.sin(self.heading)
        self.creature.goto(self.position.x + deltaX, self.position.y + deltaY)
        self.creature.dot(self.radius*.75)


    def Move(self, dt):
        distance = dt*self.speed
        deltaX = distance*math.cos(self.heading)
        deltaY = distance*math.sin(self.heading)
        self.position.x += deltaX
        self.position.y += deltaY


class Light:

    def __init__(self,radius,count,speed, random_head):
        self.radius = radius
        self.count = count
        self.speed = speed
        self.random_head = random_head
        self.position = Position(random.randint(-100,100), random.randint(-100,100))
        self.heading = math.pi / random.randint(1,5)
        self.light = turtle.Turtle()
        self.light.hideturtle()
        self.old_pos = self.position

    def __str__(self):
        return "Light"

    def Draw(self):
        self.light.pencolor("yellow")
        self.light.clear()
        self.light.hideturtle()
        self.light.pu()
        self.light.goto(self.position.x,self.position.y)
        self.light.dot(self.radius*2)
        deltaX = self.radius*math.cos(self.heading)
        deltaY = self.radius*math.sin(self.heading)
        self.light.goto(self.position.x + deltaX, self.position.y + deltaY)
        self.light.dot(self.radius*.75)

    def Move(self, dt):
        distance = dt*self.speed
        if self.random_head == True:
            if random.uniform(0.0 , 1.0) <= 0.30:  # 40% chance of changing heading, if satisfied set a random heading
                self.heading = random.randint(1,8)
                deltaX = distance*math.cos(self.heading)
                deltaY = distance*math.sin(self.heading)
            else:
                deltaX = distance*math.cos(self.heading)  # If not then keep the old heading
                deltaY = distance*math.sin(self.heading)
        elif self.random_head == False:
            deltaX = distance*math.cos(self.heading)
            deltaY = distance*math.sin(self.heading)
        self.position.x += deltaX
        self.position.y += deltaY

# -------- Using class inheritance to create a creature that is attracted to the light --------- #
class Attractive(Creature):
    '''
    Creature Sub class that is attracted to the Light
    '''

    def __init__(self, radius, count, attract, spacing, speed):
        Creature.__init__(self,radius, count, attract, spacing, speed)
        self.attract = True

    def __str__(self):
        return "Attracted"

    def maintain_space(self, light_list):

        # ----A data structure to maintain the distances between a creature and the lights in the arena --- #
        distance_dict = {}
        closest_light = None
        for light in light_list:
            distance = math.sqrt((light.position.y -  self.position.y)**2 + (light.position.x - self.position.x)**2)

            # -- Using a dictionary to keep track of which distance belongs to which object -- #
            distance_dict[light] = distance
            closest_light = min(distance_dict, key = distance_dict.get) # Get the light that corresponds to the closest distance
        # -- If distance between light and creature object less than spcing then change heading -- #
        if min(distance_dict.values()) < self.spacing:
            self.heading = closest_light.heading*max(1, 1/(min(distance_dict.values())/100)) # Set heading of the creature to the closest light heading

        return self.heading



class Ugly(Creature):
    '''
    Creature sub class that is NOT attracted to the Light
    '''

    def __init__(self,radius, count, attract, spacing, speed):
        Creature.__init__(self,radius, count, attract, spacing, speed)
        self.attract = False


    def __str__(self):
        return "Not Attracted"


    def maintain_space(self, light_list):
        # ----A data structure to maintain the distances between a creature and the lights in the arena --- #
        distance_dict = {}
        furthest_light = None
        for light in light_list:
            distance = math.sqrt((light.position.y -  self.position.y)**2 + (light.position.x - self.position.x)**2)

            # -- Using a dictionary to keep track of which distance belongs to which object -- #
            distance_dict[light] = distance
            furthest_light = max(distance_dict, key = distance_dict.get)

        # -- If distance between light and creature object less than spcing then change heading -- #
        if max(distance_dict.values()) < self.spacing:
            self.heading = -1*furthest_light.heading*max(1, 1/(max(distance_dict.values())/100))

        return self.heading
