#!/usr/bin/env python3

import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


INDEX = Path(__file__).resolve().parents[2] / "index.yaml"
PREFIX = "https://github.com/apecloud/helm-charts/releases/download/"
RELEASE_LIMIT = 5000
RFC3339 = re.compile(
    r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})"
)


def fields(node):
    return {
        key.value: value
        for key, value in node.value
        if isinstance(key, ScalarNode)
    }


def index_entries(text):
    root = yaml.compose(text, Loader=yaml.SafeLoader)
    if not isinstance(root, MappingNode):
        raise ValueError("index root must be a mapping")

    entries = fields(root).get("entries")
    if not isinstance(entries, MappingNode):
        raise ValueError("index entries must be a mapping")
    return entries


def remove_ranges(text, ranges):
    lines = text.splitlines(keepends=True)
    for start, end in sorted(ranges, reverse=True):
        del lines[start:end]
    return "".join(lines)


def fetch_release_tags():
    result = subprocess.run(
        [
            "gh",
            "release",
            "list",
            "--repo",
            "apecloud/helm-charts",
            "--limit",
            str(RELEASE_LIMIT),
            "--json",
            "tagName",
            "--jq",
            ".[].tagName",
        ],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
    )
    tags = set(result.stdout.splitlines())
    if not tags:
        raise ValueError("gh release list returned no releases")
    if len(tags) >= RELEASE_LIMIT:
        raise ValueError(f"release count reached --limit {RELEASE_LIMIT}")
    return tags


def release_tag(url):
    if not url.startswith(PREFIX):
        return None
    tag, separator, _ = url[len(PREFIX) :].partition("/")
    if not separator or not tag:
        raise ValueError(f"invalid release URL: {url}")
    return tag


def remove_invalid_releases(text, release_tags):
    ranges = []
    removed = []
    scanned = 0
    for chart, versions in index_entries(text).value:
        if not isinstance(chart, ScalarNode) or not isinstance(versions, SequenceNode):
            raise ValueError("each chart must contain a version list")

        invalid = []
        for record in versions.value:
            if not isinstance(record, MappingNode):
                raise ValueError(f"{chart.value} contains a non-mapping entry")
            values = fields(record)
            urls = values.get("urls")
            if not isinstance(urls, SequenceNode) or not urls.value:
                raise ValueError(f"{chart.value} entry is missing urls")
            url_values = []
            for url in urls.value:
                if not isinstance(url, ScalarNode):
                    raise ValueError(f"{chart.value} contains a non-scalar URL")
                url_values.append(url.value)
            tags = [release_tag(url) for url in url_values]
            if all(tags) and not any(tag in release_tags for tag in tags):
                invalid.append(record)
                version = values.get("version")
                version = version.value if isinstance(version, ScalarNode) else "<unknown>"
                removed.append(f"{chart.value} {version}")
            scanned += 1

        if invalid and len(invalid) == len(versions.value):
            ranges.append((chart.start_mark.line, versions.end_mark.line))
        else:
            ranges.extend(
                (record.start_mark.line, record.end_mark.line) for record in invalid
            )

    return remove_ranges(text, ranges), removed, scanned


def created_key(value):
    match = RFC3339.fullmatch(value)
    if not match:
        raise ValueError(f"invalid created timestamp: {value}")

    offset = "+00:00" if match[3] == "Z" else match[3]
    second = datetime.fromisoformat(match[1] + offset).astimezone(timezone.utc)
    fraction = Decimal(f"0.{match[2]}") if match[2] else Decimal(0)
    return second, fraction


def deduplicate_index(text):
    ranges = []
    removed = []
    for chart, versions in index_entries(text).value:
        if not isinstance(chart, ScalarNode) or not isinstance(versions, SequenceNode):
            raise ValueError("each chart must contain a version list")

        records = []
        for position, record in enumerate(versions.value):
            if not isinstance(record, MappingNode):
                raise ValueError(f"{chart.value} contains a non-mapping entry")

            values = fields(record)
            version = values.get("version")
            created = values.get("created")
            if not isinstance(version, ScalarNode) or not isinstance(created, ScalarNode):
                raise ValueError(f"{chart.value} entry is missing version or created")
            records.append(
                (
                    version.value,
                    created_key(created.value),
                    position,
                    created.value,
                    record,
                )
            )

        winners = {}
        for record in records:
            version = record[0]
            if version not in winners or record[1:3] >= winners[version][1:3]:
                winners[version] = record

        for record in records:
            winner = winners[record[0]]
            if record is not winner:
                ranges.append((record[4].start_mark.line, record[4].end_mark.line))
                removed.append(
                    f"{chart.value} {record[0]} "
                    f"(removed created {record[3]}; kept created {winner[3]})"
                )

    return remove_ranges(text, ranges), removed


def clean_index_text(text, release_tags):
    cleaned, invalid, scanned = remove_invalid_releases(text, release_tags)
    cleaned, duplicates = deduplicate_index(cleaned)
    return cleaned, invalid, duplicates, scanned


def report_removed(invalid, duplicates):
    if invalid:
        print(f"Removed invalid releases ({len(invalid)}):")
        for entry in invalid:
            print(f"  {entry}")
    if duplicates:
        print(f"Removed duplicate entries ({len(duplicates)}):")
        for entry in duplicates:
            print(f"  {entry}")


def validate_index_text(text, release_tags):
    index = yaml.safe_load(text)
    entries = index.get("entries")
    if not isinstance(entries, dict):
        raise ValueError("index entries must be a mapping")

    seen = set()
    total = 0
    for chart, versions in entries.items():
        if not isinstance(versions, list):
            raise ValueError(f"{chart} versions must be a list")
        for record in versions:
            version = record.get("version")
            urls = record.get("urls")
            key = (chart, version)
            if key in seen:
                raise ValueError(f"duplicate chart version: {chart} {version}")
            if not isinstance(urls, list) or not urls:
                raise ValueError(f"{chart} {version} is missing urls")
            tags = [release_tag(url) for url in urls]
            if all(tags) and not any(tag in release_tags for tag in tags):
                raise ValueError(f"invalid release: {chart} {version}")
            seen.add(key)
            total += 1
    return total


def validate_helm(path):
    with tempfile.TemporaryDirectory() as directory:
        subprocess.run(
            ["helm", "repo", "index", directory, "--merge", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )


def main():
    release_tags = fetch_release_tags()
    with INDEX.open(encoding="utf-8", newline="") as file:
        original = file.read()
    print(f"Found {len(release_tags)} releases")
    cleaned, invalid, duplicates, scanned = clean_index_text(
        original, release_tags
    )
    remaining = validate_index_text(cleaned, release_tags)

    descriptor, temporary = tempfile.mkstemp(
        dir=INDEX.parent, prefix=f".{INDEX.name}."
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
            file.write(cleaned)
        os.chmod(temporary, INDEX.stat().st_mode)
        validate_helm(Path(temporary))
        if invalid or duplicates:
            os.replace(temporary, INDEX)
            temporary = None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

    report_removed(invalid, duplicates)
    print(
        f"Scanned {scanned} entries; removed {len(invalid)} invalid releases "
        f"and {len(duplicates)} duplicates; remaining {remaining}"
    )


if __name__ == "__main__":
    main()
