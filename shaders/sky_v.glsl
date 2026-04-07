varying vec3 vWorldPosition;

void main() {
    // We calculate the position in world space to get an accurate 'height' (y)
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;

    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}