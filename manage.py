import argparse
from app.controllers.check_environment_controller import CheckEnvironmentController
from app.main import app_run
from app.services.logging_service import Logger


def runserver():
    Logger.info('Training Platform serving...')
    # Check Enviroment
    CheckEnvironmentController.check_datasets_environment()

    while True:
        app_run()

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['runserver'], help='the command to run')
    opt = parser.parse_args()

    return opt

if __name__ == '__main__':
    opt = parse_opt()
    if opt.command == 'runserver':
        runserver()
