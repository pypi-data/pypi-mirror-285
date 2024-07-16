#!/usr/bin/python

# Obtained from: https://swe.ssa.esa.int/documents/20182/165822/get_hapi_session_cookies.py
"""
(C) Copyright European Space Agency, 2022

Owner:             European Space Agency
Version:           1.3
Date of creation:  08/10/2021

Change log:
Version  |  Date        |  Reason for change
1.0      |  04/03/2021  |  Initial version
1.1      |  08/10/2021  |  Change of cookie name
1.2      |  28/03/2022  |  Improve consent handling as the consent is now stored in OpenAM
1.3      |  20/10/2022  |  Adjust to correct HAPI capabilities response

Purpose:
This Python script/module establishes a session with HAPI at a given URL and outputs the session
cookies that can be used for subsequent calls to HAPI. It provides three functions that can be
used in other Python-based programs to access HAPI and retrieve, for instance, data:
- get_auth_cookie(username, password)
        This only authenticates the user at the SSA SSO server and return the auth cookie.
- get_session_cookies(auth cookie)
        Establishes a session with HAPI using an auth cookie and return the session cookies.
- establish_hapi_session(username, password)
        Directly establishes a session with HAPI and returns the session cookies. Internally,
        an auth cookie is obtained first and then a session with HAPI is established.
- get_hapi_capabilities(jsession_id, xsrf_token)
        A test function that requests the HAPI/capabilities. It also serves as an HAPI example.

The main method can be executed to test the entire script.

Prerequisites:
Python 3 and Python libraries requests and json installed on the system

Usage:
Execute the script with Python 3 to test its functionality. Make sure to adjust the username
and password mentioned in the main function.
Use the methods described above within another script or program to establish a session with
HAPI and to use the obtained session cookies for subsequent calls to HAPI (e.g. to request data).
More details can be found in the document SSA-SWE-HAPI-TN-0001 which can be found in the SWE
Portal / Technical library.
"""


import requests
import json


# flag to control the outputs to std out in case of errors
PRINT_ERRORS=True
# Global variables to control authentication and authorisation for the respective environments
PORTAL_URL="https://swe.ssa.esa.int/"
AUTHENTICATE_URL="https://sso.ssa.esa.int/am/json/authenticate"
SSO_COOKIENAME="iPlanetDirectoryPro"


def get_auth_cookie(username, password):
    """
    Authenticates a user against OpenAM. This uses the globally defined AUTHENTICATE_URL.
    It returns whether authentication was successful and if so, the obtained auth cookie.
    If an error occurs, the exception is caught and the error printed to std out.

    :param str username: The username to use for authentication.
    :param str password: The password for the provided username.

    :returns bool: True, if authentication was successful
    :returns str: The obtained authentication cookie
    """
    try:
        # send a POST request to the authenticatoin url along username and password
        response = requests.post(AUTHENTICATE_URL,
                headers = {
                    'Content-Type': 'application/json',
                    'X-OpenAM-Username': username,
                    'X-OpenAM-Password': password,
                },
                data = '{}')
        # form the response, extract the auth cookie and return it
        token_dict = json.loads(response.content)
        auth_cookie = token_dict['tokenId']
        return True, auth_cookie
    except Exception as exc:
        if PRINT_ERRORS:
            print(exc)
        return False, ''


