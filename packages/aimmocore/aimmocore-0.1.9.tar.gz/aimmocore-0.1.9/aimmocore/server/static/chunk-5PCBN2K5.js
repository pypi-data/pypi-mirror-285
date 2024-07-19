// node_modules/three/src/math/MathUtils.js
var DEG2RAD = Math.PI / 180;
var RAD2DEG = 180 / Math.PI;
function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}
function euclideanModulo(n, m) {
  return (n % m + m) % m;
}
function lerp(x, y, t) {
  return (1 - t) * x + t * y;
}

export {
  clamp,
  euclideanModulo,
  lerp
};
