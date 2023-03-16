from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    """
    Create a superuser if none exist
    Example:
        manage.py createsuperuser_if_none_exists --user=admin --password=changeme
    """

    def add_arguments(self, parser):
        parser.add_argument("--user", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="www.fabioaugusto@hotmail.com")

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.exists():
            return

        username = options["user"]
        password = options["password"]
        email = options["email"]

        first = 'Fábio'
        last = 'Augusto Macedo dos Santos'
        RG = '4852497'
        CPF = '00522233295'
        telefone = '91985707819'

        User.objects.create_superuser(username=username, password=password, email=email, first_name=first,
                                      last_name=last, RG=RG, CPF=CPF, telefone=telefone)

        self.stdout.write(f'Local user "{username}" was created')
