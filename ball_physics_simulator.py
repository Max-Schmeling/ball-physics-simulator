import tkinter as tk
import random
import math

intbool = {1: True, 0: False}


def RadianToDegree(radian):
    """ Converts radian to degrees """
    return radian * 180 / math.pi

def DegreeToRadian(angle):
    """ Converts degrees to radian """
    return angle *  math.pi / 180

def ColorShade(hexcode, factor=0.6):
    """ Creates a shade as determined by <factor> """
    r, g, b = tuple(int(hexcode.lstrip("#")[i:i+2], 16)*factor for i in (0, 2 ,4))
    newhex = "#{0:02x}{1:02x}{2:02x}".format(int(r), int(g), int(b)).upper()
    return newhex

def GetRandomColor():
    def RandomHexColor():
        return "#{:06x}".format(random.randint(0, 0xFFFFFF)).upper()
    color = RandomHexColor()
    colors_used.append(color)
    while color in colors_used:
        color = RandomHexColor()
    return color


class Ball(object):
    """ Base class for all balls in canvas """
    
    move_permission = True
    ground_gravity = 0.5 # Gravity of bottom
    
    def __init__(self, canvas, radius, xvelocity,
                 yvelocity, startpos=-1, color=-1):
        self.canvas = canvas
        self.color = color
        self.color2 = ColorShade(self.color)
        self.vx = xvelocity # Horizontal Velocity
        self.vy = yvelocity # Vertical Velocity
        self.draw_trajectory = False
        self.elasticity = 0.7 # Factor determining intensity of deceleration/elasticity
        
        # Set radius
        if 1 <= radius <= 100: 
            self.radius = radius
        else:
            self.radius = 10
        
        # Set start position
        assert type(startpos) == tuple or startpos == -1
        if startpos == -1:
            x = random.randint(0 + self.radius, self.canvas.width - self.radius)
            y = random.randint(0 + self.radius, self.canvas.height - self.radius)
        else:
            x, y = startpos
            
        # Instantiate ball object from canvas using the params specified
        self.ball = canvas.create_oval(x, y, x+radius*2, y+radius*2,
                                       fill=color,
                                       outline=self.color,
                                       activefill=self.color2,
                                       activeoutline=self.color2)
        # Add ball to dictionary
        balls[self.ball] = self
        
    def AllowMove(self):
        self.move_permission = True

    def DisallowMove(self):
        self.move_permission = False
    
    def GetPosition(self):
        x1, y1, x2, y2 = self.canvas.coords(self.ball)
        return self.CenterPosition(x1, y1, x2, y2)
    
    def CenterPosition(self, x1, y1, x2, y2):
        x, y = x1 + (x2 - x1)/2, y1 + (y2 - y1)/2        
        return (x, y)
    
    def isCollision(self, x1, y1, x2, y2, r1, r2):
        dist_sq = abs(x2-x1)**2 + abs(y2-y1)**2
        rad_sq = (r1 + r2)**2
        if dist_sq > 0.0:
            if dist_sq <= rad_sq:
                return True
        return False  
        
    def onEachFrame(self):
        if self.move_permission:
            x, y = self.GetPosition()
            
            if ground_has_gravity:
                elasticity = self.elasticity
            else:
                elasticity = 1
            
            # Accelerate by the factor equal to gravity
            if ground_has_gravity:
                self.vy += self.ground_gravity
            
            # Break vertical velocity down by the factor <friction>
            #self.vx *= 0.98
            
            # If object hits the BOTTOM reverse and decelerate object
            if y + self.radius >= self.canvas.height:
                self.canvas.move(self.ball, 0, self.canvas.height - y - self.radius)
                self.vy *= -elasticity
                
            # If object hits the TOP reverse and decelerate object
            if y - self.radius <= 0:
                self.canvas.move(self.ball, 0, -y + self.radius)
                self.vy *= -elasticity            
                
            # If object hits the RIGHT border reverse and decelerate object
            if x + self.radius >= self.canvas.width:
                self.canvas.move(self.ball, self.canvas.width - x - self.radius, 0)
                self.vx *= -elasticity
                
            # If object hits the LEFT border reverse and decelerate object
            if x - self.radius <= 0:
                self.canvas.move(self.ball, -x + self.radius, 0)
                self.vx *= -elasticity
            
            # Check for collision with other ball
            for ball in balls.keys():
                if ball != self.ball:
                    x2, y2 = balls[ball].GetPosition()
                    if self.isCollision(x, y, x2, y2, self.radius, balls[ball].radius):
                        self.vx *= -1
                        self.vy *= -1
                        print("collision")
            
            #new_x = self.speed*math.cos(DegreeToRadian(self.direction))
            #new_y = self.speed*math.sin(DegreeToRadian(self.direction))            
            
            # Move object by RELATIVE coordinates
            self.canvas.move(self.ball, self.vx, self.vy)
            
            # Trajectory trace
            if self.draw_trajectory:
                self.canvas.create_rectangle(x, y, x, y, fill=self.color2, outline=self.color2)
    
    
