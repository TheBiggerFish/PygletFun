from typing import Optional

import pyglet
from fishpy.geometry import Point2D


class Joint(Point2D):
    """Class which represents a vertex/joint of the leg"""

    def __init__(self, x: float, y: float, batch: pyglet.graphics.Batch, static: bool = False):
        super().__init__(x, y)
        self.static = static
        self.batch = batch
        self.graphic = pyglet.shapes.Circle(
            x, y, 5, batch=batch, color=(0, 0, 0))

    def __add__(self, offset: Point2D) -> 'Joint':
        return Joint(self.x+offset.x, self.y+offset.y, self.batch, self.static)

    def __mul__(self, scalar: float) -> 'Joint':
        return Joint(self.x*scalar, self.y*scalar, self.batch, self.static)

    def copy(self) -> 'Joint':
        return Joint(self.x, self.y, self.batch, self.static)

    def __repr__(self) -> str:
        return f'Joint({self.x},{self.y})'


class Leg:
    def __init__(self, joints: list[Joint], batch: pyglet.graphics.Batch):
        self.joints = joints
        self.batch = batch
        self.segment_lengths = [joint.euclidean_distance(
            joints[i+1]) for i, joint in enumerate(joints[:-1])]
        self._segments: Optional[list[pyglet.shapes.Line]] = None
        self._updated()

    @staticmethod
    def generate_leg(leg_length: float, num_joints: int, base_joint: Joint, batch: pyglet.graphics.Batch):
        joints = [base_joint]
        for i in range(1, num_joints):
            joint = base_joint + Point2D(0, -leg_length) * i
            joint.static = False
            joints.append(joint)
        return Leg(joints, batch)

    @property
    def base(self):
        return self.joints[0]

    @property
    def foot(self):
        return self.joints[-1]

    def _updated(self):
        self._segments = [pyglet.shapes.Line(joint.x, joint.y, self.joints[i+1].x, self.joints[i+1].y,
                                             width=2, color=(0, 0, 0), batch=self.batch)
                          for i, joint in enumerate(self.joints[:-1])]

    def execute_fabrik(self, target: Point2D, tolerance: float = 1) -> 'Leg':
        # http://www.andreasaristidou.com/publications/papers/FABRIK.pdf

        root_dist = self.base.euclidean_distance(target)

        if root_dist > sum(self.segment_lengths):
            # target unreachable
            for i, joint in enumerate(self.joints[: -1]):
                remaining_distance = joint.euclidean_distance(target)
                segment_weight = self.segment_lengths[i]/remaining_distance
                self.joints[i+1] = (joint*(1-segment_weight) +
                                    target*segment_weight)

        else:
            # target reachable
            actual_base = self.base.copy()
            target_dist = self.foot.euclidean_distance(target)
            max_iterations = 200 // len(self.joints)
            iterations = 0
            while target_dist > tolerance and iterations < max_iterations:
                # forward reaching
                self.joints[-1] = Joint(target.x, target.y, batch=self.batch)
                for i in range(len(self.joints)-2, 0, -1):
                    remaining_distance = self.joints[i +
                                                     1].euclidean_distance(self.joints[i])
                    segment_weight = self.segment_lengths[i]/remaining_distance
                    self.joints[i] = self.joints[i+1] * \
                        (1-segment_weight) + self.joints[i] * segment_weight

                # backward reaching
                self.joints[0] = actual_base
                for i in range(0, len(self.joints)-1):
                    remaining_distance = self.joints[i +
                                                     1].euclidean_distance(self.joints[i])
                    segment_weight = self.segment_lengths[i]/remaining_distance
                    self.joints[i+1] = self.joints[i] * \
                        (1-segment_weight) + self.joints[i+1] * segment_weight

                tolerance = self.foot.euclidean_distance(target)
                iterations += 1

        self._updated()
        return self
