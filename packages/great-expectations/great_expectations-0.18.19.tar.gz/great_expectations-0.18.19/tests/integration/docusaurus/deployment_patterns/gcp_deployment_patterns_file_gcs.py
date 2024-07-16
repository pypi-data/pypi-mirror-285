import os
import pathlib
import tempfile

from great_expectations.core.yaml_handler import YAMLHandler
from great_expectations.data_context.data_context.file_data_context import (
    FileDataContext,
)

temp_dir = tempfile.TemporaryDirectory()
full_path_to_project_directory = pathlib.Path(temp_dir.name).resolve()

yaml = YAMLHandler()

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py get_context">
import great_expectations as gx

context = gx.data_context.FileDataContext.create(full_path_to_project_directory)
# </snippet>


# NOTE: The following code is only for testing and depends on an environment
# variable to set the gcp_project. You can replace the value with your own
# GCP project information
gcp_project = os.environ.get("GE_TEST_GCP_PROJECT")
if not gcp_project:
    raise ValueError(
        "Environment Variable GE_TEST_GCP_PROJECT is required to run GCS integration tests"
    )

# parse great_expectations.yml for comparison
great_expectations_yaml_file_path = pathlib.Path(
    context.root_directory, FileDataContext.GX_YML
)
with open(great_expectations_yaml_file_path) as f:
    great_expectations_yaml = yaml.load(f)

stores = great_expectations_yaml["stores"]
pop_stores = [
    "checkpoint_store",
    "evaluation_parameter_store",
    "validations_store",
    "profiler_store",
]
for store in pop_stores:
    stores.pop(store)

actual_existing_expectations_store = {}
actual_existing_expectations_store["stores"] = stores
actual_existing_expectations_store["expectations_store_name"] = great_expectations_yaml[
    "expectations_store_name"
]
expected_existing_expectations_store_yaml = """
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py expected_expectation_store">
stores:
  expectations_store:
    class_name: ExpectationsStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: expectations/

expectations_store_name: expectations_store
# </snippet>
"""

assert actual_existing_expectations_store == yaml.load(
    expected_existing_expectations_store_yaml
)

# adding expectations store
configured_expectations_store_yaml = """
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py new_expectation_store">
stores:
  expectations_GCS_store:
    class_name: ExpectationsStore
    store_backend:
      class_name: TupleGCSStoreBackend
      project: <YOUR GCP PROJECT NAME>
      bucket: <YOUR GCS BUCKET NAME>
      prefix: <YOUR GCS PREFIX NAME>

expectations_store_name: expectations_GCS_store
# </snippet>
"""

# replace example code with integration test configuration
configured_expectations_store = yaml.load(configured_expectations_store_yaml)
configured_expectations_store["stores"]["expectations_GCS_store"]["store_backend"][
    "project"
] = gcp_project
configured_expectations_store["stores"]["expectations_GCS_store"]["store_backend"][
    "bucket"
] = "test_metadata_store"
configured_expectations_store["stores"]["expectations_GCS_store"]["store_backend"][
    "prefix"
] = "metadata/expectations"

# add and set the new expectation store
context.add_store(
    store_name=configured_expectations_store["expectations_store_name"],
    store_config=configured_expectations_store["stores"]["expectations_GCS_store"],
)
with open(great_expectations_yaml_file_path) as f:
    great_expectations_yaml = yaml.load(f)
great_expectations_yaml["expectations_store_name"] = "expectations_GCS_store"
great_expectations_yaml["stores"]["expectations_GCS_store"]["store_backend"].pop(
    "suppress_store_backend_id"
)
with open(great_expectations_yaml_file_path, "w") as f:
    yaml.dump(great_expectations_yaml, f)

# adding validation results store

# parse great_expectations.yml for comparison
great_expectations_yaml_file_path = pathlib.Path(
    context.root_directory, FileDataContext.GX_YML
)
with open(great_expectations_yaml_file_path) as f:
    great_expectations_yaml = yaml.load(f)

stores = great_expectations_yaml["stores"]
# popping the rest out so taht we can do the comparison. They aren't going anywhere dont worry
pop_stores = [
    "checkpoint_store",
    "evaluation_parameter_store",
    "expectations_store",
    "expectations_GCS_store",
    "profiler_store",
]
for store in pop_stores:
    stores.pop(store)

actual_existing_validations_store = {}
actual_existing_validations_store["stores"] = stores
actual_existing_validations_store["validations_store_name"] = great_expectations_yaml[
    "validations_store_name"
]

expected_existing_validations_store_yaml = """
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py expected_validations_store">
stores:
  validations_store:
    class_name: ValidationsStore
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/validations/

validations_store_name: validations_store
# </snippet>
"""
assert actual_existing_validations_store == yaml.load(
    expected_existing_validations_store_yaml
)