class Canvas(tk.Canvas):
    """ 2D Box for experiment around with physics """
    def __init__(self, parent, width, height):
        tk.Canvas.__init__(self, parent, width=width, height=height)
        self.config(background="#FFFFFF")
        
        self.width = width
        self.height = height
        self.SetFrameRate(30)
        
        self.running = False
        self.after(self.update_interval, self.UpdateFrame)
        
        self.bind("<B1-Motion>", self.onMotion)
        
    def SetFrameRate(self, fps=30):
        """
        Convert frame rate given in fps
        to microseconds delays between frames
        """
        self.fps = fps # frames per second
        self.update_interval = int(1000 / self.fps)
        if self.update_interval < 1:
            self.update_interval = 1        
        
    def Start(self):
        self.running = True
        print("Start")
        
    def Stop(self):
        self.running = False
        print("stop")
        
    def Reset(self):
        self.running = False
        for i in self.find_all():
            self.delete(i)
        balls.clear()
        print("Reset")
        
    def UpdateFrame(self):
        if self.running:
            #print("running at", self.fps, "fps")
            if len(balls) > 0:
                for ball in balls.keys():
                    balls[ball].onEachFrame()
            else:
                self.Reset()
        self.after(self.update_interval, self.UpdateFrame)
        
    def onMotion(self, event):
        print(event.x, event.y)
        
    def Rotate(self, coords):
        pass
        #self.coords(self.rect, 
        
    def CreateBall(self):
        ball = Ball(self,
                    radius=20,
                    xvelocity=-10.0,
                    yvelocity=12.0,
                    startpos=(self.width/2, self.height/2),
                    color=GetRandomColor())
        
        # General size and position settings
        #x, y = 250, 250 # rotation-axis position
        #axisratio_x = 0.5 # axis x position relative to rect
        #axisratio_y = 0.25 # axis y position relative to rect
        #width = 60 # rect width
        #height = 150 # rect height
        
        # Rotational Settings
        #angle = 180
        #offset_x = math.sin(DegreeToRadian(angle))*height
        #offset_y = math.cos(DegreeToRadian(angle))*width
        #self.rect = self.create_polygon(x-width*axisratio_x, y+height*axisratio_y, # Bottom Left
                                   #x+width*axisratio_x, y+height*axisratio_y, # Bottom Right
                                   #x+width*axisratio_x+offset_x, y-height*(1-axisratio_y)+offset_y, # Top Right
                                   #x-width*axisratio_x+offset_x, y-height*(1-axisratio_y)+offset_y) # Top Left
        

class Vector(object):
    """ Baseclass for 2-Dimensional vectors """
    def __init__(self, x, y):
        if not isinstance(x, (int, float)):
            raise ValueError(f"Unexpected data type {type(x)} for x")
        if not isinstance(y, (int, float)):
            raise ValueError(f"Unexpected data type {type(y)} for y")
        self.x = float(x)
        self.y = float(y)
        
    def GetVector(self):
        """ Returns the instance's vector as tuple """
        return (self.x, self.y)
    
    def GetAbs(self):
        """ Returns the vector's absolute value """
        return (self.x**2 + self.y**2)**0.5
    
    def GetScalar(self, vector):
        """ Returns the scalar of two given vectors"""
        return vector()[0] * self.x + vector()[1] * self.y
    
    def GetVectorProduct(self, vector):
        """ Returns the vector product of two given vectors (a x b) """
        return vector()[0] * self.y - vector()[1] * self.x
    
    def GetAngle(self, vector):
        """ Returns the angle between two vectors """
        scalar = self.GetScalar(vector)
        product = self.GetAbs() * vector.GetAbs()
        return RadianToDegree(math.acos(scalar / product))
    
    def __call__(self):
        """ Action called upon instance-call """
        return self.GetVector()
        
    def __str__(self):
        """ Action called upon str() call """
        return f"({self.x}, {self.y})"
    

