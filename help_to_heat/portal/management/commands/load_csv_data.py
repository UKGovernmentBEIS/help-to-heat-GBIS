from json import JSONDecoder

from django.core.management import BaseCommand
import csv

from help_to_heat.portal.models import Referral


class Command(BaseCommand):
    help = "Load database data from a csv file"

    def add_arguments(self, parser):
        parser.add_argument("-p", "--path", type=str, help="Path to CSV file to load")

    def handle(self, *args, **kwargs):
        Referral.objects.all().delete()
        path = kwargs["path"]
        decoder = JSONDecoder()

        with open(path, newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                row["supplier_id"] = "30bf85d2-27d3-454b-8f46-1146a5429902"
                print(row["data"])
                json_data = decoder.decode(row["data"])
                row["data"] = json_data
                Referral.objects.create(**row)
