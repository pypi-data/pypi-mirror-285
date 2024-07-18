# © Copyright 2024 Hewlett Packard Enterprise Development LP
import csv
import os
import subprocess

import yaml


class TestCli:
    testdir = os.path.dirname(os.path.realpath(__file__))

    def test_version(self, setup_login: None) -> None:
        version_file = self.testdir + "/../../../../VERSION"
        expected = None
        with open(version_file, "r") as file:
            expected = file.read().rstrip()
            expected = "aioli " + expected
        assert 0 == os.system("aioli --version")
        actual = os.popen("aioli --version").read().strip()
        assert actual == expected

    def test_version_bad(self, setup_login: None) -> None:
        bad_version = "aioli 0.0.1-bad"
        assert 0 == os.system("aioli --version")
        actual = os.popen("aioli --version").read().strip()
        assert actual != bad_version

    def test_registry_list(self, setup_login: None) -> None:
        # Validating table headers, there are no entries yet
        assert os.system("aioli registry list") == 0
        expected = (
            " Name   | Type   | Access Key   | Bucket   | Secret Key   | Endpoint URL"
            "\n--------+--------+--------------+----------+--------------+----------------\n"
        )
        actual = subprocess.check_output(["aioli", "registry", "list"]).decode("utf-8")
        assert actual == expected

    def test_registry_create_and_update_insecure(self, setup_login: None) -> None:
        # Create a registry with insecure-https and test for expected values
        assert (
            os.system(
                "aioli registry create --type s3 --access-key minioadmin "
                "--secret-key minioadmin --bucket demo-bento-registry "
                "--endpoint-url http://10.30.89.14:30008 --insecure-https bento-registry-insecure"
            )
            == 0
        )

        # Newly created registry entry without id/modified as dict
        expected = yaml.safe_load(
            "accessKey: minioadmin\nbucket: demo-bento-registry\nendpointUrl: "
            "http://10.30.89.14:30008\ninsecureHttps: true\n"
            "name: bento-registry-insecure\nsecretKey: '**********'\ntype: s3\n\n"
        )
        actualstr = subprocess.check_output(
            ["aioli", "registry", "show", "bento-registry-insecure"]
        ).decode("utf-8")
        actual = yaml.safe_load(actualstr)
        del actual["id"]
        del actual["modifiedAt"]
        assert actual == expected

        # Update to secure
        if False:
            # This is blocked until CI is at python 3.9 -- then update
            # registry.py to use action=argparse.BoolOptionalAction
            assert (
                os.system("aioli registry update --no-insecure-https bento-registry-insecure") == 0
            )
            expected["insecureHttps"] = False
            actual = subprocess.check_output(
                ["aioli", "registry", "show", "bento-registry-insecure"]
            ).decode("utf-8")
            actual = yaml.safe_load(actual)
            del actual["id"]
            del actual["modifiedAt"]
            assert actual == expected

        # Cleanup test registry
        assert os.system("aioli registry delete bento-registry-insecure") == 0

    def test_registry_create(self, setup_login: None) -> None:
        # Create a registry entry and test for success
        assert (
            os.system(
                "aioli registry create --type s3 --access-key minioadmin "
                "--secret-key minioadmin --bucket demo-bento-registry "
                "--endpoint-url http://10.30.89.14:30008/ bento-registry"
            )
            == 0
        )

        # The following test is expected to fail since we already created the
        # registry and we are trying to recreate the same.
        expected = (
            "Failed to create a registry: model registry named 'bento-registry' exists already."
        )
        try:
            subprocess.check_output(
                [
                    "aioli",
                    "registry",
                    "create",
                    "--type",
                    "s3",
                    "--access-key",
                    "minioadmin",
                    "--secret-key",
                    "minioadmin",
                    "--bucket",
                    "demo-bento-registry",
                    "--endpoint-url",
                    "http://10.30.89.14:30008/",
                    "bento-registry",
                ],
                stderr=subprocess.STDOUT,
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            actual = (e.output).decode("utf-8")
            assert (actual.find(expected)) >= 0

        # Check enforcement of --type values
        proc = subprocess.run(
            [
                "aioli",
                "registry",
                "create",
                "--type",
                "bob",
                "--access-key",
                "minioadmin",
                "--secret-key",
                "minioadmin",
                "--bucket",
                "demo-bento-registry",
                "--endpoint-url",
                "http://10.30.89.14:30008/",
                "bento-registry-wrong-type",
            ],
            capture_output=True,
        )
        assert proc.returncode == 1
        expected = (
            "Failed to create a registry: registry type must be one of the values "
            + "(s3, http, openllm, ngc), provided 'bob'"
        )
        assert proc.stderr.decode("utf-8").find(expected) == 0

        # List the newly created registry entry and test for expected values
        expected = (
            "bento-registry | s3     | minioadmin   | demo-bento-registry | "
            "**********   | http://10.30.89.14:30008/"
        )
        actual = subprocess.check_output(["aioli", "registry", "list"]).decode("utf-8")
        assert (actual.find(expected)) > 0

    def test_registry_list_csv(self, setup_login: None) -> None:
        csv_output = subprocess.check_output(["aioli", "registry", "list", "--csv"]).decode("utf-8")
        temp_file: str = "/tmp/test-cli-r.csv"
        with open(temp_file, "w") as file:
            file.write(csv_output)
        with open(temp_file, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                assert row["Name"] == "bento-registry", "Expected bento-registry"
                assert row["Type"] == "s3", "Expected s3"
                assert row["Access Key"] == "minioadmin", "Expected minioadmin"
                assert row["Bucket"] == "demo-bento-registry", "Expected demo-bento-registry"
                assert row["Secret Key"] == "**********", "Expected **********"
                assert (
                    row["Endpoint URL"] == "http://10.30.89.14:30008/"
                ), "Expected http://10.30.89.14:30008/"

    # fmt: off
    def test_registry_list_json(self, setup_login: None) -> None:
        expected = (
            '[\n'    # noqa: Q000
            '  {\n'  # noqa: Q000
            '    "accessKey": "minioadmin",\n'
            '    "bucket": "demo-bento-registry",\n'
            '    "endpointUrl": "http://10.30.89.14:30008/",\n'
            '    "insecureHttps": false,\n'
            '    "name": "bento-registry",\n'
            '    "secretKey": "**********",\n'
            '    "type": "s3"\n'
            '  }\n'  # noqa: Q000
            ']\n'    # noqa: Q000
        )
        actual = subprocess.check_output(["aioli", "registry", "list", "--json"]).decode("utf-8")
        assert actual == expected
    # fmt: on

    def test_registry_update(self, setup_login: None) -> None:
        # Update registry and test for expected values
        subprocess.check_output(
            [
                "aioli",
                "registry",
                "update",
                "--type",
                "s3",
                "--access-key",
                "minioadmin",
                "--secret-key",
                "minioadmin",
                "--bucket",
                "demo-bento-registry",
                "--endpoint-url",
                "http://10.30.89.14:30008/",
                "--name",
                "bento-registry1",
                "bento-registry",
            ],
            stderr=subprocess.STDOUT,
        ).decode("utf-8")
        expected = (
            "bento-registry1 | s3     | minioadmin   | demo-bento-registry | "
            "**********   | http://10.30.89.14:30008/"
        )
        actual = subprocess.check_output(["aioli", "registry", "list"]).decode("utf-8")
        assert (actual.find(expected)) > 0

        # Check enforcement of --type values
        proc = subprocess.run(
            [
                "aioli",
                "registry",
                "update",
                "--type",
                "bob",
                "bento-registry1",
            ],
            capture_output=True,
        )
        assert proc.returncode == 1
        expected = (
            "Failed to modify a registry: registry type must be one of the values "
            + "(s3, http, openllm, ngc), provided 'bob'"
        )
        assert proc.stderr.decode("utf-8").find(expected) == 0

    def test_model_list(self, setup_login: None) -> None:
        # Test header row of model table, there are no entries at this point.
        assert os.system("aioli model list") == 0
        expected = (
            " Name   | Description   | Version   | URI   | Image   | Registry"
            "\n--------+---------------+-----------+-------+---------+------------\n"
        )
        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")
        assert actual == expected

    def test_model_create(self, setup_login: None) -> None:
        # Create an entry for model table and test for expected values
        assert (
            os.system(
                "aioli model create iris-tf-keras --registry bento-registry1 "
                "--url s3://demo-bento-registry/iris-tf-keras "
                "--image fictional.registry.example/imagename "
                '--description "the model description" '
                "-e name1 --env name2=value2 "
                "-a arg1 --arg arg2 '-a -optarg' "
                "--requests-cpu 1.0 "
                "--requests-memory 1Gi "
                "--requests-gpu 1.0 "
                "--limits-cpu 2.5 "
                "--limits-memory 1Gi "
                "--limits-gpu 1.0 "
                "--gpu-type T4 "
                "--format openllm"
            )
            == 0
        )
        expected = (
            "iris-tf-keras | the model description |         1 | "
            "s3://demo-bento-registry/iris-tf-keras | "
            "fictional.registry.example/imagename | bento-registry1"
        )
        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")
        assert (actual.find(expected)) > 0

    def test_model_list_csv(self, setup_login: None) -> None:
        csv_output = subprocess.check_output(["aioli", "model", "list", "--csv"]).decode("utf-8")
        temp_file: str = "/tmp/test-cli-m.csv"
        with open(temp_file, "w") as file:
            file.write(csv_output)
        with open(temp_file, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                assert row["Name"] == "iris-tf-keras", "Expected iris-tf-kerasy"
                assert (
                    row["Description"] == "the model description"
                ), "Expected 'the model description'"
                assert row["Version"] == "1", "Expected 1"
                assert (
                    row["URI"] == "s3://demo-bento-registry/iris-tf-keras"
                ), "Expected s3://demo-bento-registry/iris-tf-keras"
                assert (
                    row["Image"] == "fictional.registry.example/imagename"
                ), "Expected fictional.registry.example/imagename"
                assert row["Registry"] == "bento-registry1", "Expected bento-registry1"

    # Exercise various means of specifying the model version, using the show command as a vehicle.
    def test_model_versions(self, setup_login: None) -> None:
        yaml_output = subprocess.check_output(["aioli", "model", "show", "iris-tf-keras"]).decode(
            "utf-8"
        )
        temp_file: str = "/tmp/test-cli-m.yaml"

        # Demonstrate that we have valid yaml
        with open(temp_file, "w") as file:
            file.write(yaml_output)
        with open(temp_file, newline="") as file:
            from ruamel.yaml import YAML

            yaml = YAML(typ="safe")
            model = yaml.load(file)

        assert model["version"] == 1, "Validity check -- version == 1"

        yaml_output2 = subprocess.check_output(
            ["aioli", "model", "show", "iris-tf-keras.v1"]
        ).decode("utf-8")
        assert yaml_output == yaml_output2, "Expect the same output using .v1"

        yaml_output2 = subprocess.check_output(
            ["aioli", "model", "show", "iris-tf-keras.V1"]
        ).decode("utf-8")
        assert yaml_output == yaml_output2, "Expect the same output using .V1"

    # fmt: off
    def test_model_list_json(self, setup_login: None) -> None:
        expected = (
            '[\n'    # noqa: Q000
            '  {\n'  # noqa: Q000
            '    "arguments": [\n'
            '      "arg1",\n'
            '      "arg2",\n'
            '      "-optarg"\n'
            '    ],\n'  # noqa: Q000
            '    "description": "the model description",\n'
            '    "environment": {\n'
            '      "name1": "",\n'
            '      "name2": "value2"\n'
            '    },\n'  # noqa: Q000
            '    "image": "fictional.registry.example/imagename",\n'
            '    "modelFormat": "openllm",\n'
            '    "name": "iris-tf-keras",\n'
            '    "registry": "bento-registry1",\n'
            '    "resources": {\n'
            '      "gpuType": "T4",\n'
            '      "limits": {\n'
            '        "cpu": "2.5",\n'
            '        "gpu": "1.0",\n'
            '        "memory": "1Gi"\n'
            '      },\n'  # noqa: Q000
            '      "requests": {\n'
            '        "cpu": "1.0",\n'
            '        "gpu": "1.0",\n'
            '        "memory": "1Gi"\n'
            '      }\n'  # noqa: Q000
            '    },\n'   # noqa: Q000
            '    "url": "s3://demo-bento-registry/iris-tf-keras",\n'
            '    "version": 1\n'
            '  }\n'  # noqa: Q000
            ']\n'    # noqa: Q000
        )
        actual = subprocess.check_output(["aioli", "model", "list", "--json"]).decode("utf-8")
        assert actual == expected
    # fmt: on

    def test_model_create_no_image(self, setup_login: None) -> None:
        # The image is optional; verify...
        assert (
            os.system(
                "aioli model create openllm --registry bento-registry1 "
                "--format openllm "
                "--url s3://demo-bento-registry/iris-tf-keras "
                '--description "the model description"'
            )
            == 0
        )
        expected = (
            "openllm       | the model description |         1 | "
            "s3://demo-bento-registry/iris-tf-keras |"
            "                                      | bento-registry1"
        )
        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")

        assert (actual.find(expected)) > 0
        assert os.system("aioli model delete openllm.v1") == 0

    def test_model_update_bad_model_name(self, setup_login: None) -> None:
        # Attempt to update model specifying the version incorrectly. Here we specify
        # a suffix of ".1", and not ".v1" which would specify the name & version.
        # assert (os.system("aioli model update iris-tf-keras.1") == 0)
        try:
            subprocess.check_output(
                ["aioli", "model", "update", "iris-tf-keras.1"], stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as e:
            assert e.returncode == 1
            expected = "Failed to modify a packaged model: model 'iris-tf-keras.1' does not exist."
            actual: str = e.output.decode("utf-8")
            assert actual.find(expected) == 0

    def test_model_update(self, setup_login: None) -> None:
        # Update existing model entry and test for expected values
        assert (
            os.system(
                "aioli model update iris-tf-keras --name iris-tf-keras1 "
                "--registry bento-registry1 "
                "--url s3://demo-bento-registry/iris-tf-keras_updated "
                "--image fictional.registry.example/updated_imagename "
                '--description "the updated model description"'
            )
            == 0
        )
        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")
        expected = (
            "iris-tf-keras1 | the updated model description |         1 "
            "| s3://demo-bento-registry/iris-tf-keras_updated | "
            "fictional.registry.example/updated_imagename | bento-registry1"
        )
        assert (actual.find(expected)) > 0

        # Create a second version of the model
        assert (
            os.system(
                "aioli model update iris-tf-keras --name iris-tf-keras "
                "--registry bento-registry1 "
                "--url s3://demo-bento-registry/iris-tf-keras_updated_v2 "
                "--image fictional.registry.example/updated_imagename "
                '--description "the updated model description"'
            )
            == 0
        )
        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")
        expected = (
            "iris-tf-keras  | the updated model description |         2 "
            "| s3://demo-bento-registry/iris-tf-keras_updated_v2 | "
            "fictional.registry.example/updated_imagename | bento-registry1"
        )
        assert (actual.find(expected)) > 0

        # Try to create a third version of the model which fails without version
        assert (
            os.system(
                "aioli model update iris-tf-keras --name iris-tf-keras "
                "--registry bento-registry1 "
                "--url s3://demo-bento-registry/iris-tf-keras_updated_v2 "
                "--image fictional.registry.example/updated_imagename "
                '--description "the updated model description"'
            )
            == 256
        )

        # Create a third version of the model using the second version
        assert (
            os.system(
                "aioli model update iris-tf-keras.v2 --name iris-tf-keras "
                "--registry bento-registry1 "
                "--url s3://demo-bento-registry/iris-tf-keras_updated_v3 "
                "--image fictional.registry.example/updated_imagename "
                '--description "the updated model description"'
            )
            == 0
        )

        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")

        expected = (
            "iris-tf-keras  | the updated model description |         3 "
            "| s3://demo-bento-registry/iris-tf-keras_updated_v3 | "
            "fictional.registry.example/updated_imagename | bento-registry1"
        )
        assert (actual.find(expected)) > 0

        # Create a fourth with a new name of the model using the second version
        # (specifying the version with the optional v{n} format)
        assert (
            os.system(
                "aioli model update iris-tf-keras.v2 --name iris-tf-keras-v4 "
                "--registry bento-registry1 "
                "--url s3://demo-bento-registry/iris-tf-keras_updated_v3 "
                "--image fictional.registry.example/updated_imagename "
                '--description "the updated model description"'
            )
            == 0
        )

        actual = subprocess.check_output(["aioli", "model", "list"]).decode("utf-8")

        expected = (
            "iris-tf-keras-v4 | the updated model description |         1 "
            "| s3://demo-bento-registry/iris-tf-keras_updated_v3 | "
            "fictional.registry.example/updated_imagename | bento-registry1"
        )
        assert (actual.find(expected)) > 0

    def test_deployment_create(self, setup_login: None) -> None:
        # Create a deployment and test for expected values
        assert (
            os.system(
                "aioli deployment create --model iris-tf-keras "
                "--namespace aioli "
                "--authentication-required false "
                "iris-tf-keras-deployment"
            )
            == 0
        )
        actual = subprocess.check_output(["aioli", "deployment", "list"]).decode("utf-8")
        expected = (
            "iris-tf-keras-deployment | iris-tf-keras |         3 | aioli       "
            "| Deploying | False           | Deploying |           0"
        )

        assert actual.find(expected) > 0

    def test_deployment_list_csv(self, setup_login: None) -> None:
        csv_output = subprocess.check_output(["aioli", "deployment", "list", "--csv"]).decode(
            "utf-8"
        )
        temp_file: str = "/tmp/test-cli-d.csv"
        with open(temp_file, "w") as file:
            file.write(csv_output)
        with open(temp_file, newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                assert (
                    row["Name"] == "iris-tf-keras-deployment"
                ), "Expected iris-tf-keras-deployment"
                assert row["Model"] == "iris-tf-keras", "Expected iris-tf-keras"
                assert row["Namespace"] == "aioli", "Expected aioli"
                assert row["Status"] == "Deploying", "Expected Deploying"
                assert row["Auth Required"] == "False", "Expected False"
                assert row["State"] == "Deploying", "Expected Deploying"
                assert row["Traffic %"] == "0", "Expected 0"

    def test_deployment_update(self, setup_login: None) -> None:
        # Update the deployment and test for expected values.
        assert (
            os.system(
                "aioli deployment update "
                "--authentication-required true "
                "--model iris-tf-keras "
                "iris-tf-keras-deployment"
            )
            == 0
        )
        actual = subprocess.check_output(["aioli", "deployment", "list"]).decode("utf-8")

        expected = (
            "iris-tf-keras-deployment | iris-tf-keras |         3 | aioli       "
            "| Deploying | True            | Deploying |           0"
        )
        assert actual.find(expected) > 0

        # Disallow --pause and --resume at the same time
        proc = subprocess.run(
            [
                "aioli",
                "deployment",
                "update",
                "iris-tf-keras-deployment",
                "--pause",
                "--resume",
            ],
            capture_output=True,
        )
        assert proc.returncode == 1
        expected = "--pause and --resume cannot be specified at the same time"
        assert proc.stderr.decode("utf-8").find(expected) == 0

        # List the models and it's version for the deployment
        actual = subprocess.check_output(
            ["aioli", "model", "list-deployments", "iris-tf-keras"]
        ).decode("utf-8")
        expected = "| iris-tf-keras |         3"
        assert actual.find(expected) > 0

    # fmt: off
    def test_deployment_list_json(self, setup_login: None) -> None:
        expected = (
            '[\n'    # noqa: Q000
            '  {\n'  # noqa: Q000
            '    "autoScaling": {\n'
            '      "maxReplicas": 1,\n'
            '      "metric": "concurrency",\n'
            '      "minReplicas": 0,\n'
            '      "target": 1\n'
            '    },\n'  # noqa: Q000
            '    "canaryTrafficPercent": 100,\n'
            '    "environment": {},\n'
            '    "goalStatus": "Ready",\n'
            '    "model": "iris-tf-keras",\n'
            '    "name": "iris-tf-keras-deployment",\n'
            '    "namespace": "aioli",\n'
            '    "secondaryState": {\n'
            '      "endpoint": "",\n'
            '      "modelId": "",\n'
            '      "nativeAppName": "",\n'
            '      "status": "None",\n'
            '      "trafficPercentage": 0\n'
            '    },\n'  # noqa: Q000
            '    "security": {\n'
            '      "authenticationRequired": true\n'
            '    },\n'  # noqa: Q000
            '    "state": {\n'
            '      "endpoint": "",\n'
            '      "modelId": "",\n'
            '      "nativeAppName": "",\n'
            '      "status": "Deploying",\n'
            '      "trafficPercentage": 0\n'
            '    },\n'  # noqa: Q000
            '    "status": "Deploying",\n'
            '    "version": "3"\n'
            '  }\n'  # noqa: Q000
            ']\n'    # noqa: Q000
        )
        actual = subprocess.check_output(["aioli", "deployment", "list", "--json"]).decode("utf-8")
        assert actual == expected
    # fmt: on

    def test_deployment_create_with_all_options(self, setup_login: None) -> None:
        # Create a second deployment with all supported options
        # and test for expected values
        assert (
            os.system(
                "aioli deployment create --model iris-tf-keras "
                "--namespace aioli "
                "--authentication-required false "
                "--autoscaling-min-replicas 1 "
                "--autoscaling-max-replicas 10 "
                "--autoscaling-target 1 "
                "--autoscaling-metric concurrency "
                "--canary-traffic-percent 20 "
                "-a='--debug' "
                "-e MODS=SOME "
                "iris-tf-keras-deployment-2"
            )
            == 0
        )

    def test_deployment_show(self, setup_login: None) -> None:
        # Test deployment table header, there are no entries at this point.
        assert os.system("aioli deployment show iris-tf-keras-deployment-2") == 0
        expected = None
        data_file = self.testdir + "/aioli_deployment_show.txt"
        with open(data_file, "r") as file:
            expected = file.read()
        result = subprocess.check_output(
            ["aioli", "deployment", "show", "iris-tf-keras-deployment-2"]
        ).decode("utf-8")
        result_list = result.split("\n")
        filtered_result = ""

        # Filter out modifiedAt and id fields as they vary for each test run
        for line in result_list:
            if "modifiedAt" in line:
                continue
            if "id" in line:
                continue
            filtered_result = filtered_result + "\n" + line

        actual = filtered_result.strip()
        assert actual == expected

    def test_deployment_update_args_environment(self, setup_login: None) -> None:
        # Update the deployments arguments and environment and check that changes
        # were made.
        assert (
            os.system(
                "aioli deployment update "
                "-a='--updated' "
                "-e MODS=UPDATED "
                "--env OTHER=VALUE "
                "iris-tf-keras-deployment-2"
            )
            == 0
        )

        result = subprocess.check_output(
            ["aioli", "deployment", "show", "iris-tf-keras-deployment-2"]
        ).decode("utf-8")
        result_list = result.split("\n")
        args_found = False
        other_found = False
        for line in result_list:
            if "- --updated" in line:
                args_found = True
            if "MODS: UPDATED" in line:
                mods_found = True
            if "OTHER: VALUE" in line:
                other_found = True

        assert args_found
        assert mods_found
        assert other_found

    def test_deployment_delete(self, setup_login: None) -> None:
        assert os.system("aioli deployment delete iris-tf-keras-deployment") == 0
        assert os.system("aioli deployment delete iris-tf-keras-deployment-2") == 0

    def test_model_delete(self, setup_login: None) -> None:
        assert os.system("aioli model delete iris-tf-keras1") == 0
        assert os.system("aioli model delete iris-tf-keras.v1") == 0
        assert os.system("aioli model delete iris-tf-keras.v2") == 0
        assert os.system("aioli model delete iris-tf-keras.v3") == 0
        assert os.system("aioli model delete iris-tf-keras-v4.v1") == 0

    def test_registry_delete(self, setup_login: None) -> None:
        # Delete the registry entry
        assert os.system("aioli registry delete bento-registry1") == 0

    def test_user_list(self, setup_login: None) -> None:
        # Test the user table header fields
        assert os.system("aioli user list") == 0
        expected = "admin      | Default Administrator | True     | False"
        actual = subprocess.check_output(["aioli", "user", "list"]).decode("utf-8")
        assert (actual.find(expected)) > 0

    def test_user_create(self, setup_login: None) -> None:
        # create a user and test for expected values
        assert os.system("aioli user create testuser --password passwd") == 0
        expected = "testuser   |"
        actual = subprocess.check_output(["aioli", "user", "list"]).decode("utf-8")
        assert (actual.find(expected)) > 0

    def test_user_whoami(self, setup_login: None) -> None:
        assert os.system("aioli user whoami") == 0
        expected = "You are logged in as user 'admin'\n"
        actual = subprocess.check_output(["aioli", "user", "whoami"]).decode("utf-8")
        assert actual == expected

    def test_user_activate(self, setup_login: None) -> None:
        # Check activate feature
        assert os.system("aioli user activate testuser") == 0

    def test_user_deactivate(self, setup_login: None) -> None:
        # Check deactivate feature
        assert os.system("aioli user deactivate testuser") == 0

    def test_user_create_remote(self, setup_login: None) -> None:
        # create a remote user and test for expected values
        assert os.system("aioli user create --remote testuser-r") == 0
        expected = "testuser-r |                       | True     | True"
        actual = subprocess.check_output(["aioli", "user", "list"]).decode("utf-8")
        assert (actual.find(expected)) > 0