class Window(tk.Tk):
    """ Window (User Interface) """
    def __init__(self):
        tk.Tk.__init__(self)
        
        # General Settings
        self.title("Ball Physics")
        #self.geometry(f"{1000}x{600}")
        self.resizable(0, 0)
        
        # Create canvas
        self.canvas = Canvas(self, 700, 400)
        self.canvas.grid(row=0, column=1, sticky="NSWE")
        
        # Create sidepanel for controls
        padding = 5
        sidepanel = tk.Frame(self, padx=padding, pady=padding)
        sidepanel.grid(row=0, column=0, sticky="NSWE")
        panel_ctrl = tk.Frame(sidepanel, bd=2, relief=tk.GROOVE, padx=padding, pady=padding)
        panel_ctrl.grid(row=0, column=0, sticky="NSWE")
        panel_general = tk.Frame(sidepanel, bd=2, relief=tk.GROOVE, padx=padding, pady=padding)
        panel_general.grid(row=1, column=0, sticky="NSWE")
        panel_obj = tk.Frame(sidepanel, bd=2, relief=tk.GROOVE, padx=padding, pady=padding)
        panel_obj.grid(row=2, column=0, sticky="NSWE")
        
        # Create control buttons
        self.str_option = tk.StringVar()
        self.str_option.set("Ball")
        self.int_bounce = tk.IntVar()
        self.int_bounce.set(1)
        self.int_groundg = tk.IntVar()
        self.int_groundg.set(1)
        self.int_trajectory = tk.IntVar()
        self.int_trajectory.set(0)
        
        label_ctrl = tk.Label(panel_ctrl, text="Control:")
        label_ctrl.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="NW")
        button_reset = tk.Button(panel_ctrl, text="Reset", command=self.canvas.Reset)
        button_reset.grid(row=1, column=0, rowspan=1, columnspan=1, sticky="NSWE")
        button_start = tk.Button(panel_ctrl, text="Start", command=self.canvas.Start)
        button_start.grid(row=1, column=1, rowspan=1, columnspan=1, sticky="NSWE")
        button_stop = tk.Button(panel_ctrl, text="Stop", command=self.canvas.Stop)
        button_stop.grid(row=1, column=2, rowspan=1, columnspan=1, sticky="NSWE")
        slider_fps = tk.Scale(panel_ctrl, from_=1, to=60, orient=tk.HORIZONTAL, command=lambda x: self.canvas.SetFrameRate(int(x)))
        slider_fps.set(30)
        slider_fps.grid(row=2, column=0, rowspan=1, columnspan=3, sticky="NSWE")
        
        
        label_general = tk.Label(panel_general, text="General Settings:")
        label_general.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="NW")
        check_bounce_on_collision = tk.Checkbutton(panel_general, text="Bounce on ball-collision",
                                                   offvalue=0, onvalue=1, variable=self.int_bounce)
        check_bounce_on_collision.grid(row=1, column=0, rowspan=1, columnspan=2, sticky="NW")        
        check_ground_gravity = tk.Checkbutton(panel_general, text="Ground has gravity",
                                              offvalue=0, onvalue=1, variable=self.int_groundg,
                                              command=self.onGroundGravity)
        check_ground_gravity.grid(row=2, column=0, rowspan=1, columnspan=2, sticky="NW")
        label_ground_gravity = tk.Label(panel_general, text="-> Magnitude of gravity:")
        label_ground_gravity.grid(row=3, column=0, rowspan=1, columnspan=2, sticky="NW")
        spin_ground_gravity = tk.Spinbox(panel_general,  from_=-100, to=100, increment=0.1, width=8)
        spin_ground_gravity.grid(row=3, column=2, rowspan=1, columnspan=1, sticky="NW")
        
        
        label_object = tk.Label(panel_obj, text="Object Settings:")
        label_object.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="NW")        
        balltype = tk.OptionMenu(panel_obj, self.str_option, "Ball")
        balltype.grid(row=1, column=0, rowspan=1, columnspan=2, sticky="NSWE")
        button_add = tk.Button(panel_obj, text="Spawn Ball", command=self.canvas.CreateBall)
        button_add.grid(row=1, column=2, rowspan=1, columnspan=1, sticky="NSWE")
        
        label_radius = tk.Label(panel_obj, text="Radius:")
        label_radius.grid(row=2, column=0, rowspan=1, columnspan=1, sticky="NW")
        spin_radius = tk.Spinbox(panel_obj,  from_=10, to=100, increment=1, width=8)
        spin_radius.grid(row=2, column=1, rowspan=1, columnspan=1, sticky="NW")
        
        label_pos = tk.Label(panel_obj, text="Position:")
        label_pos.grid(row=3, column=0, rowspan=1, columnspan=1, sticky="NW")
        spin_pos = tk.Spinbox(panel_obj,  from_=10, to=100, increment=1, width=8)
        spin_pos.grid(row=3, column=1, rowspan=1, columnspan=1, sticky="NW")  
        
        label_xvel = tk.Label(panel_obj, text="X-Velocity:")
        label_xvel.grid(row=4, column=0, rowspan=1, columnspan=1, sticky="NW")
        spin_xvel = tk.Spinbox(panel_obj,  from_=0, to=50, increment=1, width=8)
        spin_xvel.grid(row=4, column=1, rowspan=1, columnspan=1, sticky="NW")          
        
        label_yvel = tk.Label(panel_obj, text="Y-Velocity:")
        label_yvel.grid(row=5, column=0, rowspan=1, columnspan=1, sticky="NW")
        spin_yvel = tk.Spinbox(panel_obj,  from_=0, to=50, increment=1, width=8)
        spin_yvel.grid(row=5, column=1, rowspan=1, columnspan=1, sticky="NW")    
        
        check_trajectory = tk.Checkbutton(panel_obj, text="Draw trajectory", variable=self.int_trajectory)
        check_trajectory.grid(row=6, column=0, rowspan=1, columnspan=2, sticky="NW")
        
    def onGroundGravity(self):
        ground_has_gravity = intbool[self.int_groundg.get()]
    
    
if __name__ == "__main__":
    ground_has_gravity = True # If true objects will be affected by gravity of ground 
    bounce_on_collision = True # If true objects will bounce upon collision. Else: absorb
    colors_used = ["#FFFFFF"] # holds all currently chosen colors to avoid redundancies
    balls = {}
    root = Window()
    root.mainloop()
