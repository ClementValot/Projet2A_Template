import datetime

from freezegun import freeze_time

from src.Service.JWTService import JwtService

jwt_service = JwtService("mysecret")


@freeze_time("2024-08-26 12:00:00")
def test_encode_jwt():
    user_id = "myUser"
    jwt_response = jwt_service.encode_jwt(user_id=user_id)

    expected_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyX2lkIjoibXlVc2VyIiwiZXhwaXJ5X3RpbWVzdGFtcCI6MTcyNDY3NTQwMC4wfQ."
        "HGQSpvCYTD3h7H9_Ys--ReQabvdOsdikeofkMHtHYMc"
    )

    assert jwt_response.access_token == expected_token


@freeze_time("2024-08-26 12:00:00")
def test_decode_jwt():
    jwt_token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJ1c2VyX2lkIjoibXlVc2VyIiwiZXhwaXJ5X3RpbWVzdGFtcCI6MTcyNDY3NDIwMC4wfQ."
        "eUjNbpMCDNuPESsMHF2dpeRlDl6fMJmjUWsHSZT_n1Q"
    )

    decoded_jwt = jwt_service.decode_jwt(jwt_token)

    assert decoded_jwt.get("user_id") == "myUser"
    assert datetime.datetime.fromtimestamp(decoded_jwt.get("expiry_timestamp")) == datetime.datetime.fromisoformat(
        "2024-08-26 12:10:00"
    )
