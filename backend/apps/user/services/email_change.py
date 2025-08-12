from django.core import signing

def make_email_change_token(user_id: int, new_email: str) -> str:
    """
    Create a token for email change that includes user ID and new email.
    The token is signed to ensure its integrity.
    """
    payload = {
        'user_id': user_id,
        'new_email': new_email
    }
    return signing.dumps(payload)

def parse_email_change_token(token: str) -> dict:
    """
    Parse the email change token and return the payload.
    Raises an exception if the token is invalid or expired.
    """
    return signing.loads(token, max_age=3600)  # Token is valid for 1 hour

# TODO : Implement real email sending logic
