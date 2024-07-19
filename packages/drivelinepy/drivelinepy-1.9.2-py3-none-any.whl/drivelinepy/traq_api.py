# ================================================================================
# Author: Garrett York
# Date: 2024/01/31
# Description: Class for TRAQ API
# ================================================================================

from .base_api_wrapper import BaseAPIWrapper


class TRAQAPI(BaseAPIWrapper):

    # 0 = Inactive, 1 = On-Site, 2 = Remote, 3 = Active, 4 = Archived
    VALID_STATUS_CODES = [0, 1, 2, 3, 4]

    # 0 = No Sub-Status, 217 = No Facility, 31 = AZ, 215 = WA
    VALID_SUBSTATUS_CODES = [0, 217, 31, 215]

    # ---------------------------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------------------------

    def __init__(self, client_id, client_secret, auth_url="https://traq.drivelinebaseball.com",
                 base_url="https://traq.drivelinebaseball.com/"):

        super().__init__(base_url)
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.authenticate()

    # ---------------------------------------------------------------------------
    # Method - Authenticate
    # ---------------------------------------------------------------------------

    def authenticate(self):
        """
        Authenticates with the TRAQ API and sets the access token.
        """
        self.logger.info("Entering TRAQ API authenticate()")
        path = "oauth/token"
        payload = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': '*'
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = self.post(path=path, data=payload, headers=headers, is_auth=True)
        response = response.json() if response is not None else None

        if response:
            self.access_token = response.get('access_token')
            self.logger.info("Authentication successful")
        else:
            self.logger.error("Authentication failed")

        self.logger.info("Exiting authenticate()")

    #---------------------------------------------------------------------------
    # Method - Get Users
    # ---------------------------------------------------------------------------

    def get_users(self, traq_id=None, email=None, status_code=None, substatus_code=None, facility_id=None):
        """
        Retrieves user information from the TRAQ API. Prioritizes TRAQ ID over email and status code.

        :param traq_id: TRAQ ID to filter users (optional).
        :param email: Email address to filter users (optional).
        :param status_code: Status code (int) to filter users (optional).
        :param facility_id: Facility ID to filter users (optional).
        :param substatus_code: Substatus code (int) to filter users (optional). 

        :return: User information or list of users.
        """
        self.logger.debug("Entering get_users()")

        endpoint = "api/v1.1/users"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {}

        # Check for facility filter
        if facility_id:
            if self.validate_facility_id(facility_id):
                params['facility_id'] = facility_id
            else:
                return None
        else:
            # if email and traq_id are not provided, warn the user that a facility ID filter is recommended
            if not traq_id and not email:
                self.logger.warning("Facility ID filter was not provided. It is highly recommended to provide a facility ID to avoid large data sets if not pinged by email or TRAQ ID.")

        # Check for unique identifyier filter
        if traq_id:
            if self.validate_traq_id(traq_id):
                params = {'id': traq_id}
            else:
                return None
        elif email:
            if self.validate_email(email):
                params = {'email': email}
            else:
                return None
        else:
            self.logger.warning("Neither TRAQ ID or Email provided")

        # Add status_code to params if provided
        if status_code:
            if self.validate_traq_user_status_code(status_code):
                params = {"active": status_code}
            else:
                return None
        else:
            self.logger.debug("Status code filter was not provided")
        
        # Add substatus_code to params if provided -- traq naming convention is a bit wonky here because "status" is actually the substatus_code
        if substatus_code:
            if self.validate_traq_user_substatus_code(substatus_code):
                params['status'] = substatus_code
            else:
                return None
        else:
            self.logger.debug("Substatus code filter was not provided")

        if not params:
            self.logger.debug("No valid filters provided.")
            return None

        response = self.get(endpoint, params=params, headers=headers)
        response = response.json() if response is not None else None

        self.logger.debug("Exiting get_users()")
        return response.get('data') if response else None

    #---------------------------------------------------------------------------
    # Method - Get Workouts
    #---------------------------------------------------------------------------

    def get_workouts(self, program):
        """
        Retrieves workouts information from the TRAQ API.

        :param program: Program ID to filter workouts (optional).
        :return: Workouts information or list of workouts.
        """
        self.logger.debug("Entering get_workouts()")

        endpoint = "api/v1.1/list-workouts"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        if self.validate_traq_program(program):
            params = {"program": program}
        else:
            return None  # Invalid program - logging done in validate_traq_program

        response = self.get(endpoint, params=params, headers=headers)
        response = response.json() if response is not None else None

        self.logger.debug("Exiting get_workouts()")
        return response.get('data') if response else None

    #---------------------------------------------------------------------------
    # Method - Get Workouts by Athlete
    #---------------------------------------------------------------------------

    def get_athlete_workouts(self, traq_id, start_date, end_date):
        """
        Retrieves workouts information from the TRAQ API.

        :param traq_id: TRAQ ID to filter users.
        :param start_date: Starting date range to filter workouts.
        :param end_date: Ending date range to filter workouts.
        :return: Workouts filtered by athlete and date information or list of workouts.
        """
        self.logger.debug("Entering get_athlete_workouts()")

        endpoint = "api/v1.1/athlete-workout"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {}
        if self.validate_traq_id(traq_id) and self.validate_date_yyyy_mm_dd(
                start_date) and self.validate_date_yyyy_mm_dd(end_date):
            params = {"start_date": start_date, "end_date": end_date, "user_id": traq_id}
        else:
            return None  # Invalid params - logging done in validation methods
        response = self.get(endpoint, params=params, headers=headers)
        response = response.json() if response is not None else None
        self.logger.debug("Exiting get_athlete_workouts()")

        return response.get('data') if response else None

    #---------------------------------------------------------------------------
    # Validation Methods
    #---------------------------------------------------------------------------

    def validate_facility_id(self, facility_id):
        """
        Validates that the facility id is an integer within the range of 1 to 999999.
        """
        if isinstance(facility_id, int):
            if 1 <= facility_id <= 999999:
                self.logger.info(f"Facility ID is valid: {facility_id}.")
                return True
            else:
                self.logger.error(f"Invalid Facility ID: {facility_id}. It must be a 1-6 digit integer within the range 1 to 999999.")
                return False
        else:
            self.logger.error(f"Invalid Facility ID: {facility_id}. It must be an integer.")
            return False

    def validate_traq_id(self, traq_id):
        """
        Validates that the TRAQ ID is an integer within the range of 1 to 999999.
        :param traq_id: The TRAQ ID to be validated.
        :return: Boolean indicating whether the ID is valid.
        """
        if isinstance(traq_id, int):
            if 1 <= traq_id <= 999999:
                self.logger.info(f"TRAQ ID is valid: {traq_id}.")
                return True
            else:
                self.logger.error(f"Invalid TRAQ ID: {traq_id}. It must be a 1-6 digit integer within the range 1 to 999999.")
                return False
        else:
            self.logger.error(f"Invalid TRAQ ID: {traq_id}. It must be an integer.")
            return False

    def validate_traq_program(self, program):
        """
        Validates that the TRAQ program is an int representing one of these possible options: -1, 0, 1, 2, 3, 4.

        :param program: The TRAQ program number to be validated.
        :return: Boolean indicating whether the program is valid.
        """
        if isinstance(program, int) and -1 <= program <= 4:
            self.logger.info(f"TRAQ program is valid: {program}. Exiting validate_traq_program()")
            return True
        else:
            self.logger.error(f"Invalid TRAQ program name int: {program}. Possible options: -1, 0, 1, 2, 3, 4.")
            return False

    def validate_traq_user_status_code(self, status_code):
        """
        :param status_code: The TRAQ status_code number to be validated.
        :return: Boolean indicating whether the program is valid.
        """
        if isinstance(status_code, int) and status_code in self.VALID_STATUS_CODES:
            self.logger.info(f"TRAQ status_code int is valid: {status_code}. Exiting validate_traq_user_status_code()")
            return True
        else:
            self.logger.error(f"Invalid TRAQ status_code int: {status_code}. Possible options: " + ", ".join(map(str, self.VALID_STATUS_CODES)) + ".")
            return False
        

    def validate_traq_user_substatus_code(self, substatus_code):
        """
        :param substatus_code: The TRAQ substatus_code number to be validated.
        :return: Boolean indicating whether the program is valid.
        """
        if isinstance(substatus_code, int) and substatus_code in self.VALID_SUBSTATUS_CODES:
            self.logger.info(f"TRAQ substatus_code int is valid: {substatus_code}. Exiting validate_traq_user_substatus_code()")
            return True
        else:
            self.logger.error(f"Invalid TRAQ substatus_code int: {substatus_code}. Possible options: " + ", ".join(map(str, self.VALID_SUBSTATUS_CODES)) + ".")
            return False
