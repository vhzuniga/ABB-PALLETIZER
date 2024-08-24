*Students*
-Paula Morales
-Walter Tamayo
-Victor Zuñiga

First clone the repository with git clone https://github.com/vhzuniga/ABB-PALLETIZER.git
Then enter the src folder and clone the following repositories
git clone https://github.com/fryumbla/Robotiq-grippers.git
git clone https://github.com/javierpagalo/Gazebo_utils.git
git clone https://github.com/roboticsgroup/roboticsgroup_upatras_gazebo_plugins.git
git clone https://github.com/pal-robotics/gazebo_ros_link_attacher.git

Then update and install noetic, python and moveit dependencies
sudo apt-get update
sudo apt install ros-noetic-industrial-core
sudo apt install ros-noetic-desktop-full
sudo apt-get install ros-noetic-moveit
sudo apt-get install ros-noetic-xacro
sudo apt-get upgrade ros-noetic-xacro
pip3 install pyyaml
pip3 install rospkg


After this create the workspace.
Inside the folder where the main repository was cloned. For example if it was in the documents folder.
cd ~/Documentos/catkin_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make
source devel/setup.bash

To be able to view the environment in rivz and gazebo, use the following command in a new terminal
roslaunch abb_irb4600_moveit demo_gazebo.launch

In a new terminal you must use the following code to be able to observe the palletizing robot
rosrun abb_irb4600_master pick_and_place.py

Feel free to add some textures and objects to the environment!
You can found someones on the following link
https://app.gazebosim.org/dashboard
You can add these models by looking for the route .gazebo/models
