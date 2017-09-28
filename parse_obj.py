

class Color:

    def __init__(self, r,g,b,a=1, name = None):
        self.r = r
        self.g = g
        self.b = b
        self.a = a
        
        self.name = name
        
    def print_C_code(self):
        return 'glColor4f({0},{1},{2},{3});\n\n'.format(self.r, self.g, self.b, self.a)
        
    def find_color_by_name(colors_list, name):
        return [c for c in colors_list if c.name == name][0] # TODO: class for color pallete
        
COLOR_RED = Color(1,0,0)
COLOR_GREEN = Color(0,1,0)
COLOR_BLUE = Color(0,0,1)

COLORS_LIST = [COLOR_RED, COLOR_GREEN, COLOR_BLUE]

class Verticle:

    def __init__(self, x,y,z, color = None):
        self.x = x
        self.y = y
        self.z = z
        
        self.color = color
    
    def print_C_code(self):
        code_line = 'glVertex3f({0},{1},{2});\n'.format(self.x,self.y,self.z)
        if self.color is not None:
            # vertex colors are disabled for now
            # code_line = 'glColor3f({0},{1},{2});\n'.format(self.color.r, self.color.g, self.color.b) + code_line
            None
        return code_line
        
    def print_color(self,r,g,b):
        return ''
        
        
class Novel:

    def __init__(self, x,y,z):
        self.x = x
        self.y = y
        self.z = z
        
class Face:

    def __init__(self, vert_list, color = None):
        self.vert_list  = vert_list
        self.color = color
        
        # set up right mode
        if len(vert_list) == 2:
            self.mode = 'GL_LINES'
        elif len(vert_list) == 3:
            self.mode = 'GL_TRIANGLES'
        elif len(vert_list) == 4:
            self.mode = 'GL_QUADS'
        elif len(vert_list) > 4:
            self.mode = 'GL_POLYGON'
        else:
            raise Error('aaaaaaaaa') # TODO
            
    
    def print_C_code(self):
    
        begin_line = 'glBegin ({0});\n\n'.format(self.mode)
        if self.color:
            color_line = self.color.print_C_code()
        else:
            color_line = ''
        vertex_lines = [ver.print_C_code() for ver in self.vert_list]          
        end_line = '\nglEnd();\n\n\n'
        
        return begin_line + color_line + ''.join(vertex_lines) + end_line
    
    
class Object:

    def __init__(self, name, face_list = None, color = None): 
        self.name = name.replace('.','_')
        if face_list:
            self.face_list = face_list
        else:
            self.face_list = []
        self.color = color # not implemented yet
    
    def append_face(self, face):
        self.face_list.append(face)
    
    def print_C_code(self):
        
        func_begin_line = 'void draw_{0}() {{\n\n'.format(self.name)
        
        face_lines = [face.print_C_code().replace('\n','\n\t') for face in self.face_list]
        
        func_end_line = '};\n\n'
        
        return func_begin_line + '\t' + ''.join(face_lines)[:-2] + func_end_line
        
    def print_function_declaration(self):
        
        return 'void draw_{0}();\n'.format(self.name)
        
    def print_function_call(self):
        
        return 'draw_{0}();\n'.format(self.name)
        


def parse_mtl(file_name):

    color_list = []
    
    with open(file_name+'.mtl', 'r') as file:
        lines = file.read().split('\n')
        for line in lines:
            words = line.split(' ')
            if words[0] == 'newmtl':
                new_mat_name = '_'.join(words[1:])
            elif words[0] == 'Kd':         
                color_list.append(Color(words[1],words[2], words[3], name=new_mat_name))
                
    return color_list
        

def parse_obj(file_name):

    RESULT_FILE = 'result' # TODO:
    
    color_list = parse_mtl(file_name)
    
    objects = []
    verticies = []
    
    with open(file_name+'.obj', 'r') as file:
        lines = file.read().split('\n')
        for line in lines:
            words = line.split(' ')
            if words[0] == 'o':
                new_object = Object('_'.join(words[1:]))
                objects.append(new_object)
                current_object = new_object
            elif words[0] == 'usemtl':
                cur_color_name = '_'.join(words[1:])
                cur_color = Color.find_color_by_name(color_list, cur_color_name)
            elif words[0] == 'v':
                new_vertex = Verticle(words[1], words[2], words[3])
                verticies.append(new_vertex)
            elif words[0] == 'f':
                new_face = Face([verticies[int(ver.split('/')[0]) - 1] for ver in words[1:]],
                                color = cur_color)
                current_object.append_face(new_face)
                
        file.close()
    
    write_objects(RESULT_FILE, objects)
    
    
def write_objects(file_name, object_list):
    
    with open(file_name+'.cpp', 'w') as result_file:    
    
        for o in object_list:
            result_file.write(o.print_function_declaration())
    
        for o in object_list:
            result_file.write(o.print_C_code())
            
        result_file.close()
        


def main():
    import sys

    if "--help" in sys.argv:
        print(__doc__)
        return

    for arg in sys.argv[1:]:
        try:
            parse_obj(arg)
        except:
            print("Failed to convert %r, error:" % arg)

            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()