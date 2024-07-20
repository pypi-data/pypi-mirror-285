#!/bin/bash

set -euxo pipefail

# Check that the arg is either "import" or "export"
if [[ "$1" != "import" && "$1" != "export" ]]; then
    echo "Usage: $0 <import|export>"
    exit 1
fi

cd -- "$( dirname -- "${BASH_SOURCE[0]}" )/../../.."

bazel run --run_under "cd $PWD; " @com_github_google_copybara//java/com/google/copybara --java_runtime_version=remotejdk_11 -- copybara/copy.bara.sky "jupyter-$1"