def get_session_cookies(auth_cookie):
    """
    Establishes a session with HAPI using the provided authentication cookie. It returns
    whether a session was established successfully and if so, the obtained session cookies.
    If an error occurs, the exception is caught and the error printed to std out.

    :param str auth_cookie: A valid authentication cookie.

    :returns bool: True, if a session was established
    :returns str: The obtained session cookie JSESSIONID
    :returns str: The obtained session cookie XSRF-TOKEN
    """
    try:
        # try to access the HAPI/capabilities using the auth_cookie
        init_response = requests.get(PORTAL_URL + "/hapi/capabilities",
                cookies = {
                    SSO_COOKIENAME: auth_cookie,
                })
        # extract the session cookies from the very first response from HAPI
        cookie_jar = init_response.history[0].cookies
        jsession_id = cookie_jar.get('JSESSIONID')
        xsrf_token = cookie_jar.get('XSRF-TOKEN')
        # extract the consent url we are being requested to send our consent to
        # (in case we didn't consent yet)
        consent_url = init_response.url
        content = init_response.content

        # if we consented already, we should have received the HAPI Capabilities already.
        if not "/hapi/capabilities" in consent_url:
            # if not, we need to give our consent in the next step.
            # send the consent along with all cookies to the consent url
            consent_response = requests.post(consent_url,
                    cookies = {
                        SSO_COOKIENAME: auth_cookie,
                        'JSESSIONID': jsession_id,
                        'XSRF_TOKEN': xsrf_token,
                    },
                    data = {
                        'decision': 'Allow',
                        'save_consent': 'on',
                    })
            content = consent_response.content
        # this will result in a redirect to the initial HAPI/capabilities
        capabilities = json.loads(content)
        # the json output is supposed to look something like this:
        #   {"HAPI":"2.1.0","status":{"code":1200,"message":"OK"},"outputFormats":["csv","json"]}
        hapi_version = capabilities['HAPI']
        status = capabilities['status']
        # if the output is what we expect, return True and the session cookies
        if hapi_version != '' and status != {} and status['message'] == 'OK':
            return True, jsession_id, xsrf_token
    except Exception as exc:
        if PRINT_ERRORS:
            print(exc)
    return False, '', ''


def establish_hapi_session(username, password):
    """
    Establishes a session with HAPI using the provided username and password. It returns
    whether a session was established successfully and if so, the obtained session cookies.
    If an error occurs, the exception is caught and the error printed to std out.

    :param str username: The username to use for authentication.
    :param str password: The password for the provided username.

    :returns bool: True, if a session was established
    :returns str: The obtained session cookie JSESSIONID
    :returns str: The obtained session cookie XSRF-TOKEN
    """
    authenticated, auth_cookie = get_auth_cookie(username, password)
    if authenticated:
        return get_session_cookies(auth_cookie)
    return False, '', ''


def get_hapi_capabilities(jsession_id, xsrf_token):
    """
    Uses the provided session cookies to request the HAPI/capabilities and returns them.
    If an error occurs, the exception is caught and the error printed to std out.

    :param str jsession_id: A valid JSESSIONID session cookie.
    :param str xsrf_token: A valid XSRF-TOKEN session cookie.

    :returns bool: True, if the request to HAPI/capabilities was successful
    :returns dict: The obtained HAPI/capabilities
    """
    try:
        # send a GET request to the HAPI/capabilities endpoint along with valid session cookies
        test_response = requests.get(PORTAL_URL + "/hapi/capabilities",
                cookies = {
                    'JSESSIONID': jsession_id,
                    'XSRF_TOKEN': xsrf_token,
                })
        # extract the capabilities from the response
        capabilities = json.loads(test_response.content)
        hapi_version = capabilities['HAPI']
        status = capabilities['status']
        # if the capabilities are as expected, return True along with the capabilities dict
        if hapi_version != '' and status != {} and status['message'] == 'OK':
            return True, capabilities
    except Exception as exc:
        if PRINT_ERRORS:
            print(exc)
    return False, {}


def main():
    username = '<USERNAME>'
    password = '<PASSWORD>'
    authenticated, auth_cookie = get_auth_cookie(username, password)
    if authenticated:
        print('Authentication successful. Obtained authentication cookies:')
        print('  ' + SSO_COOKIENAME + ': ' + auth_cookie)
        session_established, jsession_id, xsrf_token = get_session_cookies(auth_cookie)
        if session_established:
            print('Session successfully established. Obtained session cookies:')
            print('  JSESSIONID: ' + jsession_id)
            print('  XSRF-TOKEN: ' + xsrf_token)
            print('Testing session cookies on hapi/capabilities:')
            capabilities = get_hapi_capabilities(jsession_id, xsrf_token)
            print(capabilities)

if __name__ == "__main__":
    main()
