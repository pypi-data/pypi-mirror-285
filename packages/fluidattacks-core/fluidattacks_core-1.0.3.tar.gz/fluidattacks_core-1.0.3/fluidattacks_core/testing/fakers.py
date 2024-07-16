from .constants import (
    CVSS3_VALUES,
    CVSS4_VALUES,
    FINDING_ID,
    GROUP_NAME,
    ORG_ID,
    ORG_NAME,
    TABLE_NAME,
)
from .types import (
    DynamoDBResource,
    DynamoDBTable,
    DynamoStreamsClient,
    SeverityLevelType,
    TreatmentStatusType,
    VulnerabilityStatusType,
)
import boto3 as _boto3
import cvss as _cvss
from datetime import (
    datetime,
)
from decimal import (
    Decimal,
)
from typing import (
    Any,
)


# Fields
def get_cvssf_score(temporal_score: Decimal) -> Decimal:
    return Decimal(
        pow(Decimal("4.0"), Decimal(temporal_score) - Decimal("4.0"))
    ).quantize(Decimal("0.001"))


def fake_severity_score(level: SeverityLevelType) -> dict[str, Any]:
    cvss3_vector = _cvss.CVSS3(CVSS3_VALUES[level])
    cvss4_vector = _cvss.CVSS4(CVSS4_VALUES[level])

    return {
        "cvssf": get_cvssf_score(cvss3_vector.temporal_score),
        "base_score": cvss3_vector.base_score,
        "temporal_score": cvss3_vector.temporal_score,
        "cvss_v3": cvss3_vector.clean_vector(),
        "threat_score": cvss3_vector.base_score,
        "cvssf_v4": get_cvssf_score(cvss4_vector.base_score),
        "cvss_v4": cvss4_vector.clean_vector(),
    }


# Entities
def fake_group(
    group_name: str = GROUP_NAME,
    org_id: str = ORG_ID,
    creation_date: datetime = datetime.now(),
) -> dict[str, Any]:
    date = creation_date.isoformat()

    return {
        "id": group_name,
        "pk": f"GROUP#{group_name}",
        "sk": f"ORG#{org_id}",
        "name": group_name,
        "description": f"{group_name} description",
        "language": "EN",
        "created_date": date,
    }


def fake_finding(
    finding_id: str = FINDING_ID,
    group_name: str = GROUP_NAME,
    creation_date: datetime = datetime.now(),
) -> dict[str, Any]:
    date = creation_date.isoformat()

    return {
        "id": finding_id,
        "pk": f"FIN#{finding_id}",
        "sk": f"GROUP#{group_name}",
        "state": {
            "modified_by": "integratesmanager@gmail.com",
            "justification": "NO_JUSTIFICATION",
            "source": "ASM",
            "modified_date": date,
            "status": "CREATED",
        },
        "unreliable_indicators": {
            "open_vulnerabilities": 0,
            "closed_vulnerabilities": 0,
            "submitted_vulnerabilities": 0,
            "rejected_vulnerabilities": 0,
            "unreliable_status": "VULNERABLE",
            "oldest_vulnerability_report_date": date,
            "newest_vulnerability_report_date": date,
            "max_open_severity_score": Decimal("7.3"),
            "max_open_severity_score_v4": Decimal("6.9"),
            "max_open_epss": 0,
            "max_open_root_criticality": "LOW",
            "treatment_summary": {
                "untreated": 0,
                "in_progress": 0,
                "accepted": 0,
                "accepted_undefined": 0,
            },
            "verification_summary": {
                "requested": 0,
                "on_hold": 0,
                "verified": 0,
                "masked": 0,
            },
            "vulnerabilities_summary": {
                "closed": 0,
                "open": 0,
                "submitted": 0,
                "rejected": 0,
                "open_critical": 0,
                "open_high": 0,
                "open_low": 0,
                "open_medium": 0,
                "open_critical_v3": 0,
                "open_high_v3": 0,
                "open_low_v3": 0,
                "open_medium_v3": 0,
            },
            "total_open_cvssf": Decimal("0.0"),
            "total_open_cvssf_v4": Decimal("0.0"),
        },
        "group_name": group_name,
        "severity_score": fake_severity_score("low"),
        "description": "Test finding",
        "title": "999 - Test finding",
        "evidences": {},
        "recommendation": "",
        "requirements": "",
        "threat": "",
        "creation": {
            "modified_by": "integratesmanager@gmail.com",
            "justification": "NO_JUSTIFICATION",
            "source": "ASM",
            "modified_date": date,
            "status": "CREATED",
        },
        "sorts": "NO",
        "attack_vector_description": "",
        "min_time_to_remediate": 1,
        "verification": None,
        "unfulfilled_requirements": [],
    }


