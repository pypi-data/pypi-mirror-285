"""
AWS Inspector Model
"""

import csv
import json
from typing import List, Optional, Tuple

from pydantic import BaseModel

from regscale.core.app.utils.app_utils import error_and_exit


class InspectorRecord(BaseModel):
    """
    AWS Inspector Record
    """

    aws_account_id: str
    severity: Optional[str] = None
    fix_available: Optional[str] = None
    finding_type: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    finding_arn: Optional[str] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    last_updated: Optional[str] = None
    resource_id: Optional[str] = None
    container_image_tags: Optional[str] = None
    region: Optional[str] = None
    platform: Optional[str] = None
    resource_tags: Optional[str] = None
    affected_packages: Optional[str] = None
    package_installed_version: Optional[str] = None
    fixed_in_version: Optional[str] = None
    package_remediation: Optional[str] = None
    file_path: Optional[str] = None
    network_paths: Optional[str] = None
    age_days: Optional[str] = None
    remediation: Optional[str] = None
    inspector_score: Optional[str] = None
    inspector_score_vector: Optional[str] = None
    status: Optional[str] = None
    vulnerability_id: Optional[str] = None
    vendor: Optional[str] = None
    vendor_severity: Optional[str] = None
    vendor_advisory: Optional[str] = None
    vendor_advisory_published: Optional[str] = None
    nvd_cvss3_score: Optional[str] = None
    nvd_cvss3_vector: Optional[str] = None
    nvd_cvss2_score: Optional[str] = None
    nvd_cvss2_vector: Optional[str] = None
    vendor_cvss3_score: Optional[str] = None
    vendor_cvss3_vector: Optional[str] = None
    vendor_cvss2_score: Optional[str] = None
    vendor_cvss2_vector: Optional[str] = None
    resource_type: Optional[str] = None
    ami: Optional[str] = None
    resource_public_ipv4: Optional[str] = None
    resource_private_ipv4: Optional[str] = None
    resource_ipv6: Optional[str] = None
    resource_vpc: Optional[str] = None
    port_range: Optional[str] = None
    epss_score: Optional[str] = None
    exploit_available: Optional[str] = None
    last_exploited_at: Optional[str] = None
    lambda_layers: Optional[str] = None
    lambda_package_type: Optional[str] = None
    lambda_last_updated_at: Optional[str] = None
    reference_urls: Optional[str] = None
    detector_name: Optional[str] = None
    package_manager: Optional[str] = None

    @classmethod
    def process_csv(cls, file_path: str) -> Tuple[dict, List["InspectorRecord"]]:
        """
        Process CSV file

        :param str file_path: File path
        :return: A header dict and a list of InspectorRecord objects
        :rtype: Tuple[dict, List["InspectorRecord"]]
        """

        with open(file=file_path, mode="r", encoding="utf-8") as f:
            res = []
            reader = csv.DictReader(f)
            header = reader.fieldnames
            header_mapping = {name: name.replace(" ", "_").replace("(", "").replace(")", "").lower() for name in header}
            for row in reader:
                new_row = {header_mapping[key]: value for key, value in row.items()}
                ins = InspectorRecord(**new_row)
                res.append(ins)
        return header, res

    @classmethod
    def process_json(cls, file_path: str) -> Tuple[dict, List["InspectorRecord"]]:
        """
        Process JSON file

        :param str file_path: File path
        :rtype: Tuple[dict, List["InspectorRecord"]]
        :return: An empty dict and a list of InspectorRecord objects
        """
        with open(file=file_path, mode="r", encoding="utf-8") as file_object:
            dat = json.load(file_object)
        if not dat.get("findings"):
            error_and_exit("No findings in JSON file, check the file format and try again.")

        return {}, [cls.create_inspector_record(finding) for finding in dat.get("findings", [])]

    @classmethod
    def create_inspector_record(cls, finding: dict) -> "InspectorRecord":
        """
        Create an InspectorRecord from a finding

        :param dict finding: The finding data
        :return: An InspectorRecord object
        :rtype: InspectorRecord
        """
        resource = cls.get_resource(finding)
        details = resource.get("details", {})
        vulnerabilities = finding.get("packageVulnerabilityDetails", {})
        platform_key = list(details.keys())[0] if details.keys() else None

        return InspectorRecord(
            aws_account_id=finding.get("awsAccountId", ""),
            description=finding.get("description"),
            exploit_available=finding.get("exploitAvailable"),
            finding_arn=finding.get("findingArn"),
            first_seen=finding.get("firstObservedAt"),
            fix_available=finding.get("fixAvailable"),
            last_seen=finding.get("lastObservedAt"),
            remediation=finding.get("remediation", {}).get("recommendation", {}).get("text", ""),
            severity=finding.get("severity"),
            status=finding.get("status"),
            title=finding.get("title"),
            resource_type=resource.get("type"),
            resource_id=resource.get("id"),
            region=resource.get("region"),
            last_updated=finding.get("updatedAt"),
            platform=resource.get("details", {}).get(platform_key, {}).get("platform", ""),
            resource_tags=" ,".join(resource.get("details", {}).get(platform_key, {}).get("imageTags", "")),
            affected_packages=cls.get_vulnerable_package_info(vulnerabilities, "name"),
            package_installed_version=cls.get_vulnerable_package_info(vulnerabilities, "version"),
            fixed_in_version=cls.get_vulnerable_package_info(vulnerabilities, "fixedInVersion"),
            package_remediation=cls.get_vulnerable_package_info(vulnerabilities, "remediation"),
            vulnerability_id=vulnerabilities.get("vulnerabilityId") if vulnerabilities else None,
            vendor=vulnerabilities.get("source") if vulnerabilities else None,
            vendor_severity=finding.get("severity"),
            vendor_advisory=vulnerabilities.get("sourceUrl") if vulnerabilities else None,
            vendor_advisory_published=vulnerabilities.get("vendorCreatedAt") if vulnerabilities else None,
            package_manager=cls.get_vulnerable_package_info(
                finding.get("packageVulnerabilityDetails", {}), "packageManager"
            ),
            file_path=cls.get_vulnerable_package_info(finding.get("packageVulnerabilityDetails", {}), "filePath"),
            reference_urls=finding.get("packageVulnerabilityDetails", {}).get("sourceUrl"),
        )

    @staticmethod
    def get_resource(finding: dict) -> dict:
        """
        Get the resource from a finding

        :param dict finding: The finding data
        :return: The resource data
        :rtype: dict
        """
        resources = finding.get("resources", [])
        resource = resources.pop() if resources else {}
        return resource

    @staticmethod
    def get_vulnerable_package_info(vulnerabilities: dict, key: str) -> Optional[str]:
        """
        Get information from a vulnerable package

        :param dict vulnerabilities: The vulnerabilities data
        :param str key: The key of the information to get
        :return: The information or None if not found
        :rtype: Optional[str]
        """
        vulnerable_packages = vulnerabilities.get("vulnerablePackages", [])
        return vulnerable_packages[0].get(key) if vulnerabilities and vulnerable_packages else None
