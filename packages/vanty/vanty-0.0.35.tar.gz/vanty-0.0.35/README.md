# <img style="margin-right: 2px; margin-top: 10px" alt="logo" height="16" width="16" src="https://cdn.advantch.com/static/images/logo.png"> Vanty CLI - By Advantch

CLI for managing projects from advantch.com including:

- The Starter Kit

  - The Starter Kit is the fastest way to launch new SaaS & AI products.

  - Visit https://www.advantch.com/ for documentation and more information

- Advantch Cloud (beta)

  - Deploy caching databases and storage for your apps

- Vanty.ai (beta)

  -  Vanty.ai is Agent platform for businesses and professionals. Quickly spin up entire documentation site, manage content, research, customer support with agents.

## Installation

We recommend using poetry to install vanty:

```bash
poetry install vanty
```

## Usage

1. Verify your license:

   ```bash
   vanty auth verify <your-license-token> (closed alpha)
   ```

2. Download the project to the current directory:

   ```bash
   vanty project download --project <project-id> (closed alpha)
   ```

3. Get started:

   ```bash
   cd <project-name>
   vanty dev init
   ```

4. Run the project:

```bash
vanty dev start
```

### Template GEN

Zip the template file

```bash
cd ./scaffold/template/ && zip -rX app_template.zip app_template -x ".*" -x "__MACOSX"
```

Copy to bucket
```
rclone copy app_template.zip r2:advantch-prod/template/  --progress
```

## Docs

- [Advantch Docs](https://www.advantch.com/docs/)
- [Local CLI Docs](./docs/overview.md)

## Issues & Support:

Advantch users can report issues on the slack issue channel.

- https://www.advantch.com/support/

## Building for pypi

```bash
poetry build
poetry publish
```

## PRs and Contributions:

Please note that whilst this is open source, it is not intended to be a community project.

Advantch users can submit PRs for extensions etc that maybe helpful to the core project or other users.

Otherwise, please fork and use this as a base for your own projects.

2024 &centerdot; Advantch.
