# Saphira Python Setup

To get the Python set up, just run the following command from any standard command line tool:

```
pip install saphira
```

We currently support Python >= 3.9, but can introduce other support if needed. Please reach out to founders@saphira.ai if this is needed.

# Getting the API Token

If you have created a Saphira account, please click the [settings link](https://prod.saphira.ai/dashboard/settings) and scroll down to API token on the General tab to see the API token. This token will not change and will be the same token throughout using our API. 

# Setting Up and Using the API

To use the API, please make sure the environment variable SAPHIRA_API_TOKEN is set based on the value in the account you find above.

To access individual values linked to requirements of a specific project, please use the command below: 

```
saphira.get_param(<project>, <req>)
```

One idiosyncrasy is that the project ID currently contains .json, so copy that full value from the URL. Additionally, the requirement value is just the requirement name.

# Using the CLI

Simply pass the project_id and pipe in details, starting with the unique test name on its own line:

```
cat test.txt | python -m saphira <uuid>.json
```

# API Outputs

When you call API, we capture the script that the API is referenced in. As a longer term initiative, we could version these scripts and even surface this whole script collection within a git repo. 

While get_param instantiates the test that you see in the UI, update_test_status marks it as passing or failing. As you can see from the lib header, we offer a few different possible inputs:

```
update_test_status(project: str, requirement: str, passing: bool = False, test_result: Optional[TestResult] = None, exception: Exception = None)
```

Note that we’ll treat the filename as the test name, which is why you don’t have to manually pass it here. Furthermore, the TestResult type is from UnitTest, so that you can do the following:

```
test = unittest.main(exit=False)
saphira.update_test_status(PROJECT, REQ, test_result=test.result)
```

Finally, you could alternatively pass an exception, like this:

```
except Exception as e:
    saphira.update_test_status(PROJECT, REQ, exception=e)
```
