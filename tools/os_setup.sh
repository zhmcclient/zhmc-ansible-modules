#!/bin/bash
# Copyright 2017-2020 IBM Corp. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [[ "$OS" == "Windows_NT" ]]; then
  osname="Windows"
  distro_id=""
  platform="$osname"
elif [[ "$(uname -s | sed -e 's/-.*//g')" == "CYGWIN_NT" ]]; then
  osname="CygWin"
  distro_id=""
  platform="$osname"
elif [[ "$(uname -s)" == "Linux" ]]; then
  osname="Linux"
  if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    distro_id=$ID
  elif [[ -n $(command -v lsb_release) ]]; then
    distro_id=$(lsb_release -i -s)
  else
    echo "Error: Cannot determine Linux distro."
    exit  1
  fi
  platform="$osname ($distro_id)"
elif [[ "$(uname -s)" == "Darwin" ]]; then
  osname="OS-X"
  distro_id=""
  platform="$osname"
else
  echo "Error: Unsupported platform:"
  echo "  uname -a: $(uname -a)"
  echo "  uname -s: $(uname -s)"
  echo "  OS: $OS"
  exit  1
fi

echo "Installing OS-level prerequisite packages for ${platform}..."

if [[ -n $(command -v yum 2>/dev/null) ]]; then
  sudo yum makecache fast
  sudo yum -y install libffi-devel
elif [[ -n $(command -v apt-get 2>/dev/null) ]]; then
  sudo apt-get --quiet update
  sudo apt-get --yes install libffi-dev
elif [[ -n $(command -v choco 2>/dev/null) ]]; then
  echo "Nothing to install for platform $platform"
else
  echo "Warning: Unsupported installer (Platform: $platform)"
  exit  0
fi
