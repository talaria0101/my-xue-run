# my-xue run

Running animation for the `my_xue` mouse model (Blender 3.6).

## Files

- `my_xue_run.blend` - the model with a looping run cycle (frames 1-12,
  0.46 s at 24 fps). Open it and hit play. The action
  `ACMouse.ArmatureAction` is already assigned to the armature.
- `gen_run.py` - script that writes the animation keys directly into the
  blend file (no Blender needed). Needs `resampled.json` beside it.
- `resampled.json` - motion curves sampled from the reference mouse
  (Sketchfab `Mouse` by charliecatling, CC-style Standard license, not
  included here), demeaned and rescaled in the script.

## The cycle

Retargeted from the reference mouse's `rig|run cycle`: a fast
bounding gallop, not a trot. Hind legs drive together, front legs
follow with a slight split, body surges and pumps once per stride,
tail streams, ears flop. All 175 F-curves (25 bones x location +
quaternion) keyed with 24 samples over the 0.46 s loop, cyclic.

## Source

Original static-pose model provided by The Watermelon. Rig: 25 bones,
1 mesh (789 verts).
