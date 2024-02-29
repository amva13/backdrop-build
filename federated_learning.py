import pandas as pd
import syft as sy
from syft import autocache

from globals import SYFT_VERSION, EXAMPLE_DOMAIN, EXAMPLE_PORT

sy.requires(SYFT_VERSION)



params = {
    "name": EXAMPLE_DOMAIN,
    "port": EXAMPLE_PORT,
    "dev_mode": True,
    "reset": True
}

if __name__ == '__main__':
    node = sy.orchestra.launch(**params)
    
    # log into the node with default root credentials
    root_client = node.login(email="info@openmined.org", password="changethis")


    # register needed users
    # Register a new user using root credentials
    response_1 = root_client.register(
        email="bob@example.com",
        password="example",
        password_verify="example",
        name="Bob",
    )

    # register needed users
    # Register a new user using root credentials
    response_2 = root_client.register(
        email="alice@example.com",
        password="example2",
        password_verify="example2",
        name="Alice",
    )
    
    assert root_client.settings.get().signup_enabled is False
    assert isinstance(response_1, sy.SyftSuccess)
    assert isinstance(response_2, sy.SyftSuccess)

    #upload data
    print("Starting data upload from root")
    domain_client = root_client
    # Check for existing Data Subjects
    print("check starting from clean")
    data_subjects = domain_client.data_subject_registry.get_all()
    print("showing data_subjects object")
    assert len(data_subjects) == 0 # none have been uploaded yet
    
    # uploads
    print("uploading data subjects")
    country = sy.DataSubject(name="Country", aliases=["country_code"])
    canada = sy.DataSubject(name="Canada", aliases=["country_code:ca"])
    germany = sy.DataSubject(name="Germany", aliases=["country_code:de"])
    spain = sy.DataSubject(name="Spain", aliases=["country_code:es"])
    france = sy.DataSubject(name="France", aliases=["country_code:fr"])
    japan = sy.DataSubject(name="Japan", aliases=["country_code:jp"])
    uk = sy.DataSubject(name="United Kingdom", aliases=["country_code:uk"])
    usa = sy.DataSubject(name="United States of America", aliases=["country_code:us"])
    australia = sy.DataSubject(name="Australia", aliases=["country_code:au"])
    india = sy.DataSubject(name="India", aliases=["country_code:in"])
    
    country.add_member(canada)
    country.add_member(germany)
    country.add_member(spain)
    country.add_member(france)
    country.add_member(japan)
    country.add_member(uk)
    country.add_member(usa)
    country.add_member(australia)
    country.add_member(india)

    print("showing  members of Country data subject")
    print(country.members)
    
    # register subject and all members
    response = domain_client.data_subject_registry.add_data_subject(country)
    assert response  # did it work?
    
    # Lets look at the data subjects added to the data
    data_subjects = domain_client.data_subject_registry.get_all()
    print("showing subjects in registry")
    print(data_subjects)
    assert len(data_subjects) == 10 # 10 data subjects have been uploaded
    # prepare the dataset
    canada_dataset_url = "https://github.com/OpenMined/datasets/blob/main/trade_flow/ca%20-%20feb%202021.csv?raw=True"
    df = pd.read_csv(autocache(canada_dataset_url))
    print("downloaded dataset for uploading")
    print(df.head())
    
    # example private version dataset
    ca_data = df[0:10]
    # example mock version dataset -- public
    mock_ca_data = df[10:20]
    
    # syft dataset
    print("creating syft dataset")
    dataset = sy.Dataset(name="Canada Trade Value")
    dataset.set_description("Canada Trade Data")
    dataset.add_citation("Person, place or thing")
    dataset.add_url("https://github.com/OpenMined/datasets/tree/main/trade_flow")
    
    dataset.add_contributor(
        name="Andrew Trask",
        email="andrew@openmined.org",
        note="Andrew runs this domain and prepared the dataset metadata.",
    )

    dataset.add_contributor(
        name="Madhava Jay",
        email="madhava@openmined.org",
        note="Madhava tweaked the description to add the URL because Andrew forgot.",
    )
    
    assert len(dataset.contributors) == 2
    
    print("adding downloaded data to the created syft dataset")
    ctf = sy.Asset(name="canada_trade_flow")
    ctf.set_description(
        "Canada trade flow represents export & import of different commodities to other countries"
    )
    ctf.add_contributor(
        name="Andrew Trask",
        email="andrew@openmined.org",
        note="Andrew runs this domain and prepared the asset.",
    )
    print("adding private data to the created asset")
    ctf.set_obj(ca_data)
    ctf.set_shape(ca_data.shape)
    ctf.add_data_subject(canada)
    ctf.set_mock(mock_ca_data, mock_is_real=False)  # can use ctf.no_mock() if no mock desired
    dataset.add_asset(ctf)  # dataset.remove_asset(ctf) will remove it from the dataset
    
    print("uploading syft dataset to the domain server")
    domain_client.upload_dataset(dataset)
    
    print("checking all data was uploaded correctly, and that bob, as the owner, can access it")
    datasets = domain_client.datasets.get_all()
    assert len(datasets) == 1
    mock = domain_client.datasets[0].assets[0].mock
    assert mock_ca_data.equals(mock)
    real = domain_client.datasets[0].assets[0].data
    assert ca_data.equals(real)
    print("Data upload and user registry done!")
