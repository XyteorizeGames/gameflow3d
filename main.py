from gf3d.gameflow import GF3D

app = GF3D()

app.add_shader_file("skyShader", "shaders/sky_v.glsl", "shaders/sky_f.glsl")

app.add_component("sky", """Mesh(
    new THREE.SphereGeometry(500, 32, 32),
    new THREE.ShaderMaterial({
        vertexShader: skyShader_vert,
        fragmentShader: skyShader_frag,
        side: THREE.BackSide,
        uniforms: {
            topColor: { value: new THREE.Color(0x0077ff) },
            bottomColor: { value: new THREE.Color(0xffffff) },
            offset: { value: 33.0 },
            exponent: { value: 0.6 }
        }
    })
)""")

app.add_component("*", "AmbientLight(0xffffff, 0.7)")

app.add_component("box", "Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({color: 0xff0055}))")

app.add_custom_js("""
    const orbit = new OrbitControls(camera, renderer.domElement);
    
    const transform = new TransformControls(camera, renderer.domElement);
    transform.attach(box);
    scene.add(transform);

    transform.addEventListener('dragging-changed', (event) => {
        orbit.enabled = !event.value;
    });

    window.addEventListener('keydown', (event) => {
        switch (event.key) {
            case 'g': transform.setMode('translate'); break;
            case 'r': transform.setMode('rotate'); break;
            case 's': transform.setMode('scale'); break;
        }
    });
""")

if __name__ == "__main__":
    app.run(port=2121)