import webbrowser
import json
import numpy as np
from jinja2 import Template

class MeshConverter():
    def __init__(self):
        pass

    def scale_verts(self, x, y, z, face_type):
        x *= 2
        y *= 2
        z *= 2
        verts = []

        if face_type == 0: 
            verts = [(0.0 + x, 2.0 + y, 2.0 + z),
                    (0.0 + x, 0.0 + y, 2.0 + z),
                    (2.0 + x, 2.0 + y, 2.0 + z),
                    (2.0 + x, 0.0 + y, 2.0 + z)]

        elif face_type == 1: 
            verts = [(0.0 + x, 0.0 + y, 0.0 + z),
                    (2.0 + x, 0.0 + y, 0.0 + z),
                    (0.0 + x, 0.0 + y, 2.0 + z),               
                    (2.0 + x, 0.0 + y, 2.0 + z)]

        elif face_type == 2: 
            verts = [(0.0 + x, 2.0 + y, 0.0 + z),
                    (0.0 + x, 0.0 + y, 0.0 + z),
                    (2.0 + x, 2.0 + y, 0.0 + z),
                    (2.0 + x, 0.0 + y, 0.0 + z)]

        elif face_type == 3: 
            verts = [(0.0 + x, 2.0 + y, 0.0 + z),
                    (2.0 + x, 2.0 + y, 0.0 + z),
                    (0.0 + x, 2.0 + y, 2.0 + z),
                    (2.0 + x, 2.0 + y, 2.0 + z)]

        elif face_type == 4: 
            verts = [(2.0 + x, 2.0 + y, 0.0 + z),
                    (2.0 + x, 0.0 + y, 0.0 + z),
                    (2.0 + x, 2.0 + y, 2.0 + z),
                    (2.0 + x, 0.0 + y, 2.0 + z)]

        elif face_type == 5: 
            verts = [(0.0 + x, 2.0 + y, 0.0 + z),
                    (0.0 + x, 0.0 + y, 0.0 + z),
                    (0.0 + x, 2.0 + y, 2.0 + z),
                    (0.0 + x, 0.0 + y, 2.0 + z)]
        
        return verts

    def scale_faces(self, scale, face_type):

        faces = np.array([[[0, 1, 3, 2]],
                        [[0, 1, 3, 2]],
                        [[1, 0, 2, 3]],
                        [[1, 0, 2, 3]],
                        [[1, 0, 2, 3]],
                        [[0, 1, 3, 2]]])

        scaled_faces = faces[face_type] + 4 * scale
        return scaled_faces.tolist()

    def np2vox(self, bin_array):
        '''Convert binary numpy ndarray to indexed 3D mesh data'''

        print('--> BUILDING MESH')
        print('--> VOXEL VOLUME:', np.count_nonzero(bin_array))
        bin_array = np.fliplr(np.flipud(bin_array))
        verts = []
        faces = []
        x, y, z = bin_array.shape[0], bin_array.shape[1], bin_array.shape[2]
        x_max, y_max, z_max = x - 1, y - 1, z - 1
        count = 0
        bin_array[0, :, :] = 0
        bin_array[:, 0, :] = 0
        bin_array[:, :, 0] = 0
        bin_array[x_max, :, :] = 0
        bin_array[:, y_max, :] = 0
        bin_array[:, :, z_max] = 0
            
        for i in range(x): 
            for j in range(y):
                for k in range(z):

                    current = bin_array[i,j,k]

                    if i == x_max:
                        i = x_max - 1
                    elif i == 0:
                        i = 1
                    else: 
                        pass

                    if j == y_max:
                        j = y_max - 1
                    elif j == 0:
                        j = 1
                    else:
                        pass

                    if k == z_max:
                        k = z_max - 1 
                    elif k == 0:
                        k = 1
                    else:
                        pass

                    surrounding = np.array([bin_array[i,j+1,k],    
                                            bin_array[i-1,j,k], 
                                            bin_array[i,j-1,k], 
                                            bin_array[i+1,j,k], 
                                            bin_array[i,j,k+1], 
                                            bin_array[i,j,k-1]], dtype=int)
                    if current == 1:
                        for num in range(len(surrounding)):
                            if surrounding[num] == 0:
                                verts += self.scale_verts(k, i, j, num)
                                faces += self.scale_faces(count, num)
                                count += 1
        return verts, faces

    def render_voxels(self, voxels):
        '''Render np array in the browser as a mesh using np2vox func and three.js lib'''
        verts, faces = self.np2vox(voxels)
        mesh_data = {'verts': verts, 'faces': faces}
        json_mesh = json.dumps(mesh_data)

        html = Template('''<html>
                <head>
                    <title>Viewer</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
                    <link rel="stylesheet" type="text/css" href="css/styles.css"/>
                </head>
                <body>
                    <canvas id="canvas"></canvas>
                    <div id="top_panel"></div>
                    <div id="bottom_panel">  
                    </div>

                    <script src="js/three.min.js"></script>
                    <script src="js/OrbitControls.js"></script>
                
                    <script>
                        
                        var renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas'), antialias: true});
                    
                        var camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 10000);
                        var scene = new THREE.Scene();

                        //renderer
                        renderer.setClearColor(0x37373B); 
                        renderer.setSize(window.innerWidth, window.innerHeight);
                        renderer.setPixelRatio(window.devicePixelRatio);
                        document.body.appendChild(renderer.domElement);
                        
                        //scene and camera setup
                        camera.position.set(-200, 200, -200);
                        camera.up = new THREE.Vector3(0, 1, 0);
                        camera.lookAt(new THREE.Vector3(0, 0, 0))
                        scene.add(camera);
                    
                        //controls
                        var controls = new THREE.OrbitControls(camera, renderer.domElement);
                        controls.target.set( 0, 0, 0);
                        controls.update();
                        //controls.minDistance = 150;
                        controls.maxDistance = 2000;
                        controls.zoomSpeed = 0.5;
                        controls.enablePan = true;
                        controls.rotateSpeed = 0.5;

                        //lights
                        var light1 = new THREE.AmbientLight(0xffffff, 1.0);
                        scene.add(light1);

                        var light2 = new THREE.PointLight(0xff3333, 0.75);
                        light2.position.set(100, 200, 500);
                        scene.add(light2)
                        var light4 = new THREE.PointLight(0x3333ff, 0.75);
                        light2.position.set(-100, 200, -500);
                        scene.add(light4)

                        var light3 = new THREE.SpotLight(0xddddff, 1);
                        light3.position.set(-300, -300, 300);
                        scene.add(light3);

                        window.addEventListener('resize',windowResize, false);

                        function windowResize(){
                            camera.aspect = window.innerWidth / window.innerHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize( window.innerWidth, window.innerHeight);
                        }

                        function render() {
                            requestAnimationFrame(render);
                            renderer.render(scene, camera);
                        }

                        var mesh_data = JSON.parse(JSON.stringify({{ data }}));
                        console.log(mesh_data)
                        var verts = mesh_data.verts;
                        var faces = mesh_data.faces;
                    
                        var geometry = new THREE.Geometry();

                        for (i=0; i < verts.length; i++){
                            geometry.vertices.push(new THREE.Vector3(verts[i][1], verts[i][2], verts[i][0]));
                        }
                        for (i=0; i < faces.length; i++){
                            geometry.faces.push(new THREE.Face3(faces[i][0], faces[i][1], faces[i][2]));
                            geometry.faces.push(new THREE.Face3(faces[i][2], faces[i][3], faces[i][0]));
                        }
                        console.log('computing normals');
                        geometry.computeBoundingSphere();
                        geometry.computeFaceNormals();
                        geometry.computeVertexNormals();
                        console.log('building scene');

                        var material = new THREE.MeshLambertMaterial({

                                    color: 0x616c72,
                                
                                    
                        });
                        var material1 = new THREE.MeshLambertMaterial({

                                    color: 0x000000,
                                    wireframe: true,
                                    transparent: true,
                                    opacity: 0.7,                                
                        });
                        
                        
                        var voxmesh = new THREE.Mesh(geometry, material);
                        var voxmeshW = new THREE.Mesh(geometry, material1);
                        var geo = new THREE.PlaneGeometry(200, 200);
                        var mat = new THREE.MeshLambertMaterial({

                                    color: 0xe0e3e5,
                                    wireframe: false,
                                    transparent: true,
                                    opacity: 0.7,
                                    side: THREE.DoubleSide
                                    
                        });
                        var plane = new THREE.Mesh(geo, mat);
                        plane.rotateX(Math.PI / 2);
                        scene.add(plane);
                        scene.add(voxmesh);
                    // scene.add(voxmeshW);
                        var x = {{x}};
                        var y = {{y}};
                        var z = {{z}};
                        voxmesh.position.set(x, y, z);
                        //voxmeshW.position.set(x, y, z);

                        var cube_geo = new THREE.BoxGeometry(5, 5, 5);
                        var cube_mat = new THREE.MeshLambertMaterial({ color: 0x442222});
                        var cube = new THREE.Mesh(cube_geo, cube_mat);
                        scene.add(cube);
                        cube.position.set(-102.5, 0, -102.5);

                        render();
                    </script>
                </body>
            </html>''')
        
        new_html = html.render(data=json_mesh, x=-voxels.shape[0], y=voxels.shape[1] / 2, z=-voxels.shape[2])
        path = './templates/template.html'
        with open(path, 'w') as f:
            f.write(new_html)
        webbrowser.open(path, new=2)

    def render_voxel_ani(self, vox_list, delay):
        '''Displays list of np arrays in the browser as a mesh using np2vox func and three.js lib'''    
        verts_list = []
        faces_list = []
        for vox in vox_list:
            # compute the mesh data for each voxel array
            verts, faces = self.np2vox(vox)
            verts_list.append(verts)
            faces_list.append(faces)
        # json version of list of mesh data
        mesh_data = {'verts': verts_list, 'faces': faces_list}
        json_meshes = json.dumps(mesh_data)
        html = Template('''<html>
                <head>
                    <title>Viewer</title>
                    <meta charset="utf-8">
                    <meta name="viewport" content="width=device-width, user-scalable=no, minimum-scale=1.0, maximum-scale=1.0">
                    <link rel="stylesheet" type="text/css" href="css/styles.css"/>
                </head>
                <body>
                    <canvas id="canvas"></canvas>
                    <div id="top_panel"></div>
                    <div id="bottom_panel">  
                    </div>

                    <script src="js/three.min.js"></script>
                    <script src="js/OrbitControls.js"></script>
                
                    <script>
                        var renderer = new THREE.WebGLRenderer({canvas: document.getElementById('canvas'), antialias: true});
                        var camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.1, 10000);
                        var scene = new THREE.Scene();

                        renderer.setClearColor(0x37373B); 
                        renderer.setSize(window.innerWidth, window.innerHeight);
                        renderer.setPixelRatio(window.devicePixelRatio);
                        document.body.appendChild(renderer.domElement);
                        
                        //scene and camera setup
                        camera.position.set(-200, 200, -200);
                        camera.up = new THREE.Vector3(0, 1, 0);
                        camera.lookAt(new THREE.Vector3(0, 0, 0))
                        scene.add(camera);
                    
                        //controls
                        var controls = new THREE.OrbitControls(camera, renderer.domElement);
                        controls.target.set( 0, 0, 0);
                        controls.update();
                        //controls.minDistance = 150;
                        controls.maxDistance = 2000;
                        controls.zoomSpeed = 0.5;
                        controls.enablePan = true;
                        controls.rotateSpeed = 0.5;

                        //lights
                        var light1 = new THREE.AmbientLight(0xffffff, 1.0);
                        scene.add(light1);
                        var light2 = new THREE.PointLight(0xff3333, 0.75);
                        light2.position.set(100, 200, 500);
                        scene.add(light2)
                        var light4 = new THREE.PointLight(0x3333ff, 0.75);
                        light2.position.set(-100, 200, -500);
                        scene.add(light4)
                        var light3 = new THREE.SpotLight(0xddddff, 1);
                        light3.position.set(-300, -300, 300);
                        scene.add(light3);

                        window.addEventListener('resize',windowResize, false);

                        function windowResize(){
                            camera.aspect = window.innerWidth / window.innerHeight;
                            camera.updateProjectionMatrix();
                            renderer.setSize( window.innerWidth, window.innerHeight);
                        }

                        function render() {
                            requestAnimationFrame(render);
                            renderer.render(scene, camera);
                        }

                        var material = new THREE.MeshLambertMaterial({color: 0x616c72});
                        var material1 = new THREE.MeshLambertMaterial({
                                    color: 0x000000,
                                    wireframe: true,
                                    transparent: true,
                                    opacity: 0.7,                                
                        });

                        var geo = new THREE.PlaneGeometry(200, 200);
                        var mat = new THREE.MeshLambertMaterial({
                                    color: 0xe0e3e5,
                                    wireframe: false,
                                    transparent: true,
                                    opacity: 0.7,
                                    side: THREE.DoubleSide 
                        });

                        var plane = new THREE.Mesh(geo, mat);
                        plane.rotateX(Math.PI / 2);
                        scene.add(plane);
                        var x = {{x}};
                        var y = {{y}};
                        var z = {{z}};
                        var cube_geo = new THREE.BoxGeometry(5, 5, 5);
                        var cube_mat = new THREE.MeshLambertMaterial({ color: 0x442222});
                        var cube = new THREE.Mesh(cube_geo, cube_mat);
                        scene.add(cube);
                        cube.position.set(-102.5, 0, -102.5);
                        
                        // mesh
                        var mesh_data = JSON.parse(JSON.stringify({{ mesh_list }}));
                        var verts_list = mesh_data.verts;
                        var faces_list = mesh_data.faces;

                        for (j=0; j < verts_list.length; j++)
                        {
                            // build each object as a three js mesh
                            verts = verts_list[j];
                            faces = faces_list[j];
                            
                            var geometry = new THREE.Geometry();
                            for (i=0; i < verts.length; i++){
                                geometry.vertices.push(new THREE.Vector3(verts[i][1], verts[i][2], verts[i][0]));
                            }
                            for (i=0; i < faces.length; i++){
                                geometry.faces.push(new THREE.Face3(faces[i][0], faces[i][1], faces[i][2]));
                                geometry.faces.push(new THREE.Face3(faces[i][2], faces[i][3], faces[i][0]));
                            }
                            geometry.computeBoundingSphere();
                            geometry.computeFaceNormals();
                            geometry.computeVertexNormals();
                            var voxmesh = new THREE.Mesh(geometry, material);
                            voxmesh.name = 'mesh' + i.toString();
                            voxmesh.visible = false;
                            voxmesh.position.set(x, y, z);
                            scene.add(voxmesh);
                            console.log('built mesh');
                        }

                        var delay = {{ speed }};
                        var i = 7;
                        setInterval(function()
                        {
                            if (i == scene.children.length - 1){
                                scene.children[i-1].visible = false;
                                i = 7;
                            } else {
                                if (i != 7){
                                    scene.children[i-1].visible = false;
                                }
                                scene.children[i].visible = true;
                                i++;
                            }
                        }, delay);

                        render();
                    </script>
                </body>
            </html>''')

        new_html = html.render(mesh_list=json_meshes, 
                                x=-vox_list[0].shape[0], 
                                y=vox_list[0].shape[1] / 2, 
                                z=-vox_list[0].shape[2],
                                speed=delay)
        
        path = './templates/template_ani.html'
        with open(path, 'w') as f:
            f.write(new_html)
        webbrowser.open(path, new=2) 