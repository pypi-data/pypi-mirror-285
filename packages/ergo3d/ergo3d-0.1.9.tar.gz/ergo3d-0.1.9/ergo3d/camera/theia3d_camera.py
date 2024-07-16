from .Camera import *

def batch_load_from_theia3d(xml_filename, camera_models=["Miqus Video"]):
    tree = ET.parse(xml_filename)
    root = tree.getroot()
    cameras = []
    for child in root:
        if child.tag == 'cameras':
            for grandchild in child:
                camera = Theia3d_Camera()
                camera.load_theia3d_xml(grandchild)
                if camera.DEVICE_MODEL in camera_models:
                    cameras.append(camera)
    return cameras


class Theia3d_Camera(Camera):
    """
    A class representing a camera in Theia3D format.
    https://www.theiamarkerless.ca/docs/dataformat.html
    """
    def __init__(self):
        super().__init__()

    def load_theia3d_xml(self, xml_element):
        # Read the xcp file as xml
        self.DEVICEID = xml_element.attrib['serial']
        self.DEVICE_MODEL = xml_element.attrib['model']
        self.VIEW_ROTATION = float(xml_element.attrib['viewrotation'])
        if xml_element.attrib['video_resolution'] == '540p':
            self.RESOLUTION = np.array([960, 544])
        elif xml_element.attrib['video_resolution'] == '1080p':
            self.RESOLUTION = np.array([1920, 1080])
        else:
            raise NotImplementedError
        self.RESOLUTION_U = self.RESOLUTION[0]
        self.RESOLUTION_V = self.RESOLUTION[1]

        transform = xml_element.find('transform')
        self.X = float(transform.attrib['x'])
        self.Y = float(transform.attrib['y'])
        self.Z = float(transform.attrib['z'])
        self.R11 = float(transform.attrib['r11'])
        self.R12 = float(transform.attrib['r12'])
        self.R13 = float(transform.attrib['r13'])
        self.R21 = float(transform.attrib['r21'])
        self.R22 = float(transform.attrib['r22'])
        self.R23 = float(transform.attrib['r23'])
        self.R31 = float(transform.attrib['r31'])
        self.R32 = float(transform.attrib['r32'])
        self.R33 = float(transform.attrib['r33'])
        self.rot3x3 = np.array([[self.R11, self.R12, self.R13],
                                [self.R21, self.R22, self.R23],
                                [self.R31, self.R32, self.R33]])
        # self.ORIENTATION = self.quaternion_from_rot3x3(self.rot3x3), # just use rot3x3 for now
        self.POSITION = np.array([self.X, self.Y, self.Z])

        # Extracting the 'intrinsic' attributes
        intrinsic = xml_element.find('intrinsic')
        # self.FOCAL_LENGTH = float(intrinsic.attrib['focallength'])  # not sure what this is, 9.223126, using sensor to px ratio instead
        self.SENSOR_MIN_U = float(intrinsic.attrib['sensorMinU'])
        self.SENSOR_MAX_U = float(intrinsic.attrib['sensorMaxU'])
        self.SENSOR_MIN_V = float(intrinsic.attrib['sensorMinV'])
        self.SENSOR_MAX_V = float(intrinsic.attrib['sensorMaxV'])
        self.FOCAL_LENGTH_U_SENSOR = float(intrinsic.attrib['focalLengthU'])
        self.FOCAL_LENGTH_V_SENSOR = float(intrinsic.attrib['focalLengthV'])
        self.CENTER_POINT_U_SENSOR = float(intrinsic.attrib['centerPointU'])
        self.CENTER_POINT_V_SENSOR = float(intrinsic.attrib['centerPointV'])
        self.SKEW = float(intrinsic.attrib['skew'])  # 0.0
        self.RADIAL_DISTORTION1 = float(intrinsic.attrib['radialDistortion1'])
        self.RADIAL_DISTORTION2 = float(intrinsic.attrib['radialDistortion2'])
        self.RADIAL_DISTORTION3 = float(intrinsic.attrib['radialDistortion3'])
        self.TANGENTAL_DISTORTION1 = float(intrinsic.attrib['tangentalDistortion1'])
        self.TANGENTAL_DISTORTION2 = float(intrinsic.attrib['tangentalDistortion2'])

        sensor_U = self.SENSOR_MAX_U - self.SENSOR_MIN_U
        sensor_V = self.SENSOR_MAX_V - self.SENSOR_MIN_V
        pp_U_ratio = self.CENTER_POINT_U_SENSOR / sensor_U
        pp_V_ratio = self.CENTER_POINT_V_SENSOR / sensor_V
        px_to_sensor_ratio_U = self.RESOLUTION_U / sensor_U
        px_to_sensor_ratio_V = self.RESOLUTION_V / sensor_V
        assert abs(pp_U_ratio - 0.5) < 0.1, f'pp_U_ratio: {pp_U_ratio}'
        assert abs(pp_V_ratio - 0.5) < 0.1, f'pp_V_ratio: {pp_V_ratio}'
        assert abs(px_to_sensor_ratio_U - px_to_sensor_ratio_V) < 0.01, f'px_to_sensor_ratio_U: {px_to_sensor_ratio_U}, px_to_sensor_ratio_V: {px_to_sensor_ratio_V}'
 
        self.PRINCIPAL_POINT = np.array([self.RESOLUTION_U*pp_U_ratio, self.RESOLUTION_V*pp_V_ratio])
        self.DISTORTION_CENTER = self.PRINCIPAL_POINT
        self.DISTORTION_SCALE = np.array([1.0, self.RADIAL_DISTORTION1, self.RADIAL_DISTORTION2, self.RADIAL_DISTORTION3])
        self.PIXEL_ASPECT_RATIO = self.FOCAL_LENGTH_V_SENSOR / self.FOCAL_LENGTH_U_SENSOR

        self.FOCAL_LENGTH_U = self.FOCAL_LENGTH_U_SENSOR * px_to_sensor_ratio_U
        self.FOCAL_LENGTH_V = self.FOCAL_LENGTH_V_SENSOR * px_to_sensor_ratio_V
        self.FOCAL_LENGTH = self.FOCAL_LENGTH_U  # the projection fuction will multiply U with skew factor for V

    def undistort(self, points_2d):  # todo: modify for theia3d
        raise NotImplementedError
        # undistort radial distortion, formula provided by Vicon
        points_2d = np.array(points_2d)
        dp = (points_2d - self.DISTORTION_CENTER) * (np.array([1, self.PIXEL_ASPECT_RATIO]))
        radius = np.linalg.norm(dp, axis=1)
        scale = np.vstack([np.ones_like(radius), radius ** 2, radius ** 4, radius ** 6]).T.dot(self.DISTORTION_SCALE).reshape(-1, 1)
        point_2d_corrected = (scale*dp + self.DISTORTION_CENTER)*(np.array([1, 1/self.PIXEL_ASPECT_RATIO]))  # assuming distortion center is the same as principal point
        return point_2d_corrected

    # def distort(self, points_2d):
    #     # approximate distort radial distortion, scale calculation should use distorted points, but here we use undistorted points
    #     points_2d = np.array(points_2d)
    #     dp = points_2d * (np.array([1, self.PIXEL_ASPECT_RATIO])) - self.DISTORTION_CENTER
    #     radius = np.linalg.norm(dp, axis=1)
    #     scale = np.vstack([np.ones_like(radius), radius ** 2, radius ** 4, radius ** 6]).T.dot(self.DISTORTION_SCALE).reshape(-1, 1)
    #     point_2d_distorted = dp/scale*(np.array([1, 1/self.PIXEL_ASPECT_RATIO])) + self.DISTORTION_CENTER # assuming distortion center is the same as principal point
    #     return point_2d_distorted

    def distort(self, points_2d):
        raise NotImplementedError
        # Convert points to numpy array
        points_2d = np.array(points_2d)

        # Extract X and Y coordinates
        x = points_2d[:, 0]
        y = points_2d[:, 1]

        # Normalize points by the principal point (assuming principal point is the distortion center)
        x = (x - self.DISTORTION_CENTER[0])
        y = (y - self.DISTORTION_CENTER[1])

        # Compute radius squared
        r_squared = x ** 2 + y ** 2

        # Radial distortion correction
        radial_distortion = (1 + self.RADIAL_DISTORTION1 * r_squared +
                             self.RADIAL_DISTORTION2 * r_squared ** 2 +
                             self.RADIAL_DISTORTION3 * r_squared ** 3)

        x_radial = x #* radial_distortion
        y_radial = y #* radial_distortion

        r_squared = x_radial ** 2 + y_radial ** 2
        # Tangential distortion correction
        x_tangential = 2 * self.TANGENTAL_DISTORTION1 * x_radial * y_radial + self.TANGENTAL_DISTORTION2 * (r_squared + 2 * x_radial ** 2)
        y_tangential = self.TANGENTAL_DISTORTION1 * (r_squared + 2 * y_radial ** 2) + 2 * self.TANGENTAL_DISTORTION2 * x_radial * y_radial

        # Apply corrections
        x_corrected = x_radial + x_tangential
        y_corrected = y_radial + y_tangential

        # Re-center the points back to original coordinates
        x_corrected += self.DISTORTION_CENTER[0]
        y_corrected += self.DISTORTION_CENTER[1]

        # Return the distorted points
        return np.column_stack((x_corrected, y_corrected))




if __name__ == '__main__':
    example_case = 1
    if example_case == 1:
        xml_filename = r'H:\Onform\render\Destrie Grieman - 1\Fastball RH Markerless 1.settings.xml'
        cameras = batch_load_from_theia3d(xml_filename)
        
