import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

import boto3 as boto3
from junitparser import JUnitXml

DYNAMODB_TABLE = 'junit_reports'


@dataclass
class RepositoryTestReport:
    repository: str
    junit_report_xml: str

    @classmethod
    def from_dynamodb_item(cls, item):
        repo_owner = item['repo_owner']['S']
        repo_name = item['repo_name']['S']
        junit_report_xml = item['junit_file']['S']
        repository = '/'.join([repo_owner, repo_name])
        return RepositoryTestReport(
            repository=repository,
            junit_report_xml=junit_report_xml
        )

    def repo_owner(self):
        return self.repository.split('/')[0]

    def repo_name(self):
        return self.repository.split('/')[1]

    def junit_report(self):
        return parse_junit_string(self.junit_report_xml)

    def as_dynamodb_item(self):
        return {
            'repo_name': {
                'S': self.repo_name()
            },
            'repo_owner': {
                'S': self.repo_owner()
            },
            'junit_file': {
                'S': self.junit_report_xml
            },
        }


def parse_junit_file(filename):
    return JUnitXml.fromfile(filename)


def parse_junit_string(junit_xml_context) -> JUnitXml:
    return JUnitXml.fromstring(junit_xml_context)


def save_to_dynamodb(report: RepositoryTestReport, client):
    return client.put_item(
        TableName=DYNAMODB_TABLE,
        Item=report.as_dynamodb_item(),
    )


def main(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', '-f')
    parser.add_argument('--repo', '-r')
    parser.add_argument('--query', '-q')
    parsed = parser.parse_args(args)


    query = parsed.query
    client = dynamodb_client()

    if query:
        reports = query_dynamodb(
            repo_name=query,
            client=dynamodb_client(),
        )
        generate_report(reports)
    else:
        filename = parsed.filename
        repository = parsed.repo
        assert filename
        assert repository

        junit_content = Path(filename).read_text()
        report = RepositoryTestReport(
            repository=repository,
            junit_report_xml=junit_content,
        )
        save_to_dynamodb(
            report=report,
            client=client,
        )


def query_dynamodb(repo_name, client):
    assert repo_name
    response = client.query(
        TableName=DYNAMODB_TABLE,
        ExpressionAttributeValues={
            ':repo_name': {
                'S': repo_name,
            },
        },
        KeyConditionExpression='repo_name = :repo_name'
    )
    return [RepositoryTestReport.from_dynamodb_item(item) for item in
            response['Items']]


def generate_report(reports: list[RepositoryTestReport]):
    for report in reports:
        print(f'Owner: {report.repo_owner()}')
        for suite in report.junit_report():
            print(suite.errors)
            print(suite.tests)
            for test_case in suite:
                print(test_case)



def dynamodb_client():
    return boto3.client('dynamodb')


if __name__ == '__main__':
    main(sys.argv[1:])
