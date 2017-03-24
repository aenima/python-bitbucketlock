# -*- coding: utf8 -*-
"""
@file BitBucketLock main class

"""

import time

import requests

__all__ = ["BitBucketError", "BitBucketConnectionError",
           "BitBucketRestError", "BitBucketLock"]

DEFAULT_HEADERS = {'Content-Type': 'application/json',
                   'Accept': 'application/json'}

BITBUCKET_LOCK_PATH = "/mvc/maintenance/lock"
BITBUCKET_INIT_BACKUP_PATH = "/mvc/admin/backups?external=true"
BITBUCKET_POLL_STATUS_PATH = "/mvc/maintenance"
BITBUCKET_UPDATE_PROGRESS_PATH = "/mvc/admin/backups/progress/client"


class BitBucketError(Exception):
    """
    Base class for module exceptions
    """
    pass


class BitBucketConnectionError(BitBucketError):
    """
    Thrown on Connection errors
    """
    pass


class BitBucketRestError(BitBucketError):
    """
    Thrown on HTTPErrors
    """
    pass


class BitBucketLock(object):
    """
    Bitbucket Backup Lock Handler class
    """

    def __init__(self, server_address, username, password):
        self._server_address = server_address
        self._credentials = (username, password)
        self._session = requests.session()
        self._session.auth = (username, password)
        self._session.headers.update(DEFAULT_HEADERS)
        self._is_locked = False
        self._current_percentage = 0
        self._unlock_token = None
        self._cancel_token = None
        return

    def __enter_(self):
        self.acquire()
        return self

    def __exit__(self, *args, **kwargs):
        self.release()
        return False

    def acquire(self):
        """
        Initiate the Bitbucket Lock
        """
        self._initiate_lock()
        self._initiate_backup_process()
        self._wait_for_drain_and_latch()
        self._is_locked = True
        return

    def get_unlock_token(self):
        """
        Fetch the unlock token if it is already set

        """
        if not self._is_locked:
            raise BitBucketError("Server not locked")
        return self._unlock_token

    def get_cancel_token(self):
        """
        Fetch the backup cancel token if it is already set

        """
        if not self._is_locked:
            raise BitBucketError("Server not locked")
        return self._cancel_token

    def set_progress(self, percentage):
        """
        Set own backup progress. Visible by web users

        Note: 100% is disallowed because this will trigger a
              lock release. Use release() instead for this.
        """
        if not self._is_locked:
            raise BitBucketError("Server not locked")
        percentage = int(percentage)
        if percentage > 99 or percentage < 1:
            raise ValueError("percentage out of range")
        if percentage < self._current_percentage:
            raise ValueError("percentage lower than before")
        self._set_progress(percentage)
        return

    def release(self):
        """
        Release the krake... ehm, the lock
        """
        self._set_progress(100)
        self._release_lock()
        return

    def _initiate_lock(self):
        response_obj, response_data = self._post_request(
            BITBUCKET_LOCK_PATH)
        self._check_return_code(response_obj, "initiating lock")
        self._unlock_token = response_data['unlockToken']
        self._session.headers.update(
            {'X-Atlassian-Maintenance-Token': self._unlock_token})
        return

    def _initiate_backup_process(self):
        response_obj, response_data = self._post_request(
            BITBUCKET_INIT_BACKUP_PATH)
        self._check_return_code(response_obj, "initiating backup process")
        self._cancel_token = response_data['cancelToken']
        return

    def _wait_for_drain_and_latch(self):
        has_drained = False
        while not has_drained:
            time.sleep(0.5)
            _, response_data = self._get_request(BITBUCKET_POLL_STATUS_PATH)
            db_state = response_data['db-state']
            scm_state = response_data['scm-state']
            has_drained = db_state == "DRAINED" and scm_state == "DRAINED"
        return

    def _set_progress(self, percentage):
        response_obj, _ = self._post_request(BITBUCKET_UPDATE_PROGRESS_PATH, params={
            'token': self._unlock_token, 'percentage': percentage})
        self._check_return_code(response_obj, "setting progress")
        return

    def _release_lock(self):
        response_obj, _ = self._delete_request(
            BITBUCKET_LOCK_PATH, params={'token': self._unlock_token})
        self._check_return_code(
            response_obj, "releasing lock", expected_code=200)
        return

    def _check_return_code(self, response_obj, action, expected_code=202):
        if response_obj.status_code != expected_code:
            raise BitBucketRestError(
                "Unexpected return code {} when {}".format(response_obj.status_code, action))
        return

    def _get_request(self, relative_path, params=None):
        return self._make_request(self._session.get, relative_path, params=params)

    def _post_request(self, relative_path, json=None, params=None):
        return self._make_request(self._session.post, relative_path, data=json, params=params)

    def _delete_request(self, relative_path, json=None, params=None):
        return self._make_request(self._session.delete, relative_path, data=json, params=params)

    def _make_request(self, method, relative_path, **kwargs):
        try:
            response_obj = method(self._server_address +
                                  relative_path, verify=False, **kwargs)
            try:
                response_data = response_obj.json()
            except ValueError:
                response_data = response_obj.text
        except requests.HTTPError as err:
            raise BitBucketRestError(err)
        except requests.ConnectionError as err:
            raise BitBucketConnectionError(err)
        return response_obj, response_data
