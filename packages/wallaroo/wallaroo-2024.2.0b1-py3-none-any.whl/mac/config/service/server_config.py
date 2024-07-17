"""This module features the ServerConfig class, for specifying the server
configuration."""

from ipaddress import IPv4Address

from pydantic import BaseModel, StrictInt, StrictStr, field_validator


class ServerConfig(BaseModel):
    """This class implements the ServerConfig class, for specifying the connection
    configuration for a server."""

    # the host to serve the model on
    host: StrictStr = "0.0.0.0"

    # the port to serve the model on
    port: StrictInt = 8080

    @field_validator("host")
    @classmethod
    def validate_host(cls, value):
        """Validate host."""
        try:
            IPv4Address(value)
            return value
        except ValueError as error:
            raise ValueError("Invalid IP address") from error

    @field_validator("port")
    @classmethod
    def validate_port(cls, value):
        """Validate port."""
        if not isinstance(value, int) or value <= 0 or value > 65535:
            raise ValueError("Invalid port number")
        return value
