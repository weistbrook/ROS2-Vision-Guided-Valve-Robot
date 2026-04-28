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

# Optional debug info
float32 confidence
int32 class_id
