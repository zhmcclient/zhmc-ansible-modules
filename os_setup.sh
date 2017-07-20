#!/bin/bash

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
  elif [[ -n $(which lsb_release) ]]; then
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

if [[ -n $(which yum 2>/dev/null) ]]; then
  sudo yum makecache fast
  sudo yum -y install libffi-devel
elif [[ -n $(which apt-get 2>/dev/null) ]]; then
  sudo apt-get --quiet update
  sudo apt-get --yes install libffi-dev
elif [[ -n $(which choco 2>/dev/null) ]]; then
  echo "Nothing to install for platform $platform"
else
  echo "Warning: Unsupported installer (Platform: $platform)"
  exit  0
fi
