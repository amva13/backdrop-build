import pandas as pd
import syft as sy

from globals import SYFT_VERSION

sy.requires(SYFT_VERSION)

EXAMPLE_PORT = 8080

kwargs = {
    "email": "bob@example.com",
    "password": "example",
    "port": EXAMPLE_PORT,
}

if __name__ == "__main__":
    print("logging into the server")
    domain_client = sy.login(**kwargs)
    print(domain_client)
    print("exposed APIs are")
    print(domain_client.api)


    