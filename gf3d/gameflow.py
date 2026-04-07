import http.server
import socketserver
import webbrowser
import os

class GF3D:
    def __init__(self):
        self.nodes = []
        self.animations = []
        self.external_scripts = []
        self.shaders = {} 

    def add_component(self, name, params):
        clean_params = params.strip()
        if clean_params.startswith("new ") or clean_params.startswith("THREE."):
            js_constructor = clean_params
        else:
            js_constructor = f"new THREE.{clean_params}"

        if name in ["*", "."]:
            js_code = f"scene.add({js_constructor});"
        else:
            js_code = f"const {name} = {js_constructor}; scene.add({name});"
        
        self.nodes.append(js_code)

    def add_custom_js(self, js_code):
        self.nodes.append(js_code)

    def add_shader(self, shader_id, vertex_code, fragment_code):
        self.shaders[shader_id] = {'vert': vertex_code, 'frag': fragment_code}

    def add_shader_file(self, shader_id, vert_path, frag_path):
        with open(vert_path, 'r') as v, open(frag_path, 'r') as f:
            self.add_shader(shader_id, v.read(), f.read())

    def on_update(self, js_code):
        self.animations.append(js_code)

    def attach_script(self, url):
        self.external_scripts.append(f'<script src="{url}"></script>')

    def load_plugin(self, file_path):
        if file_path.endswith('.js'):
            self.attach_script(file_path)
        elif file_path.endswith('.py'):
            with open(file_path, 'r') as f:
                self.add_custom_js(f.read())
        elif file_path.endswith('.glsl'):
            with open(file_path, 'r') as f:
                self.add_custom_js(f.read())

    def _generate_html(self):
        components = "\n                ".join(self.nodes)
        updates = "\n                    ".join(self.animations)
        scripts = "\n        ".join(self.external_scripts)
        
        shader_js = ""
        for s_id, code in self.shaders.items():
            shader_js += f"const {s_id}_vert = `{code['vert']}`;\n"
            shader_js += f"const {s_id}_frag = `{code['frag']}`;\n"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gameflow3D Pro</title>
            <style>body {{ margin: 0; overflow: hidden; background: #000; }}</style>
            {scripts}
            <script type="importmap">
                {{
                    "imports": {{
                        "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
                        "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
                    }}
                }}
            </script>
        </head>
        <body>
            <script type="module">
                import * as THREE from 'three';
                import {{ TransformControls }} from 'three/addons/controls/TransformControls.js';
                import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
                import {{ GLTFLoader }} from 'three/addons/loaders/GLTFLoader.js';

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                const clock = new THREE.Clock();
                const mixers = []; 

                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                document.body.appendChild(renderer.domElement);
                camera.position.set(5, 5, 5);

                {shader_js}
                {components}

                function animate() {{
                    requestAnimationFrame(animate);
                    const delta = clock.getDelta();
                    mixers.forEach(m => m.update(delta));
                    if (typeof orbit !== 'undefined') orbit.update();
                    {updates}
                    renderer.render(scene, camera);
                }}
                animate();

                window.addEventListener('resize', () => {{
                    camera.aspect = window.innerWidth / window.innerHeight;
                    camera.updateProjectionMatrix();
                    renderer.setSize(window.innerWidth, window.innerHeight);
                }});
            </script>
        </body>
        </html>
        """

    def run(self, port=8080):
        if not os.path.exists("build"): os.makedirs("build")
        with open("build/index.html", "w") as f: f.write(self._generate_html())
        os.chdir("build")
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler) as httpd:
            webbrowser.open(f"http://localhost:{port}")
            try: httpd.serve_forever()
            except KeyboardInterrupt: httpd.shutdown()