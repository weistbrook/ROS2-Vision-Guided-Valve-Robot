std_msgs/Header header

# 3D target / motion offset in robot-friendly coordinates, unit: mm
float32 x
float32 y
float32 z

# Detection target info
bool valid
bool is_small

# Motion decision
# Examples: far_move, no_ahead_check, check_and_spin, small_move, small_no_head, none
string motion_type

# Rotation correction
bool need_rotation_correction
float32 rotation_correction_deg

# Valve plane pose estimated from point cloud, in camera optical frame.
# yaw:   rotation about camera Y axis; positive means plane normal leans to +X.
# pitch: rotation about camera X axis; positive means plane normal leans upward.
bool plane_valid
float32 valve_yaw_deg
float32 valve_pitch_deg
float32 plane_normal_x
float32 plane_normal_y
float32 plane_normal_z
uint32 plane_inlier_count
float32 plane_inlier_ratio

# Optional debug info
float32 confidence
int32 class_id
