# SPDX-FileCopyrightText: Peter Pentchev <roam@ringlet.net>
# SPDX-License-Identifier: BSD-2-Clause

{ pkgs ? import <nixpkgs> { }
, py-ver ? "11"
}:
let
  python-name = "python3${py-ver}";
  python = builtins.getAttr python-name pkgs;
in
pkgs.mkShell {
  buildInputs = [
    pkgs.gitMinimal
    pkgs.uv
    python
  ];
  shellHook = ''
    set -e
    if [ -z "$VETOX_CERT_FILE" ]; then
      VETOX_CERT_FILE='/etc/ssl/certs/ca-certificates.crt'
    fi
    env SSL_CERT_FILE="$VETOX_CERT_FILE" python3.${py-ver} src/vetox/__main__.py run-parallel --tox-uv --uv
    exit
  '';
}