def fake_vulnerability(
    *,
    vuln_id: str,
    finding_id: str = FINDING_ID,
    group_name: str = GROUP_NAME,
    org_name: str = ORG_NAME,
    state: VulnerabilityStatusType = "VULNERABLE",
    treatment_status: TreatmentStatusType = "UNTREATED",
    severity_level: SeverityLevelType | None = "low",
    bug_tracking_system_url: str = "https://test.com",
    webhook_url: str = "https://test.com",
    creation_date: datetime = datetime.now(),
    reported_date: datetime = datetime.now(),
) -> dict[str, Any]:
    released = "true" if state in ["SAFE", "VULNERABLE"] else "false"
    begin_sk = (
        f"VULN#DELETED#false#RELEASED#{released}"
        f"#ZR#false#STATE#{state.lower()}"
    )

    return {
        "id": vuln_id,
        "finding_id": finding_id,
        "sk": f"FIN#{finding_id}",
        "pk": f"VULN#{vuln_id}",
        "pk_2": "ROOT",
        "pk_3": "USER",
        "pk_4": "EVENT",
        "pk_5": f"GROUP#{group_name}",
        "pk_6": f"FIN#{finding_id}",
        "sk_2": f"VULN#{vuln_id}",
        "sk_3": f"VULN#{vuln_id}",
        "sk_4": f"VULN#{vuln_id}",
        "sk_5": f"VULN#ZR#false#STATE#{state.lower()}#TREAT#false",
        "sk_6": f"{begin_sk}#VERIF#none",
        "pk_hash": "HASH",
        "sk_hash": "ROOT",
        "created_date": creation_date.isoformat(),
        "created_by": "hacker@fluidattacks.com",
        "hacker_email": "hacker@fluidattacks.com",
        "type": "PORTS",
        "state": {
            "modified_by": creation_date.isoformat(),
            "where": "---",
            "source": "ASM",
            "modified_date": creation_date.isoformat(),
            "specific": "9999",
            "status": state,
        },
        "treatment": {
            "modified_date": reported_date.isoformat(),
            "status": treatment_status,
        },
        "group_name": group_name,
        "organization_name": org_name,
        "unreliable_indicators": {
            "unreliable_reattack_cycles": 0,
            "unreliable_source": "ASM",
            "unreliable_efficacy": 0,
            "unreliable_report_date": reported_date.isoformat(),
            "unreliable_treatment_changes": 1,
        },
        "bug_tracking_system_url": bug_tracking_system_url,
        "webhook_url": webhook_url,
        **(
            {"severity_score": fake_severity_score(severity_level)}
            if severity_level
            else {}
        ),
    }


def initialize_db(db_resource: DynamoDBResource) -> None:
    """It adds:
    - integrates_vms table with Streams enabled.
    """
    db_resource.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {"AttributeName": "pk", "KeyType": "HASH"},
            {"AttributeName": "sk", "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "pk", "AttributeType": "S"},
            {"AttributeName": "sk", "AttributeType": "S"},
            {"AttributeName": "pk_2", "AttributeType": "S"},
            {"AttributeName": "sk_2", "AttributeType": "S"},
            {"AttributeName": "pk_5", "AttributeType": "S"},
            {"AttributeName": "sk_5", "AttributeType": "S"},
            {"AttributeName": "pk_6", "AttributeType": "S"},
            {"AttributeName": "sk_6", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
        GlobalSecondaryIndexes=[
            {
                "IndexName": "inverted_index",
                "KeySchema": [
                    {"AttributeName": "sk", "KeyType": "HASH"},
                    {"AttributeName": "pk", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "gsi_2",
                "KeySchema": [
                    {"AttributeName": "pk_2", "KeyType": "HASH"},
                    {"AttributeName": "sk_2", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "gsi_5",
                "KeySchema": [
                    {"AttributeName": "pk_5", "KeyType": "HASH"},
                    {"AttributeName": "sk_5", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
            {
                "IndexName": "gsi_6",
                "KeySchema": [
                    {"AttributeName": "pk_6", "KeyType": "HASH"},
                    {"AttributeName": "sk_6", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        StreamSpecification={
            "StreamEnabled": True,
            "StreamViewType": "NEW_AND_OLD_IMAGES",
        },
    )


def add_finding_data(table: DynamoDBTable) -> None:
    """It adds:
    - 1 finding (FINDING_ID, GROUP_NAME)
    - 4 vulnerabilities for the finding with:
        - 1 vuln: VULNERABLE and UNTREATED
        - 1 vuln: SAFE and UNTREATED
        - 1 vuln: SUBMITTED and UNTREATED
        - 1 vuln: REJECTED and UNTREATED

    Args:
        table (Table): Table to add the data.
    """
    table.put_item(
        Item=fake_finding(finding_id=FINDING_ID, group_name=GROUP_NAME),
    )

    vulns_tuples: list[
        tuple[
            str,
            VulnerabilityStatusType,
            TreatmentStatusType,
        ]
    ] = [
        ("559cb1d7-4b4f-4d30-be0e-648d42c1c0c5", "VULNERABLE", "UNTREATED"),
        ("d7f48d61-e27f-4b57-a1d0-ae1528d7d3f7", "SAFE", "UNTREATED"),
        ("0e5c09ba-f1fc-4115-9da8-2f740d63b374", "SUBMITTED", "UNTREATED"),
        ("e6accc56-d871-4334-92ea-7bf3b3e0e99e", "REJECTED", "UNTREATED"),
    ]

    for item in vulns_tuples:
        table.put_item(
            Item=fake_vulnerability(
                vuln_id=item[0],
                finding_id=FINDING_ID,
                group_name=GROUP_NAME,
                state=item[1],
                treatment_status=item[2],
            ),
        )


def get_streams_records() -> tuple:
    streams: DynamoStreamsClient = _boto3.client("dynamodbstreams")

    stream_arn = streams.list_streams(TableName=TABLE_NAME)["Streams"][0][
        "StreamArn"
    ]

    shard_id = streams.describe_stream(StreamArn=stream_arn)[
        "StreamDescription"
    ]["Shards"][0]["ShardId"]

    shard_iterator = streams.get_shard_iterator(
        StreamArn=stream_arn,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",
    )["ShardIterator"]

    records = streams.get_records(ShardIterator=shard_iterator)["Records"]

    return tuple(records)
