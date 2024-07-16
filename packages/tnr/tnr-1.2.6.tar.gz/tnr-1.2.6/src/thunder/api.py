import requests
import click
import sys

FIREBASE_API_KEY = "AIzaSyDcJB_1Or2TbRxTXajQCr-MTipwwQSiY38"

def refresh_id_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    try:
        response = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}",
            data=data,
            timeout=5,
        )

        # Attempt to decode the response to JSON before calling raise_for_status
        # to ensure we can inspect the error response body if needed.
        response_json = response.json()

        # If the response status indicates success, check for the id_token.
        if response.ok and response_json.get("id_token"):
            return (
                response_json["id_token"],
                response_json["refresh_token"],
                response_json["user_id"],
            )

        # If the response is not OK, but we've successfully parsed the JSON,
        # we can now check for known error conditions without raising an exception.
        error_message = response_json.get("error", {}).get("message")
        known_errors = [
            "TOKEN_EXPIRED",
            "USER_DISABLED",
            "USER_NOT_FOUND",
            "INVALID_REFRESH_TOKEN",
            "INVALID_GRANT_TYPE",
            "MISSING_REFRESH_TOKEN",
        ]

        if error_message in known_errors:
            return None, None, None

        # If the error is not one of the known errors, then raise an HTTPError
        response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        # If we catch an HTTPError, we check if it's due to one of the known errors after raise_for_status() call
        if response.status_code == 400:
            return None, None, None
        else:
            # For unexpected HTTP errors, log the error.
            click.echo(f"HTTP request error: {e}")
            raise e
    except requests.exceptions.RequestException as e:
        # For other types of requests exceptions, log the error.
        click.echo(f"Request error: {e}")
        raise e
    except ValueError:
        # If the response couldn't be decoded as JSON, log the error.
        click.echo("Invalid JSON response.")
        raise

    return None, None, None


def is_token_valid(id_token):
    data = {"idToken": id_token}

    try:
        response = requests.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}",
            json=data,
            timeout=5,
        )

        # If the request was successful, the token is valid.
        if response.status_code == 200:
            return True

        # Handle potential JSON response even in error cases
        response_json = response.json()
        error_message = response_json.get("error", {}).get("message")

        # Check for specific error messages indicating invalid token or user not found
        if error_message in ("INVALID_ID_TOKEN", "USER_NOT_FOUND"):
            return None

    except requests.exceptions.RequestException as e:
        click.echo(f"Request error: {e}")
    except ValueError:
        click.echo("Invalid JSON response.")

    # Return False for other errors not explicitly handled above
    return False