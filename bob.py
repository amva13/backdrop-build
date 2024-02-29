# third party
import opendp.prelude as dp
import pandas as pd
import syft as sy
from syft.client.api import NodeIdentity
from syft.service.request.request import RequestStatus

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

    jane_client = domain_client
    # check datasets present in server
    results = jane_client.datasets.get_all()
    print("available datasets")
    print(results)
    assert len(results) == 1
    dataset = results[0]
    print(dataset)
    
    print("accessing mock data")
    asset = dataset.assets[0]
    mock = asset.mock
    print(mock.head())
    print("attempting access to actual data.. should fail")
    x = asset.data
    print(x)
    assert not isinstance(x, pd.DataFrame)
    
    print("submitting code to server")
    @sy.syft_function_single_use(trade_data=asset)
    def sum_trade_value_mil(trade_data):
        
        dp.enable_features("contrib")
        aggregate = 0.0
        base_lap = dp.m.make_base_laplace(
            dp.atom_domain(T=float),
            dp.absolute_distance(T=float),
            scale=5.0,
        )
        noise = base_lap(aggregate)
        df = trade_data
        total = df["Trade Value (US$)"].sum()
        return (float(total / 1_000_000), float(noise))
    
    # print("testing code on mock data")
    # pointer = sum_trade_value_mil(trade_data=asset)
    # result = pointer.get()
    # assert result[0] == 9.738381
    # assert isinstance(result[1], float)
    print("testing the syft wrapper on desired function to submit")
    # Tests
    assert len(sum_trade_value_mil.kwargs) == 1
    node_identity = NodeIdentity.from_api(jane_client.api)
    assert node_identity in sum_trade_value_mil.kwargs
    assert "trade_data" in sum_trade_value_mil.kwargs[node_identity]
    assert (
        sum_trade_value_mil.input_policy_init_kwargs[node_identity]["trade_data"]
        == asset.action_id
    )
    print(sum_trade_value_mil.code)
    print("submitting code to the domain server")
    # Create a new project
    new_project = sy.Project(
        name="My Cool UN Project",
        description="Hi, I want to calculate the trade volume in million's with my cool code.",
        members=[jane_client],
    )
    print(new_project)
    
    # Add a request to submit & execute the code
    result = new_project.create_code_request(sum_trade_value_mil, jane_client)
    assert len(jane_client.code.get_all()) == 1, str(result)
    
    print("submitting project")
    project = new_project.start()
    assert isinstance(project, sy.service.project.project.Project)
    print(project)
    
    print("testing the function without approval")
    result = jane_client.code.sum_trade_value_mil(trade_data=asset)
    print(result)
    assert isinstance(result, sy.SyftError)
    print("done!")
    
    
#     # Or when working on a project that already exists
# project = jane_client.get_project(name="My Cool UN Project")
# assert project
# assert len(project.events) == 1
# assert isinstance(project.events[0], sy.service.project.project.ProjectRequest)
# assert project.events[0].request.status == RequestStatus.PENDING
