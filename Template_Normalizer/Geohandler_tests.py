import math as m

EARTH_RADIUS = 6371*1000  # km
DEG_TO_RAD = (22.0 / 7) / 180.0

def __degrees_to_radians(value):
    return_value = value *DEG_TO_RAD
    return return_value


def __radians_to_degrees(value):
    return_value = value /DEG_TO_RAD
    return return_value

def __calculate_dictance( geo1, geo2):
    """This function will return the kilometer value of the distance between (lat1, lon1), (lat2, lon2)."""
    return_distance = None
    if (geo1 is not None) and (geo2 is not None):
        lat1, lon1 = geo1
        lat2, lon2 = geo2
        theta = lon1 - lon2
        lat1_rad = m.radians(lat1)
        lat2_rad = m.radians(lat2)
        theta_rad= m.radians(theta)
        dist = m.sin(lat1_rad) * m.sin(lat2_rad) + m.cos(lat1_rad) * m.cos(lat2_rad) * m.cos(theta_rad)
        dist = m.acos(dist)
        dist = m.degrees(dist)
        dist = dist * 60 * 1.1515
        return_distance=dist
    return return_distance

def calculate_dist(geo1, geo2):
    return_distance = None
    if (geo1 is not None) and (geo2 is not None):
        lat1, lon1 = geo1
        lat2, lon2 = geo2
        lat1_rad = m.radians(lat1)
        lon1_rad = m.radians(lon1)
        lat2_rad = m.radians(lat2)
        lon2_rad = m.radians(lon2)

        delta_theta = lat2_rad - lat1_rad
        delta_lambda = lon2_rad - lon1_rad
        a = m.sin(delta_theta/2)*m.sin(delta_theta/2)+m.cos(lat1_rad)*m.cos(lat2_rad)*m.sin(delta_lambda/2)*m.sin(delta_lambda/2)

        c = 2*m.atan2(m.sqrt(a), m.sqrt(1-a))
        dist = EARTH_RADIUS*c
        return_distance=dist
    return return_distance

def calculate_dist_seocnd(geo1, geo2):
    return_distance = None
    if (geo1 is not None) and (geo2 is not None):
        lat1, lon1 = geo1
        lat2, lon2 = geo2
        lat1_rad=m.radians(lat1)
        lat2_rad=m.radians(lat2)

        delta_theta=lat2-lat1
        delta_theta_rad=m.radians(delta_theta)
        delta_lambda=lon2-lon1
        delta_lambda_rad=m.radians(delta_lambda)

        a = m.sin(delta_theta_rad/2)*m.sin(delta_theta_rad/2)+m.cos(lat1_rad)*m.cos(lat2_rad)*m.sin(delta_lambda_rad/2)*m.sin(delta_lambda_rad/2)

        c = 2*m.atan2(m.sqrt(a), m.sqrt(1-a))
        dist = EARTH_RADIUS*c
        return_distance=dist
    return return_distance

def main():
    t1=__calculate_dictance((74.7602, -129.298), (74.7586, -129.281))
    t2=calculate_dist((74.7602, -129.298), (74.7586, -129.281))
    t3=calculate_dist_seocnd((74.7602, -129.298), (74.7586, -129.281))
    tst=t2/1000
    tst2=t3/1000
    print("End of Processing")
    return

main()