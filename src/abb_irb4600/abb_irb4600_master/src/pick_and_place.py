#!/usr/bin/env python3

import sys
import copy
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
from std_msgs.msg import String
from gazebo_gripper import *
from geometry_msgs.msg import Quaternion
from tf.transformations import quaternion_from_euler

# Altura del lápiz
global z

global quit
quit = 0

# Altura del lápiz
global t
t = 0.01

def addBox(name, x, y, z, sx, sy, sz, scene):
    box_name = name
    
    # Create a message object of type PoseStamped to define box positions
    box_pose = geometry_msgs.msg.PoseStamped()
    box_pose.header.frame_id = "world"
    
    # Set the position message arguments
    box_pose.pose.position.x = x
    box_pose.pose.position.y = y 
    box_pose.pose.position.z = z 
    box_pose.pose.orientation.x = 0
    box_pose.pose.orientation.y = 0
    box_pose.pose.orientation.z = 0
    box_pose.pose.orientation.w = 1.0
    
    # Add the box in the scene
    scene.add_box(box_name, box_pose, size=(sx, sy, sz))

def home():
    joint_goal = arm_group.get_current_joint_values()
    joint_goal = [0, 0, 0, 0, 0, 0]

    arm_group.go(joint_goal, wait=True)
    rospy.loginfo("Abb is at home position.")
    return wpose

def move_cartesian_path(px, py, pz):
    q = quaternion_from_euler(3.14159, 0, 0)
    waypoints = []
    
    wpose = arm_group.get_current_pose().pose
    wpose.position.x = px
    wpose.position.y = py
    wpose.position.z = pz
    wpose.orientation.x, wpose.orientation.y, wpose.orientation.z, wpose.orientation.w = q
    waypoints.append(copy.deepcopy(wpose))
    (plan, fraction) = arm_group.compute_cartesian_path(waypoints, t, 0.0)  # jump_threshold

    display_trajectory = moveit_msgs.msg.DisplayTrajectory()
    display_trajectory.trajectory_start = robot.get_current_state()
    display_trajectory.trajectory.append(plan)

    # Publish
    display_trajectory_publisher.publish(display_trajectory)
    
    arm_group.execute(plan, wait=True)
    

def move_joints(j0, j1, j2, j3, j4, j5):
    # Set the target joint values
    arm_group.set_joint_value_target([j0, j1, j2, j3, j4, j5])
    
    # Plan the trajectory
    success, plan, _, _ = arm_group.plan()

    # Check if the plan is successful
    if success and len(plan.joint_trajectory.points) > 0:
        arm_group.execute(plan, wait=True)
    else:
        rospy.logwarn("Failed to generate a valid plan for the joint values provided.")

def loginfog(msg: str):
    rospy.loginfo("\033[92m%s\033[0m" % msg)

def grab_object(size):
    joint_goal = ee_group.get_current_joint_values()
    joint_goal = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    if size == "medium":
        joint_goal = [0.17, 0.0, 0.0, 0.0, 0.0, 0.0]
    if size == "small":
        joint_goal = [0.34, 0.0, 0.0, 0.0, 0.0, 0.0]

    ee_group.go(joint_goal, wait=True)

    touch_links = robot.get_link_names(group=ee_group.get_name())
    ee_group.attach_object("box", "gripper", touch_links)

    # Attach object using gazebo_gripper only if gazebo is enabled
    if use_gazebo:
        gazebo_gripper.attach_Object()

    rospy.loginfo("Abb picked the object")

def lose_object():
    joint_goal = ee_group.get_current_joint_values()
    joint_goal = [0.0, 0., 0, 0, 0, 0]
    ee_group.go(joint_goal, wait=True)

    # Detach object using gazebo_gripper only if gazebo is enabled
    if use_gazebo:
        gazebo_gripper.detach_Object()

    touch_links = robot.get_link_names(group=ee_group.get_name())
    ee_group.detach_object("gripper")
    rospy.loginfo("Abb dropped the object")

# Main execution
moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node('planning_node')

# Parse arguments to determine if gazebo is used
use_gazebo = rospy.get_param('~use_gazebo', False)

rate = rospy.Rate(10)
robot = moveit_commander.RobotCommander()
scene = moveit_commander.PlanningSceneInterface()
arm_group = moveit_commander.MoveGroupCommander("group_arm")
ee_group = moveit_commander.MoveGroupCommander("gripper")
display_trajectory_publisher = rospy.Publisher('/move_group/display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=20)
data_writing_publisher = rospy.Publisher('/figure_writing', String, queue_size=2)
data_writing_publisher.publish(("_none"))

# Grasping group for attach in rviz
grasping_group = "ee_group"

# ADD BOX rviz
addBox("box", 1, 0.5, 0.8, 0.2, 0.2, 0.15, scene)
wpose = arm_group.get_current_pose().pose
#rospy.logwarn(wpose)

# Initialize gazebo_gripper only if gazebo is used
#Se usa un parametro _use_gazebo para ver si esta prendido el gazebo
if use_gazebo:
    gazebo_gripper = RoboticGripper()
    gazebo_gripper._Robot_Name = "robot"
    gazebo_gripper._EE_Link_Name = "link_6"
    gazebo_gripper._Box_Model_Name = "box"
    gazebo_gripper._Box_Link_Name = "link"

puntos = [
    [0.4, 1.15, 0.4],    
    [0.8, 1.15, 0.4],
    [0.4, 1.45, 0.4],
    [0.8, 1.45, 0.4],
    [0.4, 1.75, 0.4],
    [0.8, 1.75, 0.4],
    [0.4, 1.75, 0.4],       
    [0.8, 2.05, 0.4],
    [0.4, 2.05, 0.4]
    ]

i=1
for punto in puntos:
    

    print("caja #",i)
    #BAnda transportadora
    move_cartesian_path(2.3,0.0,0.8)
    wpose = arm_group.get_current_pose().pose
    grab_object("small")
    rospy.sleep(0.1)

    #Lugar seguro
    
    move_cartesian_path(wpose.position.x, wpose.position.y, 1)
    wpose = arm_group.get_current_pose().pose
    #rospy.logwarn(wpose)
    rospy.sleep(0.1)
    rospy.loginfo("Posicion segura")

        #Lugar seguro
    
    move_cartesian_path(punto[0],punto[1], wpose.position.z)
    wpose = arm_group.get_current_pose().pose
    #rospy.logwarn(wpose)
    rospy.sleep(0.1)
    rospy.loginfo("Posicion segura")

    #Place
    move_cartesian_path(punto[0],punto[1], punto[2])
    wpose = arm_group.get_current_pose().pose
    #rospy.logwarn(wpose)
    lose_object()
    rospy.sleep(0.1)

    #Lugar seguro
    move_cartesian_path(wpose.position.x, wpose.position.y, 1)
    wpose = arm_group.get_current_pose().pose
    #rospy.logwarn(wpose)
    rospy.sleep(0.1)
    rospy.loginfo("Posicion segura")

    i+=1






#wpose.orientation = arm_group.get_current_pose().pose.orientation.x



#rospy.logwarn(arm_group.get_current_joint_values())


#move_joints(-1.5699811638948276, 0.35076022743452813, -0.17050017674796938, 0, 0.014684045245539014, 0)

rospy.sleep(0.1)





move_joints(0, 0, 0, 0, 0, 0)

while not rospy.is_shutdown() and quit == 0:
    rospy.sleep(1)

#BOXES TOTAL
n=1

