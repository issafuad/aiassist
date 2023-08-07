from processors.linkedin import upload as upload_linkedin
from processors.onenote import upload as upload_onenote
from app import LOGGER
import click


@click.command()
@click.option('--choice', prompt='Your choicxe', help='update to update')
def main(choice):
    if choice == 'update-linkedin':
        LOGGER.info('Uploading linkedin')
        upload_linkedin()
    elif choice == 'update-onenote':
        LOGGER.info('Uploading onenote')
        upload_onenote()

    else:
        print('Invalid argument. Please provide "choice1" or "choice2".')


if __name__ == '__main__':
    main()
