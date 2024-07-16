import xml.etree.ElementTree as ET
import os
import numpy as np
import cv2
import pandas as pd
import json
import warnings


class Camera():
    def __int__(self):
        warnings.warn("All quaternions are in the form [x, y, z, w], double check your input")

    @staticmethod
    def string_to_float(string, delimiter=' ', suppress_warning=False):
        """
        Convert a string of floats separated by a delimiter to a list of floats.
        :param string: 
        :param delimiter: 
        :param suppress_warning: 
        :return: 
        """
        output = []
        for x in string.split(delimiter):
            try:
                output.append(float(x))
            except ValueError:
                if not suppress_warning:
                    print(f'Warning: \'{x}\' in string \'{string} \'is not a float.')
        if len(output) == 1:
            return output[0]
        else:
            return np.array(output)

    @staticmethod
    def rot3x3_from_quaternion(quaternion):
        x, y, z, w = quaternion
        rot_matrix = np.array([[1 - 2 * y ** 2 - 2 * z ** 2, 2 * x * y - 2 * z * w, 2 * x * z + 2 * y * w],
                               [2 * x * y + 2 * z * w, 1 - 2 * x ** 2 - 2 * z ** 2, 2 * y * z - 2 * x * w],
                               [2 * x * z - 2 * y * w, 2 * y * z + 2 * x * w, 1 - 2 * x ** 2 - 2 * y ** 2]])
        return rot_matrix

    @staticmethod
    def quaternion_from_rot3x3(rot3x3):  # todo: cover with test, wrong current, or imcommutable at least
        """
        Convert a 3x3 rotation matrix to a quaternion.

        :param rot3x3: A 3x3 rotation matrix.
        :return: A quaternion [w, x, y, z].  # tido: also not following the x, y, z, w convention in this package
        """
        raise NotImplementedError('Not working correctly, do not use')

        # Ensure the input is a numpy array for matrix operations.
        R = np.array(rot3x3)

        # Allocate space for the quaternion.
        q = np.zeros(4)

        # Compute the trace of the matrix.
        tr = np.trace(R)

        if tr > 0:
            S = np.sqrt(tr + 1.0) * 2  # S=4*qw 
            q[0] = 0.25 * S
            q[1] = (R[2, 1] - R[1, 2]) / S
            q[2] = (R[0, 2] - R[2, 0]) / S
            q[3] = (R[1, 0] - R[0, 1]) / S
        elif (R[0, 0] > R[1, 1]) and (R[0, 0] > R[2, 2]):
            S = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2  # S=4*qx
            q[0] = (R[2, 1] - R[1, 2]) / S
            q[1] = 0.25 * S
            q[2] = (R[0, 1] + R[1, 0]) / S
            q[3] = (R[0, 2] + R[2, 0]) / S
        elif R[1, 1] > R[2, 2]:
            S = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2  # S=4*qy
            q[0] = (R[0, 2] - R[2, 0]) / S
            q[1] = (R[0, 1] + R[1, 0]) / S
            q[2] = 0.25 * S
            q[3] = (R[1, 2] + R[2, 1]) / S
        else:
            S = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2  # S=4*qz
            q[0] = (R[1, 0] - R[0, 1]) / S
            q[1] = (R[0, 2] + R[2, 0]) / S
            q[2] = (R[1, 2] + R[2, 1]) / S
            q[3] = 0.25 * S

        return q



    @staticmethod
    def rot3x4_from_rot3x3_and_position(rot3x3, position):
        rot3x4 = np.hstack([rot3x3, -rot3x3.dot(position.reshape(-1, 1))])
        return rot3x4


    @staticmethod
    def quaternion_from_axis_angle(axis, angle=None):
        """
        Axis angle to quaternion, for SMPL mostly
        :param axis: (3,)
        :param angle: None or float
        :return:
        """
        axis_norm = np.linalg.norm(axis)
        angle = axis_norm if angle is None else angle
        axis = axis / axis_norm if axis_norm > 1e-8 else np.array([0, 0, 0])  # todo: sin(x/2)/x ~= 1/2 - (x**2)/48 for small angle x < 1e6
        w = np.cos(angle / 2.0)
        xyz = axis * np.sin(angle / 2.0)
        return np.array([xyz[0], xyz[1], xyz[2], w])

    @staticmethod
    def axis_angle_from_quaternion(quaternion, one_output=True):
        """
        Quaternion to axis angle, for SMPL mostly
        :param quaternion: (4,) x, y, z, w
        :param one_output: True: put angle as the norm of the axis vector
        :return:
        """
        x, y, z, w = quaternion
        angle = 2 * np.arccos(w)
        sin_theta_over_two = np.sqrt(1 - w * w)
        # To avoid division by zero, check if sin(theta/2) is close to zero
        axis = np.array([x, y, z]) / sin_theta_over_two if sin_theta_over_two > 1e-8 else np.array([1, 0, 0]) # If the angle is close to 0, direction does not matter  # todo: small angle approximation
        return axis * angle if one_output else [axis, angle]

    @staticmethod
    def quaternion_multiply(q1, q2):
        """
        Multiply two quaternions.

        Parameters:
        - q1: A tuple or list representing the first quaternion (x, y, z, w).
        - q2: A tuple or list representing the second quaternion (x, y, z, w).

        Returns:
        - A tuple representing the product of the two quaternions.
        """
        x1, y1, z1, w1 = q1
        x2, y2, z2, w2 = q2

        # Calculate the product
        w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2
        x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
        y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
        z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2

        return np.array([x, y, z, w])

    @staticmethod
    def rotate_axis_angle_by_axis_angle(axis_angle, axis_angle_delta):
        """
        Rotate an axis-angle vector by another axis-angle vector, for SMPL mostly
        :param axis_angle: the rotation vector, magnitude is the angle turned anticlockwise (RHR) in radians around the vector's direction
        :param axis_angle_delta:
        :return:
        """
        q1 = Camera.quaternion_from_axis_angle(axis_angle)
        q2 = Camera.quaternion_from_axis_angle(axis_angle_delta)
        q_out = Camera.quaternion_multiply(q2, q1)
        return Camera.axis_angle_from_quaternion(q_out, one_output=True)

    def get_camera_intrinsic_matrix(self):
        K = np.array([[self.FOCAL_LENGTH, self.SKEW, self.PRINCIPAL_POINT[0]],
                      [0, self.FOCAL_LENGTH / self.PIXEL_ASPECT_RATIO, self.PRINCIPAL_POINT[1]],
                      [0, 0, 1]])
        return K

    @staticmethod
    def projection_matrix_from_intrinsic_matrix_and_rot3x4(K, rot3x4):
        P = K.dot(rot3x4)
        return P

    def undistort(self, points_2d):
        raise NotImplementedError

    def distort(self, points_2d):
        raise NotImplementedError

    def get_projection_matrix(self):
        if not hasattr(self, 'rot3x3'):
            self.rot3x3 = self.rot3x3_from_quaternion(self.ORIENTATION)
        self.rot3x4 = self.rot3x4_from_rot3x3_and_position(self.rot3x3, self.POSITION)
        self.intrinsic_matrix = self.get_camera_intrinsic_matrix()
        self.projection_matrix = self.projection_matrix_from_intrinsic_matrix_and_rot3x4(self.intrinsic_matrix, self.rot3x4)
        return self.projection_matrix

    def get_camera_pitch(self):
        """
        For pitch correction, assume small roll
        Compare gravity vector in camera coordinate system with camera y axis
        only work for one frame, use def project_w_depth in the future when multiple frames are needed
        """
        world_z_point = np.array([0, 0, 1])
        world_origin = np.array([0, 0, 0])

        self.get_projection_matrix()
        camera_z_point = np.dot(self.rot3x4, np.hstack([world_z_point, 1]))
        camera_origin = np.dot(self.rot3x4, np.hstack([world_origin, 1]))

        camera_gravity_vector = camera_origin - camera_z_point  # +z-->origin
        camera_y_axis = np.array([0, 1, 0])
        pitch_correction_angle = np.arccos(np.dot(camera_gravity_vector, camera_y_axis) / (np.linalg.norm(camera_gravity_vector) * np.linalg.norm(camera_y_axis)))
        return pitch_correction_angle

    def project(self, points_3d):
        ''' extrinsic and intrinsic projection
        :param points_3d: 3d points in world coordinate
        :return: 2d points in camera coordinate, in pixel
        '''
        self.get_projection_matrix()
        points_3d = np.array(points_3d)
        points_2d = self.projection_matrix.dot(np.vstack([points_3d.T, np.ones([1, points_3d.shape[0]])]))
        points_2d = points_2d[0:2, :] / points_2d[2, :]
        points_2d = points_2d.T
        return points_2d

    def project_w_depth(self, points_3d):
        ''' world to camera coordinate system, extrinsic projection
        :param points_3d: 3d points in world coordinate
        :return: 3d points in camera coordinate, with depth, in mm/m
        '''
        self.get_projection_matrix()
        points_3d = np.array(points_3d)
        points_3d_cam = self.rot3x4.dot(np.vstack([points_3d.T, np.ones([1, points_3d.shape[0]])]))
        # translation_vector = self.POSITION.reshape([3, 1])
        # rotM = self.rot3x3
        # points_3d_cam = (rotM.dot(points_3d.T) + translation_vector).T
        return points_3d_cam.T

    def _weak_project(self, pose3d):
        """ From LCN, intrinsic projection
        """
        fx, fy = self.FOCAL_LENGTH, self.FOCAL_LENGTH / self.PIXEL_ASPECT_RATIO
        cx, cy = self.PRINCIPAL_POINT
        pose2d = pose3d[:, :2] / pose3d[:, 2:3]
        pose2d[:, 0] *= fx
        pose2d[:, 1] *= fy
        pose2d[:, 0] += cx
        pose2d[:, 1] += cy
        return pose2d

    def draw_2d(self, image, points_2d, color=(0, 0, 255)):
        for point_idx, point_2d in enumerate(points_2d):
            cv2.circle(image, (int(point_2d[0]), int(point_2d[1])), 3, color, -1)
            cv2.putText(image, str(point_idx), (int(point_2d[0]), int(point_2d[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return image
