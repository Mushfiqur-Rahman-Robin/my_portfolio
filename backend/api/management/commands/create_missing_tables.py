from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Create missing database tables for visitor counts"

    def handle(self, *args, **options):
        # Check and create DailyVisitorCount table
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'api_dailyvisitorcount'
                );
            """
            )

            table_exists = cursor.fetchone()[0]

            if not table_exists:
                self.stdout.write("Creating api_dailyvisitorcount table...")

                # Use UUID type for id, as defined in your models.
                # Assuming gen_random_uuid() is available in your PostgreSQL (usually is).
                sql = """
                CREATE TABLE api_dailyvisitorcount (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    date DATE UNIQUE NOT NULL,
                    count INTEGER NOT NULL DEFAULT 1
                );
                """

                with transaction.atomic():
                    cursor.execute(sql)

                self.stdout.write(self.style.SUCCESS("Successfully created api_dailyvisitorcount table."))
            else:
                self.stdout.write("Table api_dailyvisitorcount already exists.")

        # Check and create TotalVisitorCount table (and ensure the single record)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'api_totalvisitorcount'
                );
            """
            )

            table_exists = cursor.fetchone()[0]

            if not table_exists:
                self.stdout.write("Creating api_totalvisitorcount table...")

                sql = """
                CREATE TABLE api_totalvisitorcount (
                    id UUID PRIMARY KEY,
                    count INTEGER NOT NULL DEFAULT 0,
                    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                );

                -- Insert the default record with the fixed UUID
                -- Use a string literal for the UUID as it's a fixed value.
                INSERT INTO api_totalvisitorcount (id, count, last_updated)
                VALUES ('1a2b3c4d-e5f6-7890-1234-567890abcdef', 0, NOW())
                ON CONFLICT (id) DO NOTHING;
                """

                with transaction.atomic():
                    cursor.execute(sql)

                self.stdout.write(self.style.SUCCESS("Successfully created api_totalvisitorcount table."))
            else:
                self.stdout.write("Table api_totalvisitorcount already exists.")
                # Ensure the single record exists even if table existed before
                cursor.execute(
                    """
                    INSERT INTO api_totalvisitorcount (id, count, last_updated)
                    VALUES ('1a2b3c4d-e5f6-7890-1234-567890abcdef', 0, NOW())
                    ON CONFLICT (id) DO NOTHING;
                """
                )
                self.stdout.write("Ensured default TotalVisitorCount record exists.")
