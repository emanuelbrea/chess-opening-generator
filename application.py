from opening_generator import create_app

application = create_app()


@application.route('/')
def health():
    return 'My chess repertoire'


if __name__ == "__main__":
    application.run()
