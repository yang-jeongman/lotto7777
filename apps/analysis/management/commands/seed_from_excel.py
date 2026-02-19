"""
lotto.xlsx → DB 적재 커맨드
Usage: python manage.py seed_from_excel [--file path/to/lotto.xlsx]
"""
from datetime import date

from django.core.management.base import BaseCommand

from apps.analysis.models import DrawResult


class Command(BaseCommand):
    help = 'Excel 파일(lotto.xlsx)에서 역대 로또 당첨 데이터를 DB에 적재합니다.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default=r'C:\Users\jmyang\Downloads\lotto.xlsx',
            help='lotto.xlsx 파일 경로',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터 삭제 후 적재',
        )

    def handle(self, *args, **options):
        try:
            import openpyxl
        except ImportError:
            self.stderr.write(self.style.ERROR('openpyxl이 설치되지 않았습니다: pip install openpyxl'))
            return

        file_path = options['file']

        if options['clear']:
            count = DrawResult.objects.count()
            DrawResult.objects.all().delete()
            self.stdout.write(f'기존 데이터 {count}건 삭제 완료')

        self.stdout.write(f'파일 로딩: {file_path}')
        wb = openpyxl.load_workbook(file_path, read_only=True)
        ws = wb.active

        rows = list(ws.iter_rows(min_row=2, values_only=True))
        self.stdout.write(f'총 {len(rows)}행 발견')

        created = 0
        updated = 0
        skipped = 0

        for row in rows:
            if not row or not row[0]:
                skipped += 1
                continue

            draw_no = int(row[0])
            numbers = [int(row[i]) for i in range(1, 7)]
            bonus = int(row[7])

            # 당첨금 파싱 (숫자 또는 문자열)
            first_prize = self._parse_amount(row[8]) if len(row) > 8 else 0
            first_winners = int(row[9]) if len(row) > 9 and row[9] else 0
            second_prize = self._parse_amount(row[10]) if len(row) > 10 else 0
            second_winners = int(row[11]) if len(row) > 11 and row[11] else 0

            # 추첨일 추정 (Excel에 날짜 없을 경우)
            # 1회: 2002-12-07, 매주 토요일
            draw_date = self._estimate_draw_date(draw_no)

            obj, is_created = DrawResult.objects.update_or_create(
                draw_no=draw_no,
                defaults={
                    'draw_date': draw_date,
                    'number_1': numbers[0],
                    'number_2': numbers[1],
                    'number_3': numbers[2],
                    'number_4': numbers[3],
                    'number_5': numbers[4],
                    'number_6': numbers[5],
                    'bonus_number': bonus,
                    'first_prize_amount': first_prize,
                    'first_prize_winners': first_winners,
                    'second_prize_amount': second_prize,
                    'second_prize_winners': second_winners,
                },
            )

            if is_created:
                created += 1
            else:
                updated += 1

        wb.close()
        self.stdout.write(self.style.SUCCESS(
            f'완료! 생성: {created}건, 업데이트: {updated}건, 건너뜀: {skipped}건'
        ))

    def _parse_amount(self, value):
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        # 문자열 쉼표 제거
        return int(str(value).replace(',', '').replace(' ', '') or '0')

    def _estimate_draw_date(self, draw_no):
        """회차 → 추첨일 추정 (1회: 2002-12-07)"""
        from datetime import timedelta
        first_draw = date(2002, 12, 7)
        return first_draw + timedelta(weeks=draw_no - 1)
