# Nautobot Discovery Plugin
[Nautobot](https://github.com/nautobot/nautobot) plugin to automatically discover your network with [Slurp'it](https://slurpit.io).

## Compatibility

|    Nautobot Version    | Plugin Version |
|------------------------|----------------|
|    >= Nautobot 2.1.x   |    >= 0.8.0    |

## Installation

The App/Plugin is available as a Python package in [pypi](https://pypi.org/project/slurpit_nautobot/) and can be installed with pip  

```
pip install slurpit_nautobot
```
Enable the App in nautobot_config.py:
```
PLUGINS = ['slurpit_nautobot']
```

Run nautobot-server post_upgrade, This command will ensure that any necessary post-installation tasks are run.
```
nautobot-server post_upgrade
```

Restart the WSGI Service and add `slurpit_nautobot` to your requirements.txt
```
sudo systemctl restart nautobot nautobot-worker
```

See [Nautobot Documentation](https://docs.nautobot.com/projects/core/en/stable/user-guide/administration/installation/app-install) for details

## Getting started
On our [getting started page](https://slurpit.io/getting-started/) you can take an Online Course to understand how the plugin works, or play with the plugin in a simulated network in our Sandbox.