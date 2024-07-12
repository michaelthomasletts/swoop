# What is it?
Simple Python package for generating automatically refreshable AWS credentials with `boto3` and `botocore`.

# Testing
Presently, this package does not include any tests. Reason being that testing requires infrastructure and configuration which, of course, is unavailable.

If this package included testing, however, then I would have employed `pytest`, which is a popular unit testing framework for Python code bases. It features rich logs and tracebacks, and it is light-weight and easy to use. 

A relevant unit test for this code would involve 1) initializing the `AutoRefreshableSession` object using an AWS profile stored on whatever machine runs unit tests in the CI-CD pipeline and 2) attempts to run a trivial request via the AWS API, e.g. `GetObject` request to S3. `ClientError` exceptions from `boto3` would constitute failure.