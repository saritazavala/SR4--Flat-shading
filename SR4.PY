#SR4
#Graficas 
#Sara Zavala 18893
#Universidad del Valle

import struct 
from Obj import Obj
from collections import namedtuple
V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])


# -----------------------------------------------------------------------

def char(c):
    return struct.pack('=c', c.encode('ascii'))

# 2 bytes
def word(c):
    return struct.pack('=h', c)

# 4 bytes
def dword(c):
    return struct.pack('=l', c)

def color(red, green, blue):
     return bytes([round(blue * 255), round(green * 255), round(red * 255)])

def color2(r, g, b):
  return bytes([b, g, r])     


# Funciones matematicas dadas por Denis en clase ----------------------------
#


def sum(v0, v1):
  return V3(v0.x + v1.x, v0.y + v1.y, v0.z + v1.z)

def sub(v0, v1):
  return V3(v0.x - v1.x, v0.y - v1.y, v0.z - v1.z)

def mul(v0, k):
  return V3(v0.x * k, v0.y * k, v0.z *k)

def dot(v0, v1):
  return v0.x * v1.x + v0.y * v1.y + v0.z * v1.z

def cross(v1, v2):
  return V3(
    v1.y * v2.z - v1.z * v2.y,
    v1.z * v2.x - v1.x * v2.z,
    v1.x * v2.y - v1.y * v2.x,
  )

def length(v0):
  return (v0.x**2 + v0.y**2 + v0.z**2)**0.5

def norm(v0):
  v0length = length(v0)

  if not v0length:
    return V3(0, 0, 0)

  return V3(v0.x/v0length, v0.y/v0length, v0.z/v0length)

def bbox(*vertices):

  xs = [ vertex.x for vertex in vertices ]
  ys = [ vertex.y for vertex in vertices ]

  return (max(xs), max(ys), min(xs), min(ys))

def barycentric(A, B, C, P):
  cx, cy, cz = cross(
    V3(B.x - A.x, C.x - A.x, A.x - P.x), 
    V3(B.y - A.y, C.y - A.y, A.y - P.y)
  )

  if abs(cz) < 1:
    return -1, -1, -1   


  u = cx/cz
  v = cy/cz
  w = 1 - (cx + cy)/cz

  return w, v, u



# -------------------------------------------------------------------------


