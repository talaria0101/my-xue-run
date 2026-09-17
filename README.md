# my-xue run

Running animation for the `my_xue` mouse model (Blender 3.6).

## Files

- `my_xue_run.blend` - the model with a 24-frame looping run cycle (frames 1-24, 24 fps). Open it and hit play. The action `ACMouse.ArmatureAction` is already assigned to the armature.
- `gen_run.py` - script used to write the animation keys directly into the blend file (no Blender needed).

## The cycle

- Diagonal trot: front left + hind right together, front right + hind left opposite.
- Upper legs swing, lower legs fold with a slight lag. Body bobs twice per stride, tail sways in a wave, ears flop behind the bob, head counter-bobs.
- All 175 F-curves (25 bones x location + quaternion) keyed at frames 1, 7, 13, 19, 25 (last duplicates first) with cyclic extrapolation.

## Source

Original static-pose model provided by The Watermelon. Rig: 25 bones, 1 mesh (789 verts).
