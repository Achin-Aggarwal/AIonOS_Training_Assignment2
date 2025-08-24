# # db_connector.py
# import os
# import mysql.connector
# from dotenv import load_dotenv
# from typing import Dict, List, Optional

# load_dotenv()

# DB_CONFIG = {
#     "host": os.getenv("DB_HOST"),
#     "port": int(os.getenv("DB_PORT", 3306)),
#     "user": os.getenv("DB_USER"),
#     "password": os.getenv("DB_PASSWORD"),
#     "database": os.getenv("DB_NAME"),
# }


# def get_connection():
#     """Get database connection with error handling"""
#     try:
#         return mysql.connector.connect(**DB_CONFIG)
#     except mysql.connector.Error as e:
#         print(f"Database connection error: {e}")
#         raise


# def fetch_all_software() -> Dict[str, List[str]]:
#     """
#     Returns all software grouped by name -> [versions].
#     Example: { "zoom": ["5.16.2", "5.15.9"], "slack": ["4.30.0"] }
#     """
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
        
#         # Order by version descending to get latest versions first
#         cursor.execute("""
#             SELECT name, version 
#             FROM software 
#             ORDER BY name, version DESC
#         """)
        
#         rows = cursor.fetchall()
#         cursor.close()
#         conn.close()

#         catalog = {}
#         for name, version in rows:
#             catalog.setdefault(name.lower(), []).append(version)
        
#         return catalog
    
#     except Exception as e:
#         print(f"Error fetching all software: {e}")
#         return {}


# def fetch_software_by_names(app_names: List[str]) -> Dict[str, List[str]]:
#     """
#     Fetch only software in app_names list.
#     Returns software with their available versions.
#     """
#     if not app_names:
#         return {}

#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         # Use LIKE for partial matching (e.g., "visual studio" matches "Visual Studio Code")
#         placeholders = " OR ".join(["LOWER(name) LIKE %s"] * len(app_names))
#         query = f"""
#             SELECT name, version 
#             FROM software 
#             WHERE {placeholders}
#             ORDER BY name, version DESC
#         """
        
#         # Prepare parameters for LIKE matching
#         like_params = [f"%{name.lower()}%" for name in app_names]
        
#         cursor.execute(query, like_params)
#         rows = cursor.fetchall()

#         cursor.close()
#         conn.close()

#         catalog = {}
#         for name, version in rows:
#             catalog.setdefault(name.lower(), []).append(version)
        
#         return catalog
    
#     except Exception as e:
#         print(f"Error fetching software by names: {e}")
#         return {}


# def search_software_fuzzy(search_term: str) -> Dict[str, List[str]]:
#     """
#     Fuzzy search for software names containing the search term.
#     """
#     if not search_term:
#         return {}
    
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
        
#         query = """
#             SELECT name, version 
#             FROM software 
#             WHERE LOWER(name) LIKE %s
#             ORDER BY name, version DESC
#         """
        
#         cursor.execute(query, [f"%{search_term.lower()}%"])
#         rows = cursor.fetchall()
        
#         cursor.close()
#         conn.close()
        
#         catalog = {}
#         for name, version in rows:
#             catalog.setdefault(name.lower(), []).append(version)
        
#         return catalog
    
#     except Exception as e:
#         print(f"Error in fuzzy search: {e}")
#         return {}


# def get_software_info(app_name: str, version: Optional[str] = None) -> Optional[Dict]:
#     """
#     Get information about a specific software and version.
#     Since we only have name and version columns, we'll return basic info.
#     """
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
        
#         if version:
#             query = """
#                 SELECT name, version 
#                 FROM software 
#                 WHERE LOWER(name) = %s AND version = %s
#             """
#             cursor.execute(query, [app_name.lower(), version])
#         else:
#             query = """
#                 SELECT name, version 
#                 FROM software 
#                 WHERE LOWER(name) = %s 
#                 ORDER BY version DESC 
#                 LIMIT 1
#             """
#             cursor.execute(query, [app_name.lower()])
        
#         row = cursor.fetchone()
#         cursor.close()
#         conn.close()
        
#         if row:
#             return {
#                 "name": row[0],
#                 "version": row[1],
#                 "description": f"{row[0]} version {row[1]} - Ready for installation",
#                 "size": "Size information not available",
#                 "download_url": None
#             }
        
