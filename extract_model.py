import json
from utils import mkdir
from utils.reader import Reader


class Model(Reader):
    def __init__(self, folder):
        super().__init__(b'')

        with open(f'{folder}/scene.json') as fh:
            self.scene = json.load(fh)

        self.folder = folder
        
    def parse(self):
        with open('%s/master.mtl' % self.folder, 'w') as mtl:
            for mat in self.scene['materials']:
                name = mat['name']
                diffuse = mat['albedoTex']
                # specular = mat['extrasTex']

                # write to file
                mtl.write('newmtl {0}\n'.format(name))
                mtl.write('map_Ka {0}\n'.format(diffuse))
                mtl.write('map_Kd {0}\n'.format(diffuse))
                # omtl.write('map_Ks {0}\n\n'.format(specular))
            mtl.close()
    
        for mesh in self.scene['meshes']:
            name = mesh['name']
            filename = mesh['file']
            
            with open(f'{self.folder}/{filename}', 'rb') as dat_file:
                super().__init__(dat_file.read(), 'little')
                dat_file.close()

            # transform = mesh['transform']
            wire_count = mesh['wireCount']
            # index_count = mesh['indexCount']
            vertex_count = mesh['vertexCount']
    
            secondary_texcoord = 0
            if 'secondary_tex_coord' in mesh:
                secondary_texcoord = mesh['secondaryTexCoord']
    
            vertex_color = 0
            if 'vertexColor' in mesh:
                vertex_color = mesh['vertexColor']
    
            index_type_size = mesh['indexTypeSize']
    
            # TODO: BUG LONG INDICES 
            # if index_type_size == 4:
            #     raise Exception('Currently can\'t process any large files with long (uint32) indices... '
            #                     'To Be Updated!!!')

            mkdir(f'obj/{self.folder}')
            output = open(f'obj/{self.folder}/{filename}.obj', 'w')
            output.write('mtllib master.mtl\n')
    
            # lists
            faces = []
            vertices = []
            texcoords = []
            normals = []
            materials_list = []
    
            for sub_mesh in mesh['subMeshes']:
                face = []
                material = sub_mesh['material']
                index_count_2 = sub_mesh['indexCount']
                # wire_count_2 = sub_mesh['wireIndexCount']
    
                faces_count = index_count_2 // 3

                for x in range(faces_count):
                    face.append((
                        self.readUInt(index_type_size),
                        self.readUInt(index_type_size),
                        self.readUInt(index_type_size)
                    ))

                faces.append(face)
                materials_list.append(material)
    
            # skip unknown wire count
            self.read(wire_count * index_type_size)

            # vertices
            for v in range(vertex_count):
                vertex = (self.read_float(), self.read_float(), self.read_float())
                texcoord = (self.read_float(), self.read_float())
                if secondary_texcoord > 0:
                    self.read_float()  # u
                    self.read_float()  # v

                if vertex_color > 0:
                    self.read_float()

                normal = (self.read_float(), self.read_float(), self.read_float())
    
                vertices.append(vertex)
                texcoords.append(texcoord)
                normals.append(normal)

            for vertex in vertices:
                output.write('v {0} {1} {2}\n'.format(vertex[0], vertex[1], vertex[2]))
    
            for texcoord in texcoords:
                output.write('vt {0} {1}\n'.format(texcoord[0], 1-texcoord[1]))

            for normal in normals:
                output.write('vn {0} {1} {2}\n'.format(normal[0], normal[1], normal[2]))

            del vertex, texcoord, normal
            del vertices, texcoords, normals

            for x, faces in enumerate(faces):
                output.write('\n')
                output.write('g {0}\n'.format(name))
                output.write('usemtl {0}\n'.format(materials_list[x]))
    
                for face in faces:
                    output.write(
                        'f {0}/{0}/{0} {1}/{1}/{1} {2}/{2}/{2}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1)
                    )
            output.close()

        print('COMPLETED!!!')


if __name__ == '__main__':
    model = Model('x6k7oilwxr')
    model.parse()
