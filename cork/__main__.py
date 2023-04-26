import argparse
import json
import os
import shutil
from urllib import request
from platformdirs import user_config_dir, user_data_dir
from cork.roblox import RobloxSession

def main():
    parser = argparse.ArgumentParser(
        prog='Cork',
        description='A Roblox Wine Wrapper')
    parser.add_argument("mode", type=str, choices=[
                        "player", "studio", "wine", "install", "cleanup"])
    parser.add_argument("args", nargs='*')
    arguments = parser.parse_args()

    if not os.path.isdir(user_config_dir("cork")):
        os.makedirs(user_config_dir("cork"))
    if not os.path.isdir(user_data_dir("cork")):
        os.makedirs(user_data_dir("cork"))
    if not os.path.isdir(os.path.join(user_data_dir("cork"), "pfx")):
        os.makedirs(os.path.join(user_data_dir("cork"), "pfx"))

    settings = {
        "WineHome": "",
        "WineType": "wine",
        "Wine64": False,
        "Channel": "live",
        "Launcher": "",
        "RemoteFFlags": "",
        "FFlags": {},
        "Environment": {
            "WINEDLLOVERRIDES": "winemenubuilder.exe=d"
        },
        "StudioEnvironment": {
        }
    }

    if os.path.exists(os.path.join(user_config_dir("cork"), "settings.json")):
        with open(os.path.join(user_config_dir("cork"), "settings.json"), "r") as file:
            data = json.loads(file.read())
            settings = settings | data

    with open(os.path.join(user_config_dir("cork"), "settings.json"), "w") as file:
        file.write(json.dumps(settings, indent=4))

    session = RobloxSession(
        os.path.join(user_data_dir("cork"), "pfx"),
        wine_home=settings["WineHome"],
        environment=settings["Environment"],
        wine64=settings["Wine64"],
        wine_type=settings["WineType"])

    match arguments.mode:
        case "player":
            remote_fflags = {}
            if settings["RemoteFFlags"] != "":
                try:
                    fflag_request = request.urlopen(request.Request(settings["RemoteFFlags"], headers={"User-Agent": "Cork"}))
                    remote_fflags = json.loads(
                        fflag_request.read().decode('utf-8'))
                except:
                    pass

            session.fflags = remote_fflags | settings["FFlags"]
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_player(
                    arguments.args, launcher=settings["Launcher"], channel=settings["Channel"])
            else:
                session.execute_player(
                    ["--app"], launcher=settings["Launcher"], channel=settings["Channel"])

            session.shutdown_prefix()
        case "studio":
            session.environment = session.environment | settings["StudioEnvironment"]
            session.initialize_prefix()

            if len(arguments.args) > 0:
                session.execute_studio(
                    arguments.args, launcher=settings["Launcher"], channel=settings["Channel"])
            else:
                session.execute_studio(
                    ["-ide"], launcher=settings["Launcher"], channel=settings["Channel"])

            session.wait_prefix()
        case "wine":
            session.initialize_prefix()
            session.execute(arguments.args)
            session.shutdown_prefix()
        case "install":
            session.initialize_prefix()
            
            session.get_player()
            session.get_studio()
        case "cleanup":
            session.initialize_prefix()

            versions_directory = os.path.join(
                session.get_drive(), "Roblox", "Versions")

            for version in [f for f in os.listdir(versions_directory) if not os.path.isfile(os.path.join(versions_directory, f))]:
                print(f"Removing {version}...")
                shutil.rmtree(os.path.join(versions_directory, version))

if __name__ == "__main__":
    main()