#         return None
        
#     except Exception as e:
#         print(f"Error getting software info: {e}")
#         return None


# def get_popular_software(limit: int = 10) -> Dict[str, List[str]]:
#     """
#     Get software from the database, limited by count.
#     Returns software alphabetically since we don't have popularity tracking.
#     """
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
        
#         # Get unique software names first, then get all versions for each
#         query = """
#             SELECT name, version 
#             FROM software 
#             WHERE name IN (
#                 SELECT DISTINCT name 
#                 FROM software 
#                 ORDER BY name 
#                 LIMIT %s
#             )
#             ORDER BY name, version DESC
#         """
        
#         cursor.execute(query, [limit])
#         rows = cursor.fetchall()
#         cursor.close()
#         conn.close()
        
#         catalog = {}
#         for name, version in rows:
#             catalog.setdefault(name.lower(), []).append(version)
        
#         return catalog
        
#     except Exception as e:
#         print(f"Error getting popular software: {e}")
#         return {}


# db_connector.py
import os
import mysql.connector
from dotenv import load_dotenv
from typing import Dict, List, Optional
 
load_dotenv()
 
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}
 
 
def get_connection():
    """Get database connection with error handling"""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        raise
 
 
def fetch_all_software() -> Dict[str, List[str]]:
    """
    Returns all software grouped by name -> [versions].
    Example: { "zoom": ["5.16.2", "5.15.9"], "slack": ["4.30.0"] }
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
       
        # Order by version descending to get latest versions first
        cursor.execute("""
            SELECT name, version
            FROM software
            ORDER BY name, version DESC
        """)
       
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
 
        catalog = {}
        for name, version in rows:
            catalog.setdefault(name.lower(), []).append(version)
       
        return catalog
   
    except Exception as e:
        print(f"Error fetching all software: {e}")
        return {}
 
 
def fetch_software_by_names(app_names: List[str]) -> Dict[str, List[str]]:
    """
    Fetch only software in app_names list.
    Returns software with their available versions.
    """
    if not app_names:
        return {}
 
    try:
        conn = get_connection()
        cursor = conn.cursor()
 
        # Use LIKE for partial matching (e.g., "visual studio" matches "Visual Studio Code")
        placeholders = " OR ".join(["LOWER(name) LIKE %s"] * len(app_names))
        query = f"""
            SELECT name, version
            FROM software
            WHERE {placeholders}
            ORDER BY name, version DESC
        """
       
        # Prepare parameters for LIKE matching
        like_params = [f"%{name.lower()}%" for name in app_names]
       
        cursor.execute(query, like_params)
        rows = cursor.fetchall()
 
        cursor.close()
        conn.close()
 
        catalog = {}
        for name, version in rows:
            catalog.setdefault(name.lower(), []).append(version)
       
        return catalog
   
    except Exception as e:
        print(f"Error fetching software by names: {e}")
        return {}
 
 
def search_software_fuzzy(search_term: str) -> Dict[str, List[str]]:
    """
    Fuzzy search for software names containing the search term.
    """
    if not search_term:
        return {}
   
    try:
        conn = get_connection()
        cursor = conn.cursor()
       
        query = """
            SELECT name, version
            FROM software
            WHERE LOWER(name) LIKE %s
            ORDER BY name, version DESC
        """
       
        cursor.execute(query, [f"%{search_term.lower()}%"])
        rows = cursor.fetchall()
       
        cursor.close()
        conn.close()
       
        catalog = {}
        for name, version in rows:
            catalog.setdefault(name.lower(), []).append(version)
       
        return catalog
   
    except Exception as e:
        print(f"Error in fuzzy search: {e}")
        return {}
 
 
def get_software_info(app_name: str, version: Optional[str] = None) -> Optional[Dict]:
    """
    Get information about a specific software and version.
    Since we only have name and version columns, we'll return basic info.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
       
        if version:
            query = """
                SELECT name, version
                FROM software
                WHERE LOWER(name) = %s AND version = %s
            """
            cursor.execute(query, [app_name.lower(), version])
        else:
            query = """
                SELECT name, version
                FROM software
                WHERE LOWER(name) = %s
                ORDER BY version DESC
                LIMIT 1
            """
            cursor.execute(query, [app_name.lower()])
       
        row = cursor.fetchone()
        cursor.close()
        conn.close()
       
        if row:
            return {
                "name": row[0],
                "version": row[1],
                "description": f"{row[0]} version {row[1]} - Ready for installation",
                "size": "Size information not available",
                "download_url": None
            }
       
        return None
       
    except Exception as e:
        print(f"Error getting software info: {e}")
        return None
 
 
