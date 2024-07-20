# -*- coding: utf-8 -*-
# :Project:   metapensiero.tool.tinject — Development shell
# :Created:   mer 29 giu 2022, 10:40:08
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2022, 2023 Lele Gaifax
#

{
  description = "metapensiero.tool.tinject";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    gitignore = {
      url = "github:hercules-ci/gitignore.nix";
      # Use the same nixpkgs
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, flake-utils, gitignore }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        inherit (builtins) fromTOML readFile;
        inherit (gitignore.lib) gitignoreFilterWith;

        pinfo = (fromTOML (readFile ./pyproject.toml)).project;

        getSource = name: path: pkgs.lib.cleanSourceWith {
          name = name;
          src = path;
          filter = gitignoreFilterWith { basePath = path; };
        };

        pkgs = import nixpkgs { inherit system; };

        pkg = pkgs.python3Packages.buildPythonPackage {
          pname = pinfo.name;
          version = pinfo.version;

          src = getSource "tinject" ./.;
          format = "pyproject";
          nativeBuildInputs = with pkgs.python3Packages; [
            build
            pdm-backend
          ];
          doCheck = false;
          propagatedBuildInputs = with pkgs.python3Packages; [
            jinja2
            jinja2-time
            questionary
            ruamel-yaml
          ];
        };
        app = pkgs.python3Packages.toPythonApplication pkg;

        pythonEnv = pkgs.python3.withPackages (ps: [pkg]);
      in {
        packages = {
          tinject = pkg;
        };

        apps = rec {
          tinject = {
            type = "app";
            program = "${app}/bin/tinject";
          };
          default = tinject;
        };

        devShells = {
          default = pkgs.mkShell {
            name = "Dev shell";

            packages = with pkgs; [
              bump2version
              just
              pythonEnv
              python3Packages.build
              twine
              yq-go
            ];

            shellHook = ''
               export PYTHONPATH="$(pwd)/src''${PYTHONPATH:+:}$PYTHONPATH"
             '';
          };
        };
      });
}
