uniform vec3 topColor;
uniform vec3 bottomColor;
uniform float offset;
uniform float exponent;
varying vec3 vWorldPosition;

void main() {
    // We normalize the world position and add the offset to shift the horizon line
    // normalize(vWorldPosition).y gives us a value from -1 to 1 based on height
    float h = normalize(vWorldPosition + vec3(0.0, offset, 0.0)).y;
    
    // We use max(h, 0.0) so the bottom half of the sphere remains the bottomColor
    float factor = max(pow(max(h, 0.0), exponent), 0.0);
    
    gl_FragColor = vec4(mix(bottomColor, topColor, factor), 1.0);
}