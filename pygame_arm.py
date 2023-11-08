import pygame
import numpy as np

RED = (255, 0, 0)

FPS = 60   # frames per second

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800


def getRegularPolygon(nV, radius=1.):
    angle_step = 360. / nV 
    half_angle = angle_step / 2.

    vertices = []
    for k in range(nV):
        degree = angle_step * k 
        radian = np.deg2rad(degree + half_angle)
        x = radius * np.cos(radian)
        y = radius * np.sin(radian)
        vertices.append( [x, y] )
    #
    print("list:", vertices)

    vertices = np.array(vertices)
    print('np.arr:', vertices)
    return vertices

class myPolygon():
    def __init__(self, nvertices = 3, radius=70, color=(100,0,0), vel=[5.,0]):
        self.radius = radius
        self.nvertices = nvertices
        self.vertices = getRegularPolygon(self.nvertices, radius=self.radius)

        self.color = color
        self.color_org = color 

        self.angle = 0.
        self.angvel = np.random.normal(5., 7)

        self.position = np.array([0.,0]) #
        # self.position = self.vertices.sum(axis=0) # 2d array
        self.vel = np.array(vel)
        self.tick = 0

    def update(self,):
        self.tick += 1
        self.angle += self.angvel
        self.position += self.vel

        if self.position[0] >= WINDOW_WIDTH:
            self.vel[0] = -1. * self.vel[0]

        if self.position[0] < 0:
            self.vel[0] *= -1.

        if self.position[1] >= WINDOW_HEIGHT:
            self.vel[1] *= -1.

        if self.position[1] < 0:
            self.vel[1] *= -1

        # print(self.tick, self.position)

        return

    def draw(self, screen):
        R = Rmat(self.angle)
        points = self.vertices @ R.T + self.position

        pygame.draw.polygon(screen, self.color, points)
#

def update_list(alist):
    for a in alist:
        a.update()
#
def draw_list(alist, screen):
    for a in alist:
        a.draw(screen)
#

def Rmat(degree):
    rad = np.deg2rad(degree) 
    c = np.cos(rad)
    s = np.sin(rad)
    R = np.array([ [c, -s, 0],
                   [s,  c, 0], 
                   [0,0,1]])
    return R

def Tmat(tx, ty):
    Translation = np.array( [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])
    return Translation

def draw(P,H,screen,color=(255,255,255)):
    R= H[:2,:2]
    T= H[:2,2]
    Ptransformed = P @ R.T +T
    pygame.draw.polygon(screen, color=color, points=Ptransformed)


def drawWings(position, screen, w,h):
        rot=0
        rot+=1

        P = np.array([ [0,0], [w, 0], [w-50, h], [0, h] ])
        
        H0=Tmat(position[0],position[1])
        x=H0[0,2]
        y=H0[1,2]
        pygame.draw.circle(screen,(255,0,0),(x,y),radius=2)

        dist=25
        n=6

        for i in range(n):
            H = H0@Rmat(rot+i*(360/n))@Tmat(dist,0)@Tmat(0,h/2)
            draw(P,H,screen,(20*(3+i),20*(3+i),20*(6+i)))




def main():
    pygame.init() # initialize the engine

    screen = pygame.display.set_mode( (WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    joint1_angle=0
    joint2_angle=0
    w=150
    h=40
    P = np.array([ [0,0], [w, 0], [w, h], [0, h] ])
    Grip = np.array([[0,0],[50,0],[50,10],[0,10]])
    position=[WINDOW_WIDTH/2-w/2,50]
    
    joint1_angle=0
    joint2_angle=0
    joint3_angle=0

    gripper_gripped = False

    



    done = False
    while not done:
        #  input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    joint1_angle -= 3
                if event.key == pygame.K_LEFT:
                    joint1_angle += 3


                if event.key == pygame.K_UP:
                    joint2_angle -= 3
                if event.key == pygame.K_DOWN:
                    joint2_angle += 3


                if event.key == pygame.K_a:
                    joint3_angle -= 3
                if event.key == pygame.K_d:
                    joint3_angle += 3

                if event.key == pygame.K_SPACE:
                    gripper_gripped = not gripper_gripped
        


        # drawing
        screen.fill((0, 0, 0))

        H0=Tmat(position[0],position[1])@Tmat(0,-h)
        draw(P,H0,screen,(255,255,255))


        #arm1
        H1=H0 @Tmat(w/2,h)@Rmat(90)
        joint1=[H1[0,2],H1[1,2]]

        H11=H1@Tmat(0,-h/2)@Tmat(0,h/2)@Rmat(joint1_angle)@Tmat(0,-h/2)
        draw(P,H11,screen,(255,255,255))



        #arm2
        H2=H11@Tmat(w,0)@Tmat(0,h/2)
        joint2=[H2[0,2],H2[1,2]]

        H21=H2@Tmat(0,-h/2)@Tmat(0,h/2)@Rmat(joint2_angle)@Tmat(0,-h/2)
        draw(P,H21,screen,(255,255,255))



        #arm3
        H3=H21@Tmat(w,0)@Tmat(0,h/2)
        joint3=[H3[0,2],H3[1,2]]

        H31=H3@Tmat(0,-h/2)@Tmat(0,h/2)@Rmat(joint3_angle)@Tmat(0,-h/2)
        draw(P,H31,screen,(255,255,255))


        #gripper
        HG=H31@Tmat(w,0)@Tmat(0,h/2)
        jointGrip=[HG[0,2],HG[1,2]]

        if gripper_gripped:
            Grip_angle_L=-90
            Grip_angle_R=90
        else:
            Grip_angle_L=-45
            Grip_angle_R=45


        HGL1=HG@Tmat(0,-5)@Tmat(0,5)@Rmat(45)@Tmat(0,-5)
        draw(Grip,HGL1,screen,(255,255,0))
        HGR1=HG@Tmat(0,-5)@Tmat(0,5)@Rmat(-45)@Tmat(0,-5)
        draw(Grip,HGR1,screen,(255,255,0))

        HGL2=HGL1@Tmat(50,0)@Tmat(0,5)@Rmat(Grip_angle_L)@Tmat(0,-5)
        draw(Grip,HGL2,screen,(255,0,255))
        HGR2=HGR1@Tmat(50,0)@Tmat(0,5)@Rmat(Grip_angle_R)@Tmat(0,-5)
        draw(Grip,HGR2,screen,(255,0,255))


        #joints
        pygame.draw.circle(screen, (255,0,0),joint1,10)
        pygame.draw.circle(screen, (255,0,0),joint2,10)
        pygame.draw.circle(screen, (255,0,0),joint3,10)
        pygame.draw.circle(screen, (255,0,0),jointGrip,10)

        # finish
        pygame.display.flip()
        clock.tick(FPS)
    # end of while
# end of main()

if __name__ == "__main__":
    main()