class Render(object):

    #Initial values -------------------------------

    def __init__(self, filename):
        self.width = 0
        self.height = 0
        self.framebuffer = []
        self.change_color = color(0,0,0)
        self.filename = filename
        self.x_position = 0
        self.y_position = 0
        self.ViewPort_height = 0
        self.ViewPort_width = 0
        self.glClear()

    
    #File Header ----------------------------------

    def header(self):
        doc = open(self.filename,'bw')
        doc.write(char('B'))
        doc.write(char('M'))
        doc.write(dword(54 + self.width * self.height * 3))
        doc.write(dword(0))
        doc.write(dword(54))
        self.info(doc)
        
        
    #Info header ---------------------------------------

    def info(self, doc):
        doc.write(dword(40))
        doc.write(dword(self.width))
        doc.write(dword(self.height))
        doc.write(word(1))
        doc.write(word(24))
        doc.write(dword(0))
        doc.write(dword(self.width * self.height * 3))
        doc.write(dword(0))
        doc.write(dword(0))
        doc.write(dword(0))
        doc.write(dword(0))
        
        #Image ----------------------------------
        for x in range(self.height):
            for y in range(self.width):
                doc.write(self.framebuffer[x][y])
        doc.close()


    #Cleans a full image with the color defined in "change_color"
    def glClear(self):
        self.framebuffer = [[self.change_color for x in range(self.width)] for y in range(self.height)]
        self.zbuffer = [[-float('inf') for x in range(self.width)] for y in range(self.height)]

    #Writes all the doc
    def glFinish(self):
        self.header()
        
    #Draws a point according ot frameBuffer
    def glpoint(self, x, y):
        self.framebuffer[y][x] = self.change_color

    #Creates a window 
    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
    
    #MODELS --------------------------------------
    def triangle(self, A, B, C):
        xmax, ymax, xmin, ymin = bbox(A, B, C)
        
        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                P = V2(x, y)
                w, v, u = barycentric(A, B, C, P)
                if w < 0 or v < 0 or u < 0:
                    continue
                z = A.z * w + B.z * u + C.z * v
                try:
                    if z > self.zbuffer[x][y]:
                        self.glpoint(x,y)
                        self.zbuffer[x][y] = z
                except:
                    pass

    #New function for loading my .obj
    def load_model(self, filename, translate=(0, 0, 0), scale=(1, 1, 1)):
        model = Obj(filename)

        light = V3(0, 0, 1)
    
        for face in model.faces:
            vcount = len(face)
            
            if vcount == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = V3(model.vertex[f1][0], model.vertex[f1][1], model.vertex[f1][2])
                v2 = V3(model.vertex[f2][0], model.vertex[f2][1], model.vertex[f2][2])
                v3 = V3(model.vertex[f3][0], model.vertex[f3][1], model.vertex[f3][2])

                x1 = round((v1.x * scale[0]) + translate[0])
                y1 = round((v1.y * scale[1]) + translate[1])
                z1 = round((v1.z * scale[2]) + translate[2])

                x2 = round((v2.x * scale[0]) + translate[0])
                y2 = round((v2.y * scale[1]) + translate[1])
                z2 = round((v2.z * scale[2]) + translate[2])

                x3 = round((v3.x * scale[0]) + translate[0])
                y3 = round((v3.y * scale[1]) + translate[1])
                z3 = round((v3.z * scale[2]) + translate[2])

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)

                normal = norm(cross(sub(B, A), sub(C, A)))
                intensity = dot(normal, light)
                grey = round(255 * intensity)
               
                
                if grey < 0:
                    continue 

                self.change_color = color2(grey, grey, grey)

                self.triangle(A, B, C)

            else:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1   

                v1 = V3(model.vertex[f1][0], model.vertex[f1][1], model.vertex[f1][2])
                v2 = V3(model.vertex[f2][0], model.vertex[f2][1], model.vertex[f2][2])
                v3 = V3(model.vertex[f3][0], model.vertex[f3][1], model.vertex[f3][2])
                v4 = V3(model.vertex[f4][0], model.vertex[f4][1], model.vertex[f4][2])

                x1 = round((v1.x * scale[0]) + translate[0])
                y1 = round((v1.y * scale[1]) + translate[1])
                z1 = round((v1.z * scale[2]) + translate[2])

                x2 = round((v2.x * scale[0]) + translate[0])
                y2 = round((v2.y * scale[1]) + translate[1])
                z2 = round((v2.z * scale[2]) + translate[2])

                x3 = round((v3.x * scale[0]) + translate[0])
                y3 = round((v3.y * scale[1]) + translate[1])
                z3 = round((v3.z * scale[2]) + translate[2])

                x4 = round((v4.x * scale[0]) + translate[0])
                y4 = round((v4.y * scale[1]) + translate[1])
                z4 = round((v4.z * scale[2]) + translate[2])

                A = V3(x1, y1, z1)
                B = V3(x2, y2, z2)
                C = V3(x3, y3, z3)
                D = V3(x4, y4, z4)
                
                normal = norm(cross(sub(B, A), sub(C, A)))  
                intensity = dot(normal, light)
                grey = round(255 * intensity)
                if grey < 0:
                    continue 

                self.change_color = color2(grey, grey, grey)
               
                self.triangle(A, B, C) 

                self.triangle(A, D, C)

 

r = Render('Carota.bmp')
r.glCreateWindow(800, 600)
r.glClear()
r.load_model('./face.obj', (400, 300, 0), (15, 15, 15))
r.glFinish()