# adding validations store
configured_validations_store_yaml = """
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py new_validations_store">
stores:
  validations_GCS_store:
    class_name: ValidationsStore
    store_backend:
      class_name: TupleGCSStoreBackend
      project: <YOUR GCP PROJECT NAME>
      bucket: <YOUR GCS BUCKET NAME>
      prefix: <YOUR GCS PREFIX NAME>

validations_store_name: validations_GCS_store
# </snippet>
"""

# replace example code with integration test configuration
configured_validations_store = yaml.load(configured_validations_store_yaml)
configured_validations_store["stores"]["validations_GCS_store"]["store_backend"][
    "project"
] = gcp_project
configured_validations_store["stores"]["validations_GCS_store"]["store_backend"][
    "bucket"
] = "test_metadata_store"
configured_validations_store["stores"]["validations_GCS_store"]["store_backend"][
    "prefix"
] = "metadata/validations"

# add and set the new validation store
context.add_store(
    store_name=configured_validations_store["validations_store_name"],
    store_config=configured_validations_store["stores"]["validations_GCS_store"],
)
with open(great_expectations_yaml_file_path) as f:
    great_expectations_yaml = yaml.load(f)
great_expectations_yaml["validations_store_name"] = "validations_GCS_store"
great_expectations_yaml["stores"]["validations_GCS_store"]["store_backend"].pop(
    "suppress_store_backend_id"
)
with open(great_expectations_yaml_file_path, "w") as f:
    yaml.dump(great_expectations_yaml, f)

# adding data docs store
data_docs_site_yaml = """
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py new_data_docs_store">
data_docs_sites:
  local_site:
    class_name: SiteBuilder
    show_how_to_buttons: true
    store_backend:
      class_name: TupleFilesystemStoreBackend
      base_directory: uncommitted/data_docs/local_site/
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
  gs_site:  # this is a user-selected name - you may select your own
    class_name: SiteBuilder
    store_backend:
      class_name: TupleGCSStoreBackend
      project: <YOUR GCP PROJECT NAME>
      bucket: <YOUR GCS BUCKET NAME>
    site_index_builder:
      class_name: DefaultSiteIndexBuilder
# </snippet>
"""
data_docs_site_yaml = data_docs_site_yaml.replace(
    "<YOUR GCP PROJECT NAME>", gcp_project
)
data_docs_site_yaml = data_docs_site_yaml.replace(
    "<YOUR GCS BUCKET NAME>", "test_datadocs_store"
)
great_expectations_yaml_file_path = pathlib.Path(
    context.root_directory, FileDataContext.GX_YML
)
with open(great_expectations_yaml_file_path) as f:
    great_expectations_yaml = yaml.load(f)
great_expectations_yaml["data_docs_sites"] = yaml.load(data_docs_site_yaml)[
    "data_docs_sites"
]
with open(great_expectations_yaml_file_path, "w") as f:
    yaml.dump(great_expectations_yaml, f)

# adding datasource
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py datasource">
datasource = context.sources.add_pandas_gcs(
    name="gcs_datasource", bucket_or_name="test_docs_data"
)
# </snippet>

### Add GCS data to the Datasource as a Data Asset
# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py prefix_and_batching_regex">
batching_regex = r"yellow_tripdata_sample_(?P<year>\d{4})-(?P<month>\d{2})\.csv"
prefix = "data/taxi_yellow_tripdata_samples/"
# </snippet>

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py asset">
data_asset = datasource.add_csv_asset(
    name="csv_taxi_gcs_asset", batching_regex=batching_regex, gcs_prefix=prefix
)
# </snippet>

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py batch_request">
batch_request = data_asset.build_batch_request(
    options={
        "month": "03",
    }
)
# </snippet>

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py add_expectation_suite">
context.add_or_update_expectation_suite(expectation_suite_name="test_gcs_suite")

validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_gcs_suite"
)
# </snippet>

# NOTE: The following code is only for testing and can be ignored by users.
assert isinstance(validator, gx.validator.validator.Validator)

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py validator_calls">
validator.expect_column_values_to_not_be_null(column="passenger_count")

validator.expect_column_values_to_be_between(
    column="congestion_surcharge", min_value=-3, max_value=1000
)
# </snippet>

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py save_expectation_suite">
validator.save_expectation_suite(discard_failed_expectations=False)
# </snippet>

# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py checkpoint">
checkpoint = context.add_or_update_checkpoint(
    name="gcs_checkpoint",
    validations=[
        {"batch_request": batch_request, "expectation_suite_name": "test_gcs_suite"}
    ],
)
# </snippet>


# <snippet name="tests/integration/docusaurus/deployment_patterns/gcp_deployment_patterns_file_gcs.py run_checkpoint">
checkpoint_result = checkpoint.run()
# </snippet>

assert checkpoint_result.success is True