def get_popular_software(limit: int = 10) -> Dict[str, List[str]]:
    """
    Get software from the database, limited by count.
    Returns software alphabetically since we don't have popularity tracking.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
       
        # Get unique software names first, then get all versions for each
        query = """
            SELECT name, version
            FROM software
            WHERE name IN (
                SELECT DISTINCT name
                FROM software
                ORDER BY name
                LIMIT %s
            )
            ORDER BY name, version DESC
        """
       
        cursor.execute(query, [limit])
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
       
        catalog = {}
        for name, version in rows:
            catalog.setdefault(name.lower(), []).append(version)
       
        return catalog
       
    except Exception as e:
        print(f"Error getting popular software: {e}")
        return {}
 
 
# def log_software_request(incident_number: str, app_name: str) -> bool:
#     """
#     Log software installation request to request_logging table.
   
#     Args:
#         incident_number: ServiceNow incident number (e.g., INC0010001)
#         app_name: Name of the software being requested
       
#     Returns:
#         bool: True if logging successful, False otherwise
#     """
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
       
#         # Create status message as requested
#         status = f"user initiated install request for {app_name}"
       
#         # Insert log entry into request_logging table
#         # incident_id stores the actual ServiceNow incident number
#         query = """
#             INSERT INTO request_logging (incident_id, status)
#             VALUES (%s, %s)
#         """
       
#         cursor.execute(query, [incident_number, status])
#         conn.commit()
       
#         cursor.close()
#         conn.close()
       
#         print(f"📝 Request logged successfully: Incident {incident_number} for {app_name}")
#         return True
       
#     except Exception as e:
#         print(f"❌ Error logging software request: {e}")
#         return False


# def log_software_request(
#     incident_number: str,
#     software_name: str,
#     version_name: str,
#     status: str,
#     timestamp: str
# ) -> bool:
#     """
#     Log software installation request to request_logging table.

#     Args:
#         incident_number: ServiceNow incident number (e.g., INC0010001)
#         software_name: Name of the software being requested
#         version_name: Version of the software
#         status: Status of the request (e.g., Created, Completed, Failed)
#         timestamp: When the request was made

#     Returns:
#         bool: True if logging successful, False otherwise
#     """
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()

#         # Insert log entry into request_logging table
#         query = """
#             INSERT INTO request_logging (incident_id, software_name, version_name, status, timestamp)
#             VALUES (%s, %s, %s, %s, %s)
#         """

#         cursor.execute(query, [
#             incident_number,
#             software_name,
#             version_name,
#             status,
#             timestamp
#         ])
#         conn.commit()

#         cursor.close()
#         conn.close()

#         print(f"📝 Request logged: {incident_number}, {software_name}, {version_name}, {status}, {timestamp}")
#         return True

#     except Exception as e:
#         print(f"❌ Error logging software request: {e}")
#         return False



def log_software_request(
    incident_number: str,
    software_name: str,
    version_name: str,
    status: str
) -> bool:
    """
    Log software installation request to request_logging table.

    Args:
        incident_number: ServiceNow incident number (e.g., INC0010001)
        software_name: Name of the software being requested
        version_name: Version of the software
        status: Status of the request (e.g., Created, Completed, Failed)
    Returns:
        bool: True if logging successful, False otherwise
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Insert log entry without timestamp (auto-handled by DB)
        query = """
            INSERT INTO request_logging (incident_id, software_name, version_name, status)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, [
            incident_number,
            software_name,
            version_name,
            status
        ])
        conn.commit()

        cursor.close()
        conn.close()

        print(f"📝 Request logged: {incident_number}, {software_name}, {version_name}, {status}")
        return True

    except Exception as e:
        print(f"❌ Error logging software request: {e}")
        return False
