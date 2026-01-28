import math
from datetime import timedelta


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    if not all([lat1, lon1, lat2, lon2]):
        return None
    
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in meters
    radius = 6371000
    
    distance = c * radius
    return round(distance, 2)


def is_within_distance(distance_meters, allowed_distance_meters=500):
    """
    Check if the distance is within allowed distance
    Returns True if within distance, False otherwise
    """
    if distance_meters is None:
        return False
    return distance_meters <= allowed_distance_meters


def format_distance(distance_meters):
    """Format distance for display"""
    if distance_meters is None:
        return "N/A"
    if distance_meters < 1000:
        return f"{distance_meters:.0f}m"
    else:
        return f"{distance_meters / 1000:.2f}km"


def calculate_working_hours(check_in_time, check_out_time):
    """Calculate working hours between two times"""
    if not check_in_time or not check_out_time:
        return None
    
    delta = check_out_time - check_in_time
    hours = delta.total_seconds() / 3600
    return round(hours, 2)


def determine_attendance_status(check_in_time, expected_time, late_threshold_minutes=15):
    """
    Determine attendance status based on check-in time
    Returns 'present', 'late', or 'absent'
    """
    if not check_in_time:
        return 'absent'
    
    if expected_time:
        delay = (check_in_time - expected_time).total_seconds() / 60
        if delay > late_threshold_minutes:
            return 'late'
    
    return 'present'
