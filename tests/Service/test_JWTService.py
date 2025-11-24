import datetime

from freezegun import freeze_time

from src.Service.JWTService import JwtService

jwt_service = JwtService()


@freeze_time("2024-08-26 12:00:00")
def test_encode_jwt():
    user_id = "myUser"
    user_role = "customer"
    jwtResponse = jwt_service.encode_jwt(user_id=user_id, user_role=user_role)
    print(jwtResponse.access_token)
    assert (
        jwtResponse.access_token
        == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoibXlVc2VyIiwidXNlcl9yb2xlIjoiY3VzdG9tZXIiLCJleHBpcnlfdGltZXN0YW1wIjoxNzI0Njc3MjAwLjB9.Zmay-jStMDgD5GssJXrkTC9VLNVQddorYVwPomF93XE"  # noqa: E501
    )


@freeze_time("2024-08-26 12:00:00")
def test_decode_jwt():
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoibXlVc2VyIiwiZXhwaXJ5X3RpbWVzdGFtcCI6MTcyNDY3NDIwMC4wfQ.6BlZzHEW-KWlL1JYtmJol4aArumjZOxWSe0kBumSSMs"  # noqa: E501
    decoded_jwt = jwt_service.decode_jwt(jwt)
    assert decoded_jwt.get("user_id") == "myUser"
    assert datetime.datetime.fromtimestamp(
        decoded_jwt.get("expiry_timestamp")
    ) == datetime.datetime.fromisoformat("2024-08-26 12:10:00")
