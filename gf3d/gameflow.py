import http.server
import socketserver
import webbrowser
import os
import threading
import shutil

print("GF3D 1.0.1")
print("GF3D is part of and developed from Xyteorize Games")

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

    def _generate_html(self, title, icon_path):
        components = "\n                ".join(self.nodes)
        updates = "\n                    ".join(self.animations)
        scripts = "\n        ".join(self.external_scripts)
        icon_tag = f'<link rel="icon" href="{icon_path}">' if icon_path else ""
        shader_js = ""
        for s_id, code in self.shaders.items():
            shader_js += f"const {s_id}_vert = `{code['vert']}`;\n"
            shader_js += f"const {s_id}_frag = `{code['frag']}`;\n"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            {icon_tag}
            <style>body {{ margin: 0; overflow: hidden; background: #000; }}</style>
            {scripts}
            <script type="importmap">
                {{
                    "imports": {{
                        "three": "/node_modules/three/build/three.module.js",
                        "three/addons/": "/node_modules/three/examples/jsm/"
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
                import {{ FBXLoader }} from 'three/addons/loaders/FBXLoader.js';

                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 10000);
                const renderer = new THREE.WebGLRenderer({{ antialias: true }});
                const clock = new THREE.Clock();
                const mixers = []; 

                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(window.devicePixelRatio);
                document.body.appendChild(renderer.domElement);
                camera.position.set(5, 5, 5);

                window.playAnimation = (object, clipName = "mixamo.com") => {{
                    if (object.animations && object.animations.length > 0) {{
                        const mixer = new THREE.AnimationMixer(object);
                        const clip = object.animations.find(a => a.name.includes(clipName)) || object.animations[0];
                        const action = mixer.clipAction(clip);
                        action.play();
                        mixers.push(mixer);
                        return mixer;
                    }}
                    return null;
                }};

                {shader_js}
                {components}

                function animate() {{
                    requestAnimationFrame(animate);
                    const delta = clock.getDelta();
                    mixers.forEach(mixer => mixer.update(delta));
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
                
                window.mixers = mixers;
                window.THREE = THREE;
            </script>
        </body>
        </html>
        """

    def run(self, port=8080, use_window=False, title="GF3D Engine", icon=None, fullscreen=False):
        if not os.path.exists("build"): 
            os.makedirs("build")
        
        if os.path.exists("assets"):
            dest_assets = os.path.join("build", "assets")
            if os.path.exists(dest_assets): shutil.rmtree(dest_assets)
            shutil.copytree("assets", dest_assets)
            print(f"[*] Assets synced to build/assets")

        dest_modules = os.path.join("build", "node_modules")
        if not os.path.exists(dest_modules):
            lib_path = os.path.dirname(__file__)
            local_node = os.path.join(lib_path, "node_modules")
            root_node = "node_modules"
            source = root_node if os.path.exists(root_node) else local_node
            
            if os.path.exists(source):
                try:
                    shutil.copytree(source, dest_modules)
                    print(f"[*] node_modules synced to build/")
                except Exception as e:
                    print(f"[!] Sync error: {e}")
            else:
                print("[!] Error: node_modules not found!")
        else:
            print("[*] node_modules already exists in build/. Skipping copy.")

        icon_filename = None
        if icon and os.path.exists(icon):
            icon_filename = os.path.basename(icon)
            shutil.copy(icon, f"build/{icon_filename}")

        with open("build/index.html", "w") as f: 
            f.write(self._generate_html(title, icon_filename))
        
        os.chdir("build")

        class GF3DHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                self.send_header('Access-Control-Allow-Origin', '*')
                super().end_headers()

        GF3DHandler.extensions_map.update({
            '.js': 'application/javascript',
            '.mjs': 'application/javascript',
        })

        socketserver.TCPServer.allow_reuse_address = True
        httpd = socketserver.TCPServer(("", port), GF3DHandler)
        url = f"http://localhost:{port}"
        
        if use_window:
            import webview
            server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            server_thread.start()
            webview.create_window(title, url, width=1280, height=720, fullscreen=fullscreen)
            webview.start()
        else:
            webbrowser.open(url)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()
