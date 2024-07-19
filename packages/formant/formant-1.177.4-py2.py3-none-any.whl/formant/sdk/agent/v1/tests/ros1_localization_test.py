import time
import rospy
from formant.sdk.agent.v1 import Client as FormantClient
from formant.sdk.agent.v1.localization.types import (
    PointCloud,
    Odometry,
    Map,
    Path,
    Goal,
    Transform,
)
from sensor_msgs.msg import PointCloud2 as ROSPointCloud2
from nav_msgs.msg import (
    Odometry as ROSOdometry,
    OccupancyGrid as ROSOccupancyGrid,
    Path as ROSPath,
)
from geometry_msgs.msg import PoseStamped as ROSPoseStamped

POINT_CLOUD_TOPIC = "/scan"
ODOM_TOPIC = "/odom"
MAP_TOPIC = "/map"
PATH_TOPIC = "/move_base/NavfnROS/plan"
GOAL_TOPIC = "/move_base/current_goal"
BASE_REFERENCE_FRAME = "map"


class ROSLocalizationTester:
    def __init__(self):
        self._fclient = FormantClient(
            ignore_throttled=True, ignore_unavailable=True, agent_url="localhost:5501"
        )
        self._localization_manager = self._fclient.get_localization_manager(
            "ros.localization"
        )
        self._subscribers = []
        SUBSCRIBER_MAPPING = [
            (POINT_CLOUD_TOPIC, ROSPointCloud2, self._pointcloud_callback),
            (ODOM_TOPIC, ROSOdometry, self._odometry_callback),
            (MAP_TOPIC, ROSOccupancyGrid, self._map_callback),
            (PATH_TOPIC, ROSPath, self._path_callback),
            (GOAL_TOPIC, ROSPoseStamped, self._goal_callback),
        ]
        for mapping in SUBSCRIBER_MAPPING:
            self._subscribers.append(
                rospy.Subscriber(mapping[0], mapping[1], mapping[2])
            )
        self._tf_buffer = None
        self._tf_listener = None
        self._setup_trasform_listener()

    def _setup_trasform_listener(self):
        try:
            from tf2_ros.buffer import Buffer
            from tf2_ros.transform_listener import TransformListener

            self._tf_buffer = Buffer()
            self._tf_listener = TransformListener(self._tf_buffer)
        except Exception as e:
            print("Error setting up tf2_ros transform listener: %s" % str(e))

    def _lookup_transform(self, msg):
        if self._tf_buffer is None or self._tf_listener is None:
            return Transform()
        try:
            transform = self._tf_buffer.lookup_transform(
                BASE_REFERENCE_FRAME,
                msg.header.frame_id,
                rospy.Time(0),
                rospy.Duration(0.2),
            )
            return Transform.from_ros_transform_stamped(transform)
        except Exception as e:
            print(
                "Error looking up transform between %s and %s: %s, using identity"
                % (BASE_REFERENCE_FRAME, msg.header.frame_id, str(e))
            )
        return Transform()

    def _pointcloud_callback(self, pointcloud):
        print("pointcloud")
        self._generic_callback(
            pointcloud, PointCloud, self._localization_manager.update_point_cloud
        )

    def _odometry_callback(self, odometry):
        self._generic_callback(
            odometry, Odometry, self._localization_manager.update_odometry
        )

    def _map_callback(self, map):
        self._generic_callback(map, Map, self._localization_manager.update_map)

    def _path_callback(self, path):
        print("path")
        self._generic_callback(path, Path, self._localization_manager.update_path)

    def _goal_callback(self, goal):
        print("goal")

        formant_goal = Goal(Transform.from_ros_pose_stamped(goal))
        formant_goal.transform_to_world = self._lookup_transform(goal)
        self._localization_manager.update_goal(formant_goal)

    def _generic_callback(self, obj, formant_type, update_function):
        formant_obj = formant_type.from_ros(obj)
        formant_obj.transform_to_world = self._lookup_transform(obj)
        update_function(formant_obj)


if __name__ == "__main__":
    rospy.init_node("formant_localization_tester")
    ROSLocalizationTester()
    while True:
        time.sleep(1)
