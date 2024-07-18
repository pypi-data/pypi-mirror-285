#!/bin/bash -eux

# when the version is known not to be in the archive as it was built in a private PPA then we should fallback to the latest version in the archive
ubuntu-package-download --package-architecture arm64 --package-name libseccomp2 --package-version 2.4.3-1ubuntu3.20.04.1 --fallback-series --fallback-version --series focal

# If fallback is used we need to ensure that the architecture is the same or _all
ubuntu-package-download --package-architecture arm64 --package-name libquadmath0 --package-version 10.5.0-1ubuntu1~20.04.1 --fallback-series --fallback-version --series focal
ubuntu-package-download --package-architecture arm64 --package-name libquadmath0 --package-version 10.3.0-1ubuntu1~20.04.1 --fallback-series --fallback-version --series focal

# ensure that the fallback version of some binary packages (for the same source package) is not different
ubuntu-package-download --package-architecture amd64 --package-name gcc-10-base --package-version 10.4.0-9ubuntu1~20.04.1 --fallback-series --fallback-version --series focal
ubuntu-package-download --package-architecture amd64 --package-name libgcc-s1 --package-version 10.4.0-9ubuntu1~20.04.1 --fallback-series --fallback-version --series focal

# ensure that the fallback version of some binary package is from the same Ubuntu series if it exists
ubuntu-package-download --package-architecture amd64 --package-name libstdc++6 --package-version 12.3.0-1ubuntu1~22.04.1 --fallback-series --fallback-version --series jammy

# ensure we fallback to a previous series if not found in the current series
ubuntu-package-download --package-architecture amd64 --package-name base-files --package-version 13ubuntu1 --fallback-series --series noble
