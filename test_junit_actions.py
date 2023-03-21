from unittest.mock import MagicMock, call, ANY

import junit_actions

# By: GITHUB_REPOSITORY https://docs.github.com/en/actions/learn-github-actions/variables#default-environment-variables

JUNIT_FILE_CONTENT = '''
<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite name="pytest" errors="0" failures="5" skipped="0" tests="10"
               time="0.046" timestamp="2023-03-14T23:47:49.567219"
               hostname="some">
        <testcase classname="day1.test_day1" name="test_task1" time="0.001">
            <failure
                    message="Failed: DID NOT RAISE &lt;class 'ValueError'&gt;">
                def test_task1():
                &gt; with pytest.raises(ValueError):
                E Failed: DID NOT RAISE &lt;class 'ValueError'&gt;

                day1/test_day1.py:7: Failed
            </failure>
        </testcase>
        <testcase classname="day1.test_day1" name="test_true" time="0.000"/>
        <testcase classname="day1.subday1.test_subday1" name="test_ok[val1]"
                  time="0.001"/>
        <testcase classname="day1.subday1.test_subday1" name="test_ok[val2]"
                  time="0.000"/>
    </testsuite>
</testsuites>
'''.strip()


def test_parse_junit_string():
    test_suites = junit_actions.parse_junit_string(JUNIT_FILE_CONTENT)
    assert test_suites.tests == 4
    for suite in test_suites:
        # test_suite = next(test_suites)
        assert suite.name == 'pytest'
        assert suite.tests == 4
        assert suite.failures == 1
        assert suite.errors == 0


def test_junit_file_to_dynamodb_item():
    report = junit_actions.RepositoryTestReport(
        repository='vasya/python01',
        junit_report_xml='<xml/>',
    )

    result = report.as_dynamodb_item()
    assert result == {
        'repo_name': {
            'S': 'python01'
        },
        'repo_owner': {
            'S': 'vasya'
        },
        'junit_file': {
            'S': '<xml/>'
        },
    }


def test_save_to_dynamodb():
    client = MagicMock()
    report = MagicMock()
    junit_actions.save_to_dynamodb(
        report=report,
        client=client,
    )

    assert client.put_item.call_args_list == [
        call(
            TableName='junit_reports',
            Item=report.as_dynamodb_item(),
        )
    ]


def test_query_dynamodb():
    client = MagicMock()
    client.query.return_value = {
        'Count': 1,
        'Items': [
            {'repo_owner': {'S': 'petya'},
             'repo_name': {'S': 'python01'},
             'junit_file': {'S': '</xml>'}}
        ]
    }
    client = junit_actions.dynamodb_client()
    result = junit_actions.query_dynamodb(
        repo_name='python01',
        client=client,
    )

    assert client.query.call_args_list == [
        call(
            TableName='junit_reports',
            ExpressionAttributeValues={':repo_name': {'S': 'python01'}},
            KeyConditionExpression='repo_name = :repo_name',
        )
    ]
    assert result == [
        junit_actions.RepositoryTestReport(
            repository='petya/python01',
            junit_report_xml='</xml>'
        )
    ]


def test_from_dynamodb_item():
    dynamodb_item = {'repo_owner': {'S': 'petya'},
                     'repo_name': {'S': 'python01'},
                     'junit_file': {'S': '</xml>'}}
    report = junit_actions.RepositoryTestReport.from_dynamodb_item(dynamodb_item)
    assert report == junit_actions.RepositoryTestReport(
        repository='petya/python01',
        junit_report_xml='</xml>'
    )