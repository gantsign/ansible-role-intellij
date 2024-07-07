#!/bin/bash

download_url='https://data.services.jetbrains.com/products/releases?latest=true&type=release'

query_utlimate_editions() {
    curl -s "$download_url&code=IIU" | jq -r '
(
  .IIU[] |
  .version as $version |
  .downloads.linux |
  [
    $version,
    "Ultimate",
    .checksumLink
  ]
) | @tsv'
}

query_community_editions() {
    curl -s "$download_url&code=IIC" | jq -r '
(
  .IIC[] |
  .version as $version |
  .downloads.linux |
  [
    $version,
    "Community",
    .checksumLink
  ]
) | @tsv'
}

query_versions() {
    (
        query_utlimate_editions
        query_community_editions
    ) | sort -V
}

query_checksums() {
    IFS=$'\t'
    while read -r -a columns; do
        local version="${columns[0]}"
        local edition="${columns[1]}"
        local checksum_url="${columns[2]}"

        # Fetch the checksum using curl
        local response
        response="$(curl -s "$checksum_url")"
        checksum="${response%% *}" # Extract the checksum part (everything before the first space)

        # Output the Version, Edition, and Checksum as a tab-separated value
        echo -e "${version}\t${edition}\t${checksum}"
    done
}

(
    echo 'Version   Edition SHA256'
    query_versions | query_checksums
) | column -t